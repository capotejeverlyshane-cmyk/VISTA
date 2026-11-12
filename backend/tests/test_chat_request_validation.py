import unittest

from pydantic import ValidationError

from routers.chat import ChatRequest


class ChatRequestValidationTests(unittest.TestCase):
    def test_accepts_question_at_character_limit(self):
        request = ChatRequest(message="a" * 499 + "😀")
        self.assertEqual(len(request.message), 500)

    def test_rejects_question_over_character_limit(self):
        with self.assertRaises(ValidationError):
            ChatRequest(message="a" * 501)


if __name__ == "__main__":
    unittest.main()
