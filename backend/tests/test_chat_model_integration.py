import asyncio
import tempfile
import unittest
from contextlib import chdir
from unittest.mock import patch

from routers.chat import ChatRequest, chat
from services import nlp
from services.cache import load_local_answers, refresh_answers_cache
from test_multilingual_chat import make_request
from utils.preprocess import clean_text


class SavedModelResponseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        nlp.load_models()
        cls.answers = load_local_answers()

    def test_local_answers_cover_every_saved_model_label_in_all_languages(self):
        for intent in nlp.label_encoder.classes_:
            with self.subTest(intent=intent):
                self.assertIn(intent, self.answers)
                for language in ("en", "tl", "bis"):
                    self.assertTrue(self.answers[intent]["answers"][language].strip())

    def test_endpoint_returns_exact_saved_model_prediction_and_answer(self):
        cases = (
            ("How do I get a birth certificate?", "en"),
            ("Paano kumuha ng birth certificate?", "tl"),
            ("Unsaon pagkuha og birth certificate?", "bis"),
            ("What are the requirements for business permit?", "en"),
            ("Ano ang requirements para sa business permit?", "tl"),
            ("Unsay kinahanglan para sa business permit?", "bis"),
            ("What are the requirements for MTOP?", "en"),
            ("Ano ang kailangan para sa MTOP?", "tl"),
            ("Unsay requirements sa MTOP?", "bis"),
        )
        with (
            patch("routers.chat.ANSWERS", self.answers),
            patch("routers.chat.summarize_text", side_effect=lambda answer: answer),
        ):
            for message, language in cases:
                with self.subTest(message=message):
                    expected_intent = nlp.predict_intent(clean_text(message))
                    response = asyncio.run(chat(ChatRequest(message=message), make_request()))
                    self.assertEqual(response["intent"], expected_intent)
                    self.assertEqual(response["language"], language)
                    self.assertEqual(response["reply"], self.answers[expected_intent]["answers"][language].strip())

    def test_all_menu_selections_use_real_model_labels(self):
        from routers.chat import FOLLOW_UP_QUERIES

        expected_intents = {
            "awaiting_business_permit_type": (
                "cmo_new_business_permit",
                "cmo_renew_business_permit",
                "cmo_retirement_of_business_permit",
                "cmo_transfer_of_ownership_change_location",
            ),
            "awaiting_mtop_type": (
                "cmo_motorized_tricycle_operators_permit_franchise_new",
                "cmo_franchise_renewal",
                "cmo_motorized_tricycle_operators_permit_annual_mayor_s_permit",
                "cmo_tricycle_dropping",
                "cmo_motorized_tricycle_operators_permit_substitution_of_unit",
                "cmo_mtop_transfer",
            ),
        }
        with (
            patch("routers.chat.ANSWERS", self.answers),
            patch("routers.chat.summarize_text", side_effect=lambda answer: answer),
        ):
            for context, choices in FOLLOW_UP_QUERIES.items():
                for number, (query, aliases) in enumerate(choices, 1):
                    for language in ("en", "tl", "bis"):
                        with self.subTest(context=context, number=number, language=language):
                            expected = expected_intents[context][number - 1]
                            response = asyncio.run(chat(
                                ChatRequest(message=str(number), context=context, context_language=language),
                                make_request(),
                            ))
                            self.assertEqual(response["intent"], expected)
                            self.assertEqual(response["reply"], self.answers[expected]["answers"][language].strip())
                            self.assertEqual(response["language"], language)

    def test_local_fallback_does_not_depend_on_working_directory(self):
        with tempfile.TemporaryDirectory() as directory, chdir(directory):
            self.assertEqual(load_local_answers(), self.answers)

    def test_network_failure_loads_csv_not_stale_json(self):
        with (
            patch("services.cache.supabase") as supabase,
            patch("services.cache.ANSWERS", {}) as answers,
        ):
            supabase.table.return_value.select.return_value.execute.side_effect = ConnectionError("offline test")
            refresh_answers_cache()
            self.assertEqual(set(answers), set(self.answers))


if __name__ == "__main__":
    unittest.main()
