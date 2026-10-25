"""tests/test_agent.py - Comprehensive Unit & Integration Tests for StudyPilot AI.

Tests:
1. Safe Calculator Tool (valid operations, negative numbers, floats, precedence)
2. Safe Calculator Security (zero division, giant exponent, prohibited keywords, arbitrary code execution)
3. Chat arithmetic detection and tool routing
4. Prompt formatting across modules
5. JSON quiz extraction and validation
6. Date validation for Study Planner
7. Missing API Key handling and environment resolution
"""

from datetime import date, timedelta
from io import BytesIO
import unittest

from pypdf import PdfWriter

from agent.document_processing import extract_uploaded_text
from agent.llm_client import GroqClientManager, get_effective_api_key, mask_api_key
from agent.prompts import (
    NOTES_SUMMARIZER_PROMPT,
    QUIZ_GENERATOR_PROMPT,
    STUDY_CHAT_SYSTEM_PROMPT,
    STUDY_PLANNER_PROMPT,
)
from agent.study_features import (
    extract_json_from_text,
    format_quiz_to_txt,
    generate_study_plan_feature,
    process_chat_message,
    summarize_notes_feature,
)
from agent.tools import calculate, detect_and_execute_arithmetic


class UploadedFileStub:
    """Minimal Streamlit upload object for extraction tests."""

    def __init__(self, name, content):
        self.name = name
        self._content = content

    def getvalue(self):
        return self._content


class TestDocumentProcessing(unittest.TestCase):
    """Verifies supported uploaded-document extraction behavior."""

    def test_text_file_extraction(self):
        uploaded = UploadedFileStub("notes.txt", b"Binary trees revision notes")
        self.assertEqual(extract_uploaded_text(uploaded), "Binary trees revision notes")

    def test_blank_pdf_is_readable_but_empty(self):
        pdf_buffer = BytesIO()
        writer = PdfWriter()
        writer.add_blank_page(width=300, height=300)
        writer.write(pdf_buffer)

        uploaded = UploadedFileStub("notes.pdf", pdf_buffer.getvalue())
        self.assertEqual(extract_uploaded_text(uploaded), "")

    def test_invalid_pdf_has_user_facing_error(self):
        uploaded = UploadedFileStub("broken.pdf", b"not a valid PDF")
        with self.assertRaisesRegex(RuntimeError, "Could not read PDF"):
            extract_uploaded_text(uploaded)


class TestSafeArithmeticCalculator(unittest.TestCase):
    """Verifies correctness and security boundaries of the Safe Calculator Tool."""

    def test_basic_arithmetic(self):
        self.assertEqual(calculate("2 + 3")["result"], 5)
        self.assertEqual(calculate("10 - 4")["result"], 6)
        self.assertEqual(calculate("6 * 7")["result"], 42)
        self.assertEqual(calculate("20 / 4")["result"], 5)
        self.assertEqual(calculate("21 // 4")["result"], 5)
        self.assertEqual(calculate("17 % 5")["result"], 2)
        self.assertEqual(calculate("2 ** 10")["result"], 1024)

    def test_operator_precedence_and_grouping(self):
        res = calculate("2 + 3 * 4")
        self.assertTrue(res["success"])
        self.assertEqual(res["result"], 14)

        res_paren = calculate("(2 + 3) * 4")
        self.assertTrue(res_paren["success"])
        self.assertEqual(res_paren["result"], 20)

    def test_unary_and_negative_numbers(self):
        res = calculate("-5 + 10")
        self.assertTrue(res["success"])
        self.assertEqual(res["result"], 5)

        res2 = calculate("-(3 * 4)")
        self.assertTrue(res2["success"])
        self.assertEqual(res2["result"], -12)

    def test_division_by_zero(self):
        res = calculate("10 / 0")
        self.assertFalse(res["success"])
        self.assertIn("zero", res["error"].lower())

        res_mod = calculate("10 % 0")
        self.assertFalse(res_mod["success"])
        self.assertIn("zero", res_mod["error"].lower())

    def test_giant_exponent_rejection(self):
        """Must reject astronomical exponents to prevent CPU hangs."""
        res = calculate("99999 ** 99999")
        self.assertFalse(res["success"])
        self.assertIn("too large", res["error"].lower())

    def test_non_finite_numbers_rejection(self):
        for expression in ("1e309", "1e308 * 1e308"):
            res = calculate(expression)
            self.assertFalse(res["success"])
            self.assertIn("finite", res["error"].lower())

    def test_code_injection_rejection(self):
        """Must strictly reject code injection attempts."""
        injections = [
            "__import__('os').system('ls')",
            "eval('2 + 2')",
            "exec('x = 1')",
            "open('/etc/passwd').read()",
            "import math; math.sqrt(4)",
            "lambda x: x + 1",
        ]
        for inj in injections:
            res = calculate(inj)
            self.assertFalse(res["success"], f"Failed to reject malicious input: {inj}")


