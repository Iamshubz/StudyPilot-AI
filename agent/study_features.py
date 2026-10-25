"""agent/study_features.py - Feature implementations for StudyPilot AI.

Coordinates the LLM client, prompt templates, tool routing, and input validation
for Chat, Notes Summarization, Quiz Generation, and Study Planning.
"""

from datetime import date
import json
import math
import re
from typing import Any, Dict, List, Optional, Tuple

from agent.llm_client import GroqClientManager
from agent.prompts import (
    NOTES_SUMMARIZER_PROMPT,
    QUIZ_GENERATOR_PROMPT,
    STUDY_CHAT_SYSTEM_PROMPT,
    STUDY_PLANNER_PROMPT,
)
from agent.tools import calculate, detect_and_execute_arithmetic


def process_chat_message(
    user_message: str,
    conversation_history: List[Dict[str, str]],
    api_key: Optional[str] = None,
    model: Optional[str] = None,
) -> Dict[str, Any]:
    """Processes a user chat message:

    1. Validates input length and empty states.
    2. Checks for arithmetic expressions to invoke the local Calculator Tool.
    3. If conversational, sends context-limited messages to Groq API.
    """
    clean_msg = user_message.strip()
    if not clean_msg:
        return {
            "success": False,
            "response": "Please enter a valid study question or calculation.",
            "is_tool_call": False,
            "tool_data": None,
            "error": "Empty input",
        }

    if len(clean_msg) > 4000:
        return {
            "success": False,
            "response": "Input too long. Please limit your message to under 4,000 characters.",
            "is_tool_call": False,
            "tool_data": None,
            "error": "Input length exceeded",
        }

    # Step 2: Check for direct arithmetic tool invocation
    tool_result = detect_and_execute_arithmetic(clean_msg)
    if tool_result is not None:
        if tool_result["success"]:
            answer_text = (
                f"🧮 **[Tool Execution: Safe Arithmetic Calculator]**\n\n"
                f"**Expression**: `{tool_result['expression']}`\n\n"
                f"**Computed Result**: `{tool_result['result']}`\n\n"
                f"*Note: Computed deterministically using local AST arithmetic engine (Zero LLM tokens consumed).*"
            )
            return {
                "success": True,
                "response": answer_text,
                "is_tool_call": True,
                "tool_data": tool_result,
                "error": None,
            }
        else:
            answer_text = (
                f"🧮 **[Tool Execution: Safe Arithmetic Calculator]**\n\n"
                f"**Expression**: `{tool_result['expression']}`\n\n"
                f"⚠️ **Error**: {tool_result['error']}"
            )
            return {
                "success": True,
                "response": answer_text,
                "is_tool_call": True,
                "tool_data": tool_result,
                "error": tool_result["error"],
            }

    # Step 3: LLM Chat generation
    manager = GroqClientManager(api_key=api_key, model=model)
    if not manager.is_configured():
        return {
            "success": False,
            "response": (
                "⚠️ **Backend AI Service Unavailable**\n\n"
                "The AI assistant requires `GROQ_API_KEY` to be set in the server environment (e.g. `.env` file).\n\n"
                "💡 *Note: The local **Safe Arithmetic Calculator** is fully operational! Try calculating expressions like `2**10 * 8` or using the Calculator tab.*"
            ),
            "is_tool_call": False,
            "tool_data": None,
            "error": "Missing API Key in server environment",
        }

    # Prepare message payload with system prompt
    messages_payload: List[Dict[str, str]] = [
        {"role": "system", "content": STUDY_CHAT_SYSTEM_PROMPT}
    ]

    # Append recent conversation history
    for msg in conversation_history:
        messages_payload.append({"role": msg["role"], "content": msg["content"]})

    # Append current user message
    messages_payload.append({"role": "user", "content": clean_msg})

    llm_res = manager.chat_completion(messages_payload)
    if llm_res["success"]:
        return {
            "success": True,
            "response": llm_res["content"],
            "is_tool_call": False,
            "tool_data": None,
            "error": None,
            "usage": llm_res.get("usage"),
            "model": llm_res.get("model"),
        }
    else:
        return {
            "success": False,
            "response": (
                f"⚠️ **Study service unavailable**\n\n{llm_res['error']}\n\n"
                "Check `GROQ_MODEL` and `GROQ_API_KEY` in `.env`, then restart Streamlit."
            ),
            "is_tool_call": False,
            "tool_data": None,
            "error": llm_res["error"],
        }


