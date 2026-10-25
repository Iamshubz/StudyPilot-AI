# 🎓 StudyPilot AI — Intelligent Study and Exam Preparation Assistant

**An AI Agent Development Mini-Project**  
**Department of Computer Science and Engineering**  
**Maharashtra Institute of Technology (Autonomous), Chhatrapati Sambhajinagar**  
*Affiliated to Dr. Babasaheb Ambedkar Marathwada University (Dr. BAMU)*  
*Academic Year: 2026–2027 | Practical Evaluation*

---

## 📌 Project Overview

**StudyPilot AI** is a multi-tool academic preparation assistant built with Python, Streamlit, and the official Groq API SDK. It is designed to assist undergraduate and engineering students with rapid revision, interactive quiz assessments, structured exam study schedules, concept explanations, and safe, deterministic arithmetic problem solving.

The project demonstrates core competencies in:
- **LLM Integration & Prompt Engineering**: High-speed inference using the current Groq model `openai/gpt-oss-20b`, with automatic fallback when a configured model is unavailable.
- **Tool-Augmented AI Agents**: Local deterministic tool invocation via Python's Abstract Syntax Tree (`ast`), executing without consuming LLM tokens.
- **Short-Term Conversational Memory**: Sliding-window context management in Streamlit session state.
- **Defensive Input Validation & Security**: Hard rejection of arbitrary code execution (`eval`/`exec`), CPU-bound denial of service attacks, and strict server-side credential isolation.
- **Responsive Light-Theme First UI**: Polished modern design optimized for laptops and mobile screens.

---

## 🏗️ System Architecture

```
Student User
     │
     ▼
Streamlit Responsive Web Interface (app.py)
     │
     ▼
Input Validation & Feature Routing
     │
     ├─────────────────────────────────┬───────────────────────────────┐
     │ [Conversational Queries]        │ [Arithmetic Requests]         │ [Study Workflows]
     ▼                                 ▼                               ▼
Context Manager                   AST Safe Calculator             Dedicated Modules
(Sliding Window History)          (Deterministic Python AST)      - Notes Summarizer (4-Part)
     │                                 │                          - Quiz Generator (Structured JSON)
     ▼                                 │                          - Exam Planner (Date-aware)
Groq Client Manager                    │                               │
(Secret & Fallback Handling)           │                               │
     │                                 │                               │
     ▼                                 │                               │
Groq API Inference                     │                               │
(`openai/gpt-oss-20b`)                 │                               │
     │                                 │                               │
     └─────────────────────────────────┴───────────────────────────────┘
                                       │
                                       ▼
                     Formatted Output & Interactive UI
                     (Markdown Cards, Interactive MCQs, TXT Exports)
```

---

## 🚀 Key Modules & Features

### 1. 💬 AI Study Chat (Modules A & F)
- Explains complex engineering and computer science concepts in clear, intuitive English.
- Supports definitions, real-world analogies, algorithm time complexities, and comparisons (e.g., Bellman-Ford vs Dijkstra, TCP vs UDP).
- **Conversational Memory**: Retains multi-turn dialogue context across follow-ups using a sliding window to prevent token overflow.
- **Tool Auto-Detection**: Arithmetic expressions like `calculate (2**10 * 8) / 1024` are automatically identified, routed to the safe local calculator tool, and badged distinctly with zero LLM tokens consumed.

### 2. 📝 Notes Summarizer (Module B)
- Accepts pasted lecture notes or uploaded `.txt`, `.md`, `.pdf`, `.png`, `.jpg`, `.jpeg`, and `.webp` files.
- Extracts text from PDFs locally; image uploads use local Tesseract OCR.
- Generates a **4-part revision suite**:
  1. *Quick Revision Notes* (high-level synthesis)
  2. *Detailed Structured Breakdown*
  3. *Key Definitions & Formulas*
  4. *Exam-Focused High-Yield Bullet Points*
- Downloadable directly as a `.txt` document.

### 3. 🎯 AI Quiz Generator (Module C)
- Generates 3 to 10 multiple-choice questions on any subject or topic.
- Four difficulty tiers: **Easy**, **Medium**, **Hard**, and **Mixed**.
- **Interactive Exam Mode**: Students choose answers directly in the UI, submit, and receive an instant score with explanations and color-coded answer badges.
- Downloadable complete quiz with answer key as a `.txt` file.