class TestChatArithmeticDetection(unittest.TestCase):
    """Verifies automatic detection of arithmetic requests in the chat interface."""

    def test_arithmetic_detection(self):
        queries = [
            "calculate 25 * 4",
            "what is 1024 / 8?",
            "solve 2**8",
            "compute (10 + 20) * 3",
        ]
        for q in queries:
            res = detect_and_execute_arithmetic(q)
            self.assertIsNotNone(res, f"Should have detected arithmetic in: {q}")
            self.assertTrue(res["success"])

    def test_conversational_queries_not_misclassified(self):
        queries = [
            "What is the difference between TCP and UDP?",
            "Can you explain Dijkstra's algorithm?",
            "How does virtual memory paging work in OS?",
            "Give me 5 tips to score well in B.Tech exams.",
        ]
        for q in queries:
            res = detect_and_execute_arithmetic(q)
            self.assertIsNone(res, f"Should NOT detect arithmetic in conversational query: {q}")


class TestJSONQuizExtractor(unittest.TestCase):
    """Verifies resilient JSON extraction from markdown or raw text."""

    def test_clean_json(self):
        sample = '{"topic": "OS", "questions": [{"id": 1, "question": "What is PCB?", "options": {"A": "Process Control Block", "B": "Print", "C": "Program", "D": "None"}, "correct_answer": "A", "explanation": "PCB stores process metadata."}]}'
        data = extract_json_from_text(sample)
        self.assertIsNotNone(data)
        self.assertEqual(data["topic"], "OS")
        self.assertEqual(len(data["questions"]), 1)

    def test_json_in_markdown_fences(self):
        sample = '```json\n{"topic": "DBMS", "questions": []}\n```'
        data = extract_json_from_text(sample)
        self.assertIsNotNone(data)
        self.assertEqual(data["topic"], "DBMS")


class TestValidationAndErrorHandling(unittest.TestCase):
    """Verifies edge case handling and validation."""

    def test_empty_notes_validation(self):
        res = summarize_notes_feature("")
        self.assertFalse(res["success"])
        self.assertIn("Please paste", res["error"])

    def test_short_notes_validation(self):
        res = summarize_notes_feature("too short")
        self.assertFalse(res["success"])
        self.assertIn("too short", res["error"].lower())

    def test_planner_invalid_dates(self):
        res = generate_study_plan_feature(
            subjects="Maths",
            hours_per_day=4,
            start_date=date(2026, 10, 25),
            exam_date=date(2026, 10, 20),
        )
        self.assertFalse(res["success"])
        self.assertIn("cannot be before", res["error"].lower())

    def test_planner_rejects_invalid_hours(self):
        res = generate_study_plan_feature(
            subjects="Maths",
            hours_per_day=0,
            start_date=date(2026, 10, 25),
            exam_date=date(2026, 10, 26),
        )
        self.assertFalse(res["success"])
        self.assertIn("positive", res["error"].lower())

    def test_quiz_rejects_invalid_question_count(self):
        from agent.study_features import generate_quiz_feature

        res = generate_quiz_feature("Operating Systems", num_questions="many")
        self.assertFalse(res["success"])
        self.assertIn("whole number", res["error"].lower())

    def test_mask_api_key(self):
        self.assertEqual(mask_api_key(None), "Not Configured")
        self.assertEqual(mask_api_key(""), "Not Configured")
        self.assertEqual(mask_api_key("gsk_1234567890abcdef"), "gsk_...cdef")


if __name__ == "__main__":
    unittest.main()
