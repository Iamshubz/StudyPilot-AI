# 🧪 StudyPilot AI — Test Cases and Verification Report

**Subject**: AI Agent Development (B.Tech CSE 2026–2027)  
**Institution**: Maharashtra Institute of Technology, Chhatrapati Sambhajinagar  
**Test Suite File**: `tests/test_agent.py`  
**Execution Command**: `python3 -m unittest tests/test_agent.py`  
**Overall Status**: ✅ **14 / 14 Unit Tests Passed (0.001s)**

---

## 1. Automated Test Matrix

| Test ID | Module / Component | Test Objective | Input Data | Expected Result | Actual Result | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| **TC-01** | Safe Calculator | Basic binary operations | `"2 + 3"`, `"10 - 4"`, `"6 * 7"`, `"20 / 4"` | Correct numeric results: `5`, `6`, `42`, `5` | Exactly matched expected arithmetic values | **PASS** |
| **TC-02** | Safe Calculator | Floor division and modulo | `"21 // 4"`, `"17 % 5"` | Returns integer division and remainder (`5`, `2`) | `5` and `2` returned | **PASS** |
| **TC-03** | Safe Calculator | Exponentiation within limits | `"2 ** 10"` | Returns `1024` | `1024` returned | **PASS** |
| **TC-04** | Safe Calculator | Operator precedence | `"2 + 3 * 4"`, `"(2 + 3) * 4"` | Respects BODMAS precedence: `14` and `20` | `14` and `20` returned | **PASS** |
| **TC-05** | Safe Calculator | Unary operators | `"-5 + 10"`, `"-(3 * 4)"` | Evaluates negative numbers correctly: `5` and `-12` | `5` and `-12` returned | **PASS** |
| **TC-06** | Safe Calculator | Zero division protection | `"10 / 0"`, `"10 % 0"` | Catches `ZeroDivisionError` gracefully without crash | Returns `"Division or modulo by zero is undefined."` | **PASS** |
| **TC-07** | AST Sandbox | CPU DoS prevention | `"99999 ** 99999"` | Rejects giant exponents exceeding safe power limit | Returns `"Exponentiation too large"` error | **PASS** |
| **TC-08** | AST Sandbox | Code injection rejection | `"__import__('os').system('ls')"` | Blocks prohibited keyword before parsing | Safely rejected with `"Contains prohibited keywords"` | **PASS** |
| **TC-09** | AST Sandbox | Arbitrary `eval()` rejection | `"eval('2 + 2')"` | Blocks `eval` keyword | Safely rejected with `"Contains prohibited keywords"` | **PASS** |
| **TC-10** | Chat Tool Routing | Arithmetic auto-detection | `"calculate 25 * 4"`, `"what is 1024 / 8?"` | Routes to local AST calculator instead of LLM | Structured tool response returned with exact math | **PASS** |
| **TC-11** | Chat Tool Routing | False-positive prevention | `"What is the difference between TCP and UDP?"` | Does NOT trigger arithmetic tool | Returns `None` (passes to conversational LLM) | **PASS** |
| **TC-12** | Quiz Generator | JSON schema parsing | Raw JSON and markdown-fenced ```json ... ``` | Cleanly extracts dictionary with question objects | Dictionary extracted with all question fields | **PASS** |
| **TC-13** | Notes Summarizer | Input length validation | Empty string `""` and short string `"too short"` | Rejects inputs < 20 characters with validation message | Returns appropriate user warning message | **PASS** |
| **TC-14** | Study Planner | Date consistency check | `start_date = 2026-10-25`, `exam_date = 2026-10-20` | Rejects exam date preceding start date | Returns `"Exam date cannot be before study start date"` | **PASS** |

---

## 2. Interactive Browser Manual Verifications

| Test ID | User Flow / Feature | Action Taken | Observed Behavior | Status |
| :--- | :--- | :--- | :--- | :---: |
| **MB-01** | AI Study Chat | Clicked preset chip `"🧮 Calculate: (2**10 * 8) / 1024"` | Assistant displayed tool badge: `⚡ Tool Executed Locally: Safe Arithmetic Calculator` and output `8`. | **PASS** |
| **MB-02** | Conversational Memory | Sent follow-up prompt, inspected memory counter in sidebar | Memory counter incremented to `2`, subsequent requests sent context window. | **PASS** |
| **MB-03** | Clear Memory Button | Clicked `"🗑️ Clear Chat History"` | Chat container reset, session history cleared, counter reset to `0`. | **PASS** |
| **MB-04** | Notes Summarizer | Clicked `"📋 Load Sample OS Notes"` | Text area populated with CPU Scheduling and Deadlock lecture notes. | **PASS** |
| **MB-05** | Notes Download | Clicked `"📥 Download Summary as TXT"` | Downloaded formatted text file `StudyPilot_Summary_YYYYMMDD.txt`. | **PASS** |
| **MB-06** | Quiz Mode | Clicked `"OSI 7-Layer Model"` chip, selected questions | Form populated with topic and questions slider configured between 3 and 10. | **PASS** |
| **MB-07** | Study Planner | Tested date inputs | Timeline calculator updated dynamically (`8 days | 32.0 total hours`). | **PASS** |
| **MB-08** | Safe Calculator Tab | Entered `(120 * 4) + (85 / 5)` and clicked Calculate | Green result card displayed: `Result: 497`. Added to Recent Calculations. | **PASS** |
| **MB-09** | Sandbox Button Tests | Clicked `"Test: __import__('os')"` and `"Test: Division by Zero"` | System displayed red/warning rejection alerts without crashing. | **PASS** |
| **MB-10** | Responsive Viewport | Tested in 1280x715 desktop and mobile viewports | Layout adapts fluidly, columns stack without clipping or horizontal overflow. | **PASS** |

---

## 3. Security Boundary Verification Summary

```
Security Test Input: __import__('os').system('rm -rf /')
Result: REJECTED (Forbidden keyword detected)

Security Test Input: eval('2+2')
Result: REJECTED (Forbidden keyword detected)

Security Test Input: 99999999999999999 ** 99999999999999999
Result: REJECTED (Exponent exceeds maximum safe limit of 1000)

Security Test Input: 100 / 0
Result: REJECTED (ZeroDivisionError caught gracefully)
```

No unhandled exceptions or secret exposures occurred during testing.