def summarize_notes_feature(
    notes_text: str,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
) -> Dict[str, Any]:
    """Summarizes user-provided study notes into 4 distinct revision sections."""
    clean_notes = notes_text.strip()
    if not clean_notes:
        return {"success": False, "summary": None, "error": "Please paste or upload study notes."}

    if len(clean_notes) < 20:
        return {
            "success": False,
            "summary": None,
            "error": "Notes are too short (minimum 20 characters required for a meaningful summary).",
        }

    if len(clean_notes) > 20000:
        return {
            "success": False,
            "summary": None,
            "error": "Notes exceed the 20,000 character limit. Please summarize in smaller chapters.",
        }

    manager = GroqClientManager(api_key=api_key, model=model)
    if not manager.is_configured():
        return {
            "success": False,
            "summary": None,
            "error": "Backend AI service requires GROQ_API_KEY to be configured in server environment (.env).",
        }

    prompt = NOTES_SUMMARIZER_PROMPT.format(notes_text=clean_notes)
    messages = [
        {"role": "system", "content": "You are a professional educational summarizer."},
        {"role": "user", "content": prompt},
    ]

    res = manager.chat_completion(messages, temperature=0.3, max_tokens=3000)
    if res["success"]:
        return {"success": True, "summary": res["content"], "error": None, "model": res["model"]}
    return {"success": False, "summary": None, "error": res["error"]}


def extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    """Robustly extracts JSON from an LLM response even if surrounded by markdown fences."""
    text_clean = text.strip()

    # Try direct parse
    try:
        return json.loads(text_clean)
    except json.JSONDecodeError:
        pass

    # Try regex matching ```json ... ```
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text_clean, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # Try finding outer braces
    first_brace = text_clean.find("{")
    last_brace = text_clean.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        candidate = text_clean[first_brace : last_brace + 1]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

    return None


def generate_quiz_feature(
    topic: str,
    num_questions: int = 5,
    difficulty: str = "Medium",
    api_key: Optional[str] = None,
    model: Optional[str] = None,
) -> Dict[str, Any]:
    """Generates structured multiple-choice quiz questions on a given topic."""
    clean_topic = topic.strip()
    if not clean_topic:
        return {"success": False, "quiz_data": None, "error": "Please enter a subject or topic for the quiz."}

    if len(clean_topic) > 200:
        return {"success": False, "quiz_data": None, "error": "Topic name too long (maximum 200 characters)."}

    try:
        requested_questions = int(num_questions)
    except (TypeError, ValueError):
        return {
            "success": False,
            "quiz_data": None,
            "error": "Number of questions must be a whole number between 3 and 10.",
        }

    num_q = max(3, min(10, requested_questions))
    diff = difficulty if difficulty in ("Easy", "Medium", "Hard", "Mixed") else "Medium"

    manager = GroqClientManager(api_key=api_key, model=model)
    if not manager.is_configured():
        return {
            "success": False,
            "quiz_data": None,
            "error": "Backend AI service requires GROQ_API_KEY to be configured in server environment (.env).",
        }

    prompt = QUIZ_GENERATOR_PROMPT.format(topic=clean_topic, num_questions=num_q, difficulty=diff)
    messages = [
        {"role": "system", "content": "You are an automated academic quiz generator that responds strictly in valid JSON."},
        {"role": "user", "content": prompt},
    ]

    res = manager.chat_completion(messages, temperature=0.4, max_tokens=2500)
    if not res["success"]:
        return {"success": False, "quiz_data": None, "error": res["error"]}

    parsed_json = extract_json_from_text(res["content"])
    if not parsed_json or "questions" not in parsed_json or not isinstance(parsed_json["questions"], list):
        return {
            "success": False,
            "quiz_data": None,
            "raw_content": res["content"],
            "error": "The AI response could not be parsed into structured quiz format. Please try again.",
        }

    # Validate each question
    valid_questions = []
    for idx, q in enumerate(parsed_json["questions"]):
        q_text = q.get("question", f"Question {idx + 1}")
        options = q.get("options", {})
        correct = str(q.get("correct_answer", "A")).upper().strip()
        explanation = q.get("explanation", "No explanation provided.")

        # Ensure all 4 options exist
        if not all(k in options for k in ("A", "B", "C", "D")):
            continue

        valid_questions.append({
            "id": idx + 1,
            "question": q_text,
            "options": {k: str(options[k]) for k in ("A", "B", "C", "D")},
            "correct_answer": correct if correct in ("A", "B", "C", "D") else "A",
            "explanation": explanation,
        })

    if len(valid_questions) < 3:
        return {
            "success": False,
            "quiz_data": None,
            "error": "Could not extract a sufficient number of valid 4-option questions. Please retry.",
        }

    structured_quiz = {
        "topic": clean_topic,
        "difficulty": diff,
        "questions": valid_questions,
    }

    return {"success": True, "quiz_data": structured_quiz, "error": None}