### 4. 📅 Personalized Study Planner (Module D)
- Inputs: Syllabus list, daily study hours, start date, and target exam date.
- Input validation: Guarantees exam date cannot precede start date; computes total hours and available days.
- Tailors schedules to strategies: **Pomodoro (25/5)**, **Deep Focus (50/10)**, or **Active Recall Spaced Repetition**.
- Includes revision checkpoints and a 24-hour pre-exam protocol.
- Downloadable study schedule as a `.txt` file.

### 5. 🧮 Safe Arithmetic Calculator Tool (Module E)
- Built on Python's `ast.parse(mode='eval')`—**strictly never uses unrestricted `eval()` or `exec()`**.
- Whitelisted operators: `+`, `-`, `*`, `/`, `//`, `%`, `**` (binary) and `+`, `-` (unary).
- **Security Guardrails**:
  - Exponentiation capped to power $\le 1000$ and base $\le 1,000,000$ to prevent CPU freeze attacks.
  - Zero-division detection (`ZeroDivisionError`).
  - Prohibits imports, method calls, semicolons, and code execution.
- Includes a dedicated interactive sandbox verification suite.

---

## 📂 Project Structure

```
StudyPilot_AI/
├── app.py                      # Main Streamlit web application
├── requirements.txt            # Python dependencies
├── .env.example                # Configuration template (keys kept safe)
├── .gitignore                  # Prevents committing secrets & venv
├── README.md                   # Complete documentation
├── test_cases.md               # Test matrix and verification results
├── deployment_guide.md         # Streamlit Community Cloud deployment guide
├── agent/
│   ├── __init__.py             # Agent package init
│   ├── document_processing.py  # PDF and image upload text extraction
│   ├── llm_client.py           # Groq API client with backend resolution & fallback
│   ├── prompts.py              # Tuned educational system & task prompts
│   ├── study_features.py       # Core logic for Chat, Notes, Quiz & Planner
│   └── tools.py                # AST-based Safe Arithmetic Calculator
├── tests/
│   └── test_agent.py           # Automated unit test suite (14 passing tests)
└── .streamlit/
    └── config.toml             # Light theme & server configuration
```

---

## 🛠️ Setup & Local Installation

### Prerequisites
- Python 3.9, 3.10, or 3.11
- A free Groq Cloud API key from [https://console.groq.com/keys](https://console.groq.com/keys)

### Step 1: Clone or Navigate to the Workspace
```bash
cd /path/to/StudyPilot_AI
```

### Step 2: Create and Activate Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate    # On macOS/Linux
# or
venv\Scripts\activate       # On Windows
```

### Step 3: Install Required Dependencies
```bash
pip install -r requirements.txt
```

For image uploads on macOS, install the local OCR engine once:
```bash
brew install tesseract
```

### Step 4: Configure Backend Environment Variables
Create a `.env` file in the project root:
```bash
cp .env.example .env
```
Edit `.env` and add your Groq API key:
```env
GROQ_API_KEY="gsk_your_actual_groq_api_key_here"
GROQ_MODEL="openai/gpt-oss-20b"
```

### Step 5: Run the Automated Test Suite
```bash
python3 -m unittest tests/test_agent.py
```
*(All 14 unit and security tests should pass)*

### Step 6: Launch the Streamlit Web Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

If the app was already running before changing `.env`, stop the old Streamlit process
and start it again so the current API configuration is loaded:

```bash
# Stop the existing Streamlit process with Ctrl+C in its terminal first.
streamlit run app.py --server.port 8501
```

The AI chat and other Groq-powered features require a valid `GROQ_API_KEY`. The
Safe Calculator continues to work without an API key.

---

## 🔒 Security Best Practices

1. **No Keys in UI or Git**: Credentials are read exclusively from backend `.env` variables or platform secrets.
2. **Strict Code Sandbox**: Mathematical operations use AST node whitelisting; malicious strings like `__import__('os').system('ls')` or `eval('2+2')` are blocked before parsing.
3. **DoS Prevention**: Exponential computations like `99999**99999` are rejected to prevent CPU starvation.
4. **Input Length Limits**: Chat messages are capped at 4,000 characters; notes at 20,000 characters.

---


