import asyncio
import unittest
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.requests import Request

from routers.chat import ChatRequest, answer_for_intent, chat, router
from services.nlp import detect_supported_language, resolve_language


def make_request() -> Request:
    return Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/chat",
            "headers": [],
            "client": ("127.0.0.1", 12345),
        }
    )


class LanguageDetectionTests(unittest.TestCase):
    def test_detects_supported_languages(self):
        cases = {
            "What are the business permit requirements?": "en",
            "Ano ang kailangan para sa business permit?": "tl",
            "Unsay kinahanglan para sa business permit?": "bis",
        }
        for message, expected in cases.items():
            with self.subTest(message=message):
                self.assertEqual(detect_supported_language(message), expected)
                self.assertEqual(resolve_language("auto", message), expected)


class MultilingualChatTests(unittest.TestCase):
    def request_chat(self, **payload):
        return asyncio.run(chat(ChatRequest(**payload), make_request()))

    def test_auto_language_disambiguation_responses(self):
        cases = (
            ("business permit", "en", "I'd be happy"),
            ("business permit", "tl", "Tutulong ako"),
            ("business permit", "bis", "Motabang ko"),
        )
        for message, language, reply_fragment in cases:
            with self.subTest(language=language):
                response = self.request_chat(message=message, language=language)
                self.assertEqual(response["language"], language)
                self.assertIn(reply_fragment, response["reply"])

    def test_auto_language_is_preserved_during_numeric_follow_up(self):
        answers = {
            "cmo_new_business_permit": {
                "answers": {
                    "en": "English answer",
                    "tl": "Sagot sa Tagalog",
                    "bis": "Tubag sa Bisaya",
                }
            }
        }
        with (
            patch("routers.chat.ANSWERS", answers),
            patch("routers.chat.predict_intent", return_value="cmo_new_business_permit") as predict,
            patch("routers.chat.get_confidence", return_value=0.9),
        ):
            response = self.request_chat(
                message="1",
                language="auto",
                context="awaiting_business_permit_type",
                context_language="bis",
            )

        self.assertEqual(response["language"], "bis")
        self.assertEqual(response["reply"], "Tubag sa Bisaya")
        predict.assert_called_once_with("new business permit")

    def test_invalid_follow_ups_are_localized(self):
        cases = (
            ("awaiting_business_permit_type", "tl", "Hindi ko nakilala"),
            ("awaiting_mtop_type", "bis", "Wala nako mailhi"),
        )
        for context, language, reply_fragment in cases:
            with self.subTest(context=context, language=language):
                response = self.request_chat(
                    message="99",
                    language=language,
                    context=context,
                )
                self.assertEqual(response["language"], language)
                self.assertIn(reply_fragment, response["reply"])

    def test_missing_localized_answer_does_not_fall_back_to_english(self):
        answers = {
            "sample": {
                "answers": {
                    "en": "English answer",
                    "tl": "",
                    "bis": "Tubag sa Bisaya",
                }
            }
        }
        with patch("routers.chat.ANSWERS", answers):
            response = answer_for_intent(
                "sample", "tl", "Wala pang impormasyon para sa katanungang ito."
            )

        self.assertEqual(response, "Wala pang impormasyon para sa katanungang ito.")

    def test_complete_queries_use_model_and_original_language(self):
        cases = (
            ("What are the requirements for business permit?", "en"),
            ("Ano ang requirements para sa business permit?", "tl"),
            ("Unsay kinahanglan para sa MTOP?", "bis"),
            ("business permit requirements", "en"),
            ("Where can I renew my business permit?", "en"),
        )
        answers = {"sample": {"answers": {"en": "English", "tl": "Tagalog", "bis": "Bisaya"}}}
        from utils.preprocess import clean_text

        for message, language in cases:
            with (
                self.subTest(message=message),
                patch("routers.chat.ANSWERS", answers),
                patch("routers.chat.predict_intent", return_value="sample") as predict,
                patch("routers.chat.get_confidence", return_value=0.9),
            ):
                response = self.request_chat(message=message, language="auto")
                predict.assert_called_once_with(clean_text(message))
                self.assertEqual(response["intent"], "sample")
                self.assertEqual(response["language"], language)
                self.assertEqual(response["reply"], answers["sample"]["answers"][language])
                self.assertIsNone(response["context"])

    def test_missing_confidence_does_not_crash_or_reject_prediction(self):
        with (
            patch("routers.chat.ANSWERS", {"sample": {"answers": {"en": "Answer"}}}),
            patch("routers.chat.predict_intent", return_value="sample"),
            patch("routers.chat.get_confidence", return_value=None),
        ):
            response = self.request_chat(message="A complete question")
        self.assertEqual(response["reply"], "Answer")

    def test_threshold_and_missing_prediction(self):
        for intent, confidence, expected in (
            ("sample", 0.349, "unresolved"),
            ("sample", 0.35, "sample"),
            (None, None, "unresolved"),
        ):
            with (
                self.subTest(intent=intent, confidence=confidence),
                patch("routers.chat.ANSWERS", {"sample": {"answers": {"en": "Answer"}}}),
                patch("routers.chat.predict_intent", return_value=intent),
                patch("routers.chat.get_confidence", return_value=confidence),
            ):
                response = self.request_chat(message="A complete question")
                self.assertEqual(response["intent"], expected)
                self.assertEqual(
                    set(response), {"reply", "summary", "context", "intent", "language"}
                )

    def test_numbers_are_not_substring_matched(self):
        for message in ("0", "12", "123", "option 99"):
            with (
                self.subTest(message=message),
                patch("routers.chat.predict_intent") as predict,
            ):
                response = self.request_chat(
                    message=message, context="awaiting_business_permit_type",
                    context_language="tl",
                )
                predict.assert_not_called()
                self.assertEqual(response["context"], "awaiting_business_permit_type")
                self.assertEqual(response["language"], "tl")
                self.assertIn("Hindi ko nakilala", response["reply"])
                self.assertEqual(
                    set(response), {"reply", "summary", "context", "intent", "language"}
                )

    def test_new_topic_escapes_context_without_language_lock(self):
        with (
            patch("routers.chat.ANSWERS", {"birth_certificate": {"answers": {"tl": "Sagot"}}}),
            patch("routers.chat.predict_intent", return_value="birth_certificate") as predict,
            patch("routers.chat.get_confidence", return_value=0.9),
        ):
            response = self.request_chat(
                message="Paano kumuha ng birth certificate?",
                context="awaiting_business_permit_type", context_language="bis",
            )
        predict.assert_called_once_with("kumuha birth certificate")
        self.assertEqual(response["language"], "tl")
        self.assertEqual(response["reply"], "Sagot")
        self.assertIsNone(response["context"])

    def test_substrings_in_new_questions_do_not_select_menu_items(self):
        with (
            patch("routers.chat.ANSWERS", {"sample": {"answers": {"en": "Answer"}}}),
            patch("routers.chat.predict_intent", return_value="sample") as predict,
            patch("routers.chat.get_confidence", return_value=0.9),
        ):
            response = self.request_chat(
                message="Where is the newspaper office at 12 Main Street?",
                context="awaiting_business_permit_type",
            )
        predict.assert_called_once_with("newspaper office at 12 main street")
        self.assertEqual(response["intent"], "sample")
        self.assertIsNone(response["context"])

    def test_explicit_preference_overrides_previous_context_language(self):
        with (
            patch("routers.chat.ANSWERS", {"sample": {"answers": {"tl": "Sagot"}}}),
            patch("routers.chat.predict_intent", return_value="sample"),
            patch("routers.chat.get_confidence", return_value=0.9),
        ):
            response = self.request_chat(
                message="1", language="Filipino",
                context="awaiting_business_permit_type", context_language="bis",
            )
        self.assertEqual(response["language"], "tl")
        self.assertEqual(response["reply"], "Sagot")

    def test_non_english_answers_skip_english_summarizer(self):
        for language in ("tl", "bis"):
            with (
                self.subTest(language=language),
                patch("routers.chat.ANSWERS", {"sample": {"answers": {language: "Localized"}}}),
                patch("routers.chat.predict_intent", return_value="sample"),
                patch("routers.chat.get_confidence", return_value=0.9),
                patch("routers.chat.summarize_text") as summarize,
            ):
                response = self.request_chat(message="A question", language=language)
                summarize.assert_not_called()
                self.assertEqual(response["summary"], "Localized")

    def test_blank_translation_is_not_returned_as_resolved(self):
        with (
            patch("routers.chat.ANSWERS", {"sample": {"answers": {"en": "Answer", "tl": "  "}}}),
            patch("routers.chat.predict_intent", return_value="sample"),
            patch("routers.chat.get_confidence", return_value=0.9),
            patch("routers.chat.log_chat") as log,
        ):
            response = self.request_chat(message="A question", language="tl")
        self.assertIn("Wala pang impormasyon", response["reply"])
        self.assertFalse(log.call_args.args[3])


class ChatApiTests(unittest.TestCase):
    def setUp(self):
        app = FastAPI()
        app.include_router(router)
        self.client = TestClient(app)

    def test_rejects_empty_and_invalid_messages(self):
        for message in ("", "   ", "..."):
            with self.subTest(message=message):
                response = self.client.post("/chat", json={"message": message})
                self.assertEqual(response.status_code, 422)

    def test_rejects_unsupported_language(self):
        response = self.client.post("/chat", json={"message": "hello", "language": "invalid"})
        self.assertEqual(response.status_code, 422)

    def test_http_response_shape_and_context_language(self):
        response = self.client.post("/chat", json={
            "message": "12", "language": " AUTO ",
            "context": "awaiting_mtop_type", "context_language": "Bisaya",
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["language"], "bis")
        self.assertEqual(set(response.json()), {"reply", "summary", "context", "intent", "language"})


if __name__ == "__main__":
    unittest.main()