def format_quiz_to_txt(quiz_data: Dict[str, Any]) -> str:
    """Formats structured quiz data into a printable/downloadable text document."""
    lines = [
        "=" * 70,
        f"STUDYPILOT AI - PRACTICE QUIZ: {quiz_data.get('topic', 'General').upper()}",
        f"Difficulty: {quiz_data.get('difficulty', 'Mixed')} | Total Questions: {len(quiz_data.get('questions', []))}",
        "=" * 70,
        "",
        "--- SECTION 1: QUESTIONS ---",
        "",
    ]

    for q in quiz_data.get("questions", []):
        lines.append(f"Q{q['id']}. {q['question']}")
        for opt_key in ("A", "B", "C", "D"):
            lines.append(f"   ({opt_key}) {q['options'].get(opt_key, '')}")
        lines.append("")

    lines.append("-" * 70)
    lines.append("--- SECTION 2: ANSWER KEY & EXPLANATIONS ---")
    lines.append("-" * 70)
    lines.append("")

    for q in quiz_data.get("questions", []):
        correct = q['correct_answer']
        ans_text = q['options'].get(correct, '')
        lines.append(f"Q{q['id']} Correct Answer: ({correct}) {ans_text}")
        lines.append(f"   Explanation: {q['explanation']}")
        lines.append("")

    lines.append("=" * 70)
    lines.append("Generated by StudyPilot AI Assistant | Maharashtra Institute of Technology")
    lines.append("=" * 70)
    return "\n".join(lines)


def generate_study_plan_feature(
    subjects: str,
    hours_per_day: float,
    start_date: date,
    exam_date: date,
    study_style: str = "Pomodoro Technique (25m study / 5m break)",
    api_key: Optional[str] = None,
    model: Optional[str] = None,
) -> Dict[str, Any]:
    """Generates a personalized day-wise study schedule with input validation."""
    clean_subjects = subjects.strip()
    if not clean_subjects:
        return {"success": False, "plan": None, "error": "Please enter at least one subject or topic."}

    if not math.isfinite(hours_per_day) or hours_per_day <= 0:
        return {
            "success": False,
            "plan": None,
            "error": "Available study hours per day must be a positive finite number.",
        }

    if exam_date < start_date:
        return {
            "success": False,
            "plan": None,
            "error": "Invalid date range: Exam date cannot be before the study start date.",
        }

    total_days = (exam_date - start_date).days + 1
    total_hours = round(total_days * hours_per_day, 1)

    manager = GroqClientManager(api_key=api_key, model=model)
    if not manager.is_configured():
        return {
            "success": False,
            "plan": None,
            "error": "Backend AI service requires GROQ_API_KEY to be configured in server environment (.env).",
        }

    prompt = STUDY_PLANNER_PROMPT.format(
        subjects=clean_subjects,
        hours_per_day=hours_per_day,
        start_date=start_date.strftime("%Y-%m-%d"),
        exam_date=exam_date.strftime("%Y-%m-%d"),
        total_days=total_days,
        total_hours=total_hours,
        study_style=study_style,
    )

    messages = [
        {"role": "system", "content": "You are an expert academic planner and curriculum strategist."},
        {"role": "user", "content": prompt},
    ]

    res = manager.chat_completion(messages, temperature=0.4, max_tokens=3000)
    if res["success"]:
        return {
            "success": True,
            "plan": res["content"],
            "total_days": total_days,
            "total_hours": total_hours,
            "error": None,
        }
    return {"success": False, "plan": None, "error": res["error"]}
