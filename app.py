"""StudyPilot AI - Intelligent Study and Exam Preparation Assistant."""

from datetime import date, timedelta
import streamlit as st

from agent.study_features import (
    format_quiz_to_txt,
    generate_quiz_feature,
    generate_study_plan_feature,
    process_chat_message,
    summarize_notes_feature,
)
from agent.document_processing import SUPPORTED_UPLOAD_TYPES, extract_uploaded_text
from agent.tools import calculate

# ---------------------------------------------------------
# Page Configuration & Advanced Responsive Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="StudyPilot AI | Intelligent Academic Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Responsive Light-Theme First CSS
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    .stApp {
        background: #F5F8FE;
    }
    [data-testid="stAppViewContainer"] > .main {
        background: #F5F8FE;
    }
    .block-container {
        max-width: 1240px;
        padding: 0.75rem 1.5rem 2.5rem;
    }
    
    .main-header {
        background: transparent;
        padding: 1.5rem 0 1.2rem;
        border-radius: 0;
        color: white;
        margin-bottom: 0.25rem;
        box-shadow: none;
    }
    .main-header h1 {
        margin: 0;
        font-size: clamp(1.8rem, 3vw, 2.35rem);
        font-weight: 800;
        letter-spacing: -0.025em;
        color: #101A3A !important;
    }
    .main-header p {
        margin: 0.35rem 0 0;
        font-size: 0.98rem;
        color: #7080A3;
    }
    .main-header h1 span {
        color: #4168F2;
    }
    [data-testid="stSidebar"] {
        background: #FFFFFF;
        border-right: 1px solid #E4EAF5;
        width: 238px;
    }
    [data-testid="stSidebar"] > div:first-child {
        padding: 0.35rem 0.8rem 1rem;
    }
    [data-testid="stSidebarHeader"] {
        height: 0;
        padding: 0;
    }
    [data-testid="stSidebarCollapseButton"] {
        display: none;
    }
    .sidebar-brand-box {
        display: flex;
        align-items: center;
        gap: 0.65rem;
        padding: 0.75rem 0.35rem 1rem;
        border-bottom: 1px solid #E7ECF6;
        margin-bottom: 1rem;
    }
    .sidebar-brand-icon {
        display: grid;
        place-items: center;
        width: 2.2rem;
        height: 2.2rem;
        flex: 0 0 2.2rem;
        background: #EAF1FF;
        border-radius: 40px;
        font-size: 1.45rem;
    }
    .sidebar-brand-copy {
        min-width: 0;
    }
    .sidebar-brand-title {
        margin: 10px 0;
        font-size: 1.08rem;
        font-weight: 800;
        color: #182142;
        letter-spacing: -0.02em;
    }
    .sidebar-brand-subtitle {
        display: block;
        color: #7A88A8;
        font-size: 0.64rem;
        margin-top: 0.12rem;
        white-space: nowrap;
    }
    .sidebar-module-list {
        list-style: none;
        padding: 0;
        margin: 0.5rem 0;
    }
    .sidebar-module-item {
        display: flex;
        align-items: center;
        padding: 0.62rem 0.75rem;
        border-radius: 8px;
        font-size: 0.83rem;
        color: #4B587C;
        font-weight: 500;
        margin-bottom: 0.25rem;
        background: transparent;
        border: 1px solid transparent;
    }
    .sidebar-module-item:first-child {
        background: #E8F0FF;
        border-color: #DCE8FF;
        color: #2F63DB;
        font-weight: 700;
    }

    .feature-card {
        background: #FFFFFF;
        border: 1px solid #E3EAF6;
        border-radius: 14px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        box-shadow: 0 5px 18px rgba(49, 79, 145, 0.05);
    }
    .welcome-title {
        color: #101A3A;
        font-size: 2rem;
        font-weight: 800;
        letter-spacing: -0.04em;
        margin: 0;
    }
    .welcome-title span {
        color: #4168F2;
    }
    .welcome-subtitle {
        color: #7180A2;
        font-size: 0.92rem;
        margin: 0.25rem 0 1rem;
    }
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(5, minmax(0, 1fr));
        gap: 0.6rem;
        margin: 1rem 0 1.25rem;
    }
    .feature-tile {
        min-height: 112px;
        padding: 1rem 0.9rem;
        border: 1px solid transparent;
        border-radius: 12px;
        position: relative;
    }
    .feature-tile.blue { background: #EAF3FF; border-color: #DCEAFF; }
    .feature-tile.green { background: #ECFAF2; border-color: #D9F2E3; }
    .feature-tile.pink { background: #FFF0F4; border-color: #FFE0E8; }
    .feature-tile.yellow { background: #FFF9E9; border-color: #FDEFC8; }
    .feature-tile.purple { background: #F2EEFF; border-color: #E8DFFF; }
    .feature-icon {
        font-size: 1.15rem;
        margin-bottom: 0.35rem;
    }
    .feature-tile h4 {
        color: #182142;
        font-size: 0.8rem;
        margin: 0 0 0.25rem;
    }
    .feature-tile p {
        color: #7180A2;
        font-size: 0.7rem;
        line-height: 1.35;
        margin: 0;
    }

    div[data-testid="stTabs"] button {
        font-weight: 600;
        color: #647295;
        border-radius: 999px;
        padding: 0.45rem 0.75rem;
    }

    div[data-testid="stTabs"] [data-baseweb="tab-list"] {
        display: none;
    }

    div[data-testid="stTabs"] button[aria-selected="true"] {
        color: #2F63DB;
        background: #EAF1FF;
    }

    div[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
        display: none;
    }

    .chat-empty-state {
        color: #7180A2;
        background: #F8FAFF;
        border: 1px dashed #D8E3F6;
        border-radius: 10px;
        padding: 0.8rem 1rem;
        margin: 0.75rem 0;
        font-size: 0.84rem;
    }

    .chat-composer {
        background: #FFFFFF;
        border: 1px solid #DCE5F4;
        border-radius: 12px;
        padding: 0.45rem 0.6rem;
        margin-top: 0.8rem;
        box-shadow: 0 4px 14px rgba(49, 79, 145, 0.06);
    }

    .chat-composer input {
        border: 0 !important;
        box-shadow: none !important;
    }

    div[data-testid="stChatMessage"] {
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 0.75rem 1rem;
        margin-bottom: 0.65rem;
    }

    /* Tool Call Execution Badge */
    .tool-badge {
        display: inline-flex;
        align-items: center;
        background: #EFF6FF;
        border: 1px solid #BFDBFE;
        color: #1D4ED8;
        padding: 0.35rem 0.75rem;
        border-radius: 6px;
        font-size: 0.82rem;
        font-weight: 600;
        margin-bottom: 0.6rem;
    }

    .stButton>button {
        border-radius: 9px;
        font-weight: 500;
        border-color: #DDE6F6;
    }

    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 1.35rem;
        }
        .block-container {
            padding: 0.65rem 0.75rem 1.5rem;
        }
        .feature-grid {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }
        [data-testid="stSidebar"] {
            width: 220px;
        }
        [data-testid="stSidebar"] > div:first-child {
            padding: 0.35rem 0.65rem 0.8rem;
        }
        .sidebar-brand-title {
            font-size: 1rem;
        }
        .sidebar-brand-subtitle {
            font-size: 0.58rem;
        }
    }

    .app-footer {
        text-align: center;
        color: #64748B;
        font-size: 0.82rem;
        margin-top: 2.5rem;
        padding-top: 1.25rem;
        border-top: 1px solid #E2E8F0;
        line-height: 1.5;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = None

if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}

if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False

if "calc_history" not in st.session_state:
    st.session_state.calc_history = []

if "summary_result" not in st.session_state:
    st.session_state.summary_result = None

if "planner_result" not in st.session_state:
    st.session_state.planner_result = None

MODULES = {
    "chat": "💬 AI Study Chat",
    "notes": "📝 Notes Summarizer",
    "quiz": "🎯 AI Quiz Generator",
    "planner": "📅 Exam Study Planner",
    "calculator": "🧮 Safe Calculator Tool",
}

if "active_module" not in st.session_state:
    st.session_state.active_module = "chat"


# ---------------------------------------------------------
# Clean Student-Centric Sidebar
# ---------------------------------------------------------
with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand-box">
            <div class="sidebar-brand-icon">🎓</div>
            <div class="sidebar-brand-copy">
                <div class="sidebar-brand-title">StudyPilot AI</div>
                <span class="sidebar-brand-subtitle">Your personal study assistant</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("**Study workspace**")
    for module_key, module_label in MODULES.items():
        if st.button(
            module_label,
            key=f"sidebar_{module_key}",
            use_container_width=True,
            type="primary" if st.session_state.active_module == module_key else "secondary",
        ):
            st.session_state.active_module = module_key
            st.rerun()


# ---------------------------------------------------------
# Top Header Banner
# ---------------------------------------------------------
st.markdown(
    """
    <div class="main-header">
        <h1>Welcome to <span>StudyPilot AI</span></h1>
        <p>Your intelligent study companion for better learning, practice, and exam preparation.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

feature_columns = st.columns(5)
feature_styles = ("blue", "green", "pink", "yellow", "purple")
for column, (module_key, module_label), style in zip(
    feature_columns, MODULES.items(), feature_styles
):
    with column:
        if st.button(
            module_label,
            key=f"feature_{module_key}",
            use_container_width=True,
            type="primary" if st.session_state.active_module == module_key else "secondary",
        ):
            st.session_state.active_module = module_key
            st.rerun()
        st.caption(
            {
                "chat": "Ask questions and get clear explanations",
                "notes": "Convert notes into concise revision material",
                "quiz": "Generate practice questions with explanations",
                "planner": "Get a personalized study schedule",
                "calculator": "Solve arithmetic expressions safely",
            }[module_key]
        )


# ---------------------------------------------------------
# Main Functional Navigation Tabs
# ---------------------------------------------------------
ordered_module_keys = [
    st.session_state.active_module,
    *[key for key in MODULES if key != st.session_state.active_module],
]
workspace_tabs = st.tabs([MODULES[key] for key in ordered_module_keys])
workspace_by_key = dict(zip(ordered_module_keys, workspace_tabs))


# =========================================================
# TAB 1: AI STUDY CHAT (Module A, E, F)
# =========================================================
with workspace_by_key["chat"]:
    clear_chat_col, chat_hint_col = st.columns([1, 4])
    with clear_chat_col:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.toast("Chat history cleared.")
            st.rerun()
    with chat_hint_col:
        st.caption("Ask a question or enter an arithmetic expression.")

    # Display Conversation History
    chat_container = st.container()
    with chat_container:
        if not st.session_state.chat_history:
            st.markdown(
                '<div class="chat-empty-state">Your conversation will appear here.</div>',
                unsafe_allow_html=True,
            )
        else:
            for message in st.session_state.chat_history:
                with st.chat_message(message["role"]):
                    if message.get("is_tool_call"):
                        st.markdown('<div class="tool-badge">⚡ Tool Executed Locally: Safe Arithmetic Calculator</div>', unsafe_allow_html=True)
                    st.markdown(message["content"])

    # Handle incoming message
    with st.container():
        st.markdown('<div class="chat-composer">', unsafe_allow_html=True)
        with st.form("study_chat_form", clear_on_submit=True):
            input_col, send_col = st.columns([8, 1])
            with input_col:
                user_input = st.text_input(
                    "Your question",
                    placeholder="Ask an academic question or calculate 45 * 12...",
                    label_visibility="collapsed",
                    key="study_chat_input",
                )
            with send_col:
                send_message = st.form_submit_button("➤", type="primary", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Check if a preset button was clicked
    if "pending_chat_prompt" in st.session_state and st.session_state.pending_chat_prompt:
        user_input = st.session_state.pending_chat_prompt
        st.session_state.pending_chat_prompt = None

    if send_message and user_input.strip():
        # Display user message immediately
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Process message with tool routing & backend LLM
        with st.chat_message("assistant"):
            with st.spinner("StudyPilot AI is processing your request..."):
                result = process_chat_message(
                    user_message=user_input,
                    conversation_history=st.session_state.chat_history,
                )
                
                if result.get("is_tool_call"):
                    st.markdown('<div class="tool-badge">⚡ Tool Executed Locally: Safe Arithmetic Calculator</div>', unsafe_allow_html=True)
                
                st.markdown(result["response"])
        
        # Save to session history
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": result["response"],
            "is_tool_call": result.get("is_tool_call", False),
        })
        st.rerun()

    # Academic Disclaimer Footer
    st.markdown(
        "<p style='font-size:0.75rem; color:#94A3B8; text-align:center; margin-top:1.5rem;'>"
        "⚠️ <i>Academic Notice: StudyPilot AI generates educational explanations using LLMs and safe tools. "
        "Always cross-reference critical topics with your official university syllabus and prescribed textbooks before examinations.</i>"
        "</p>",
        unsafe_allow_html=True,
    )


# =========================================================
# TAB 2: NOTES SUMMARIZER (Module B)
# =========================================================
with workspace_by_key["notes"]:
    st.subheader("📝 Intelligent Study Notes Summarizer")
    st.caption("Paste your lecture notes or upload a TXT, PDF, or image file to generate a structured 4-part revision suite.")

    col_note_in, col_note_cfg = st.columns([2.5, 1])

    with col_note_cfg:
        st.markdown("#### ⚙️ Input Options")
        uploaded_file = st.file_uploader(
            "Upload notes or study material",
            type=SUPPORTED_UPLOAD_TYPES,
            help="Supported formats: TXT, MD, PDF, PNG, JPG, JPEG, and WEBP.",
            key="notes_upload",
        )
        
        # Sample notes loader for quick testing
        if st.button("📋 Load Sample OS Notes", use_container_width=True):
            st.session_state.sample_notes = (
                "Operating Systems - CPU Scheduling and Deadlocks\n\n"
                "CPU Scheduling is the process of deciding which process in the ready queue is allocated CPU time. "
                "The primary scheduling criteria are CPU utilization, Throughput, Turnaround Time, Waiting Time, and Response Time.\n\n"
                "Common algorithms include:\n"
                "1. First-Come, First-Served (FCFS): Non-preemptive, suffers from the Convoy Effect where short processes wait for long ones.\n"
                "2. Shortest Job First (SJF): Optimal waiting time. Can be preemptive (Shortest Remaining Time First - SRTF) or non-preemptive.\n"
                "3. Round Robin (RR): Designed for time-sharing systems. Each process gets a small unit of CPU time called a time quantum (typically 10-100 ms). If quantum is too large, it degrades to FCFS; if too small, context-switch overhead dominates.\n"
                "4. Priority Scheduling: Each process is assigned a priority. High priority gets CPU first. Starvation (indefinite blocking) is a major risk, solved via Aging.\n\n"
                "Deadlocks occur when a set of blocked processes each hold a resource and wait for another held by another process.\n"
                "Four Coffman conditions must hold simultaneously for a deadlock:\n"
                "1. Mutual Exclusion\n"
                "2. Hold and Wait\n"
                "3. No Preemption\n"
                "4. Circular Wait\n\n"
                "Deadlock handling strategies: Deadlock Prevention, Deadlock Avoidance (Banker's Algorithm), Deadlock Detection and Recovery, or Ostrich algorithm (ignore)."
            )
            st.toast("Sample OS notes loaded into input area.")

    with col_note_in:
        default_notes = ""
        if uploaded_file is not None:
            try:
                default_notes = extract_uploaded_text(uploaded_file)
                if default_notes:
                    st.success(f"Loaded file: {uploaded_file.name} ({len(default_notes)} characters)")
                else:
                    st.warning(
                        f"No readable text was found in {uploaded_file.name}. "
                        "For scanned PDFs, upload an image or paste the text manually."
                    )
            except (RuntimeError, UnicodeDecodeError, ValueError) as error:
                st.error(str(error))
        elif "sample_notes" in st.session_state:
            default_notes = st.session_state.sample_notes

        notes_input = st.text_area(
            "Paste Study Material / Notes Here:",
            value=default_notes,
            height=250,
            placeholder="Paste your lecture notes, definitions, algorithm steps, or syllabus topics here...",
            key="notes_input",
        )
        st.write(f"<small style='color:#64748B;'>Character Count: {len(notes_input)} / 20,000</small>", unsafe_allow_html=True)

    if st.button("🚀 Generate 4-Part Revision Suite", type="primary"):
        if not notes_input.strip():
            st.warning("Please provide or paste study notes first.")
        else:
            with st.spinner("Analyzing notes and structuring revision materials..."):
                sum_res = summarize_notes_feature(notes_input)
                if sum_res["success"]:
                    st.session_state.summary_result = sum_res["summary"]
                    st.success("Summary generated successfully!")
                else:
                    st.error(f"{sum_res['error']}")

    if st.session_state.summary_result:
        st.markdown("---")
        st.markdown("### 📋 Generated Revision Document")
        
        # Display formatted output
        st.markdown(st.session_state.summary_result)

        # Download Button
        txt_content = (
            "STUDYPILOT AI - GENERATED STUDY SUMMARY\n"
            f"Generated on: {date.today().strftime('%Y-%m-%d')}\n"
            + "=" * 70 + "\n\n"
            + st.session_state.summary_result
        )
        st.download_button(
            label="📥 Download Summary as TXT",
            data=txt_content,
            file_name=f"StudyPilot_Summary_{date.today().strftime('%Y%m%d')}.txt",
            mime="text/plain",
        )


# =========================================================
# TAB 3: AI QUIZ GENERATOR (Module C)
# =========================================================
with workspace_by_key["quiz"]:
    st.subheader("🎯 AI Practice Quiz Generator & Evaluator")
    st.caption("Generate custom multiple-choice quizzes with explanations and test your knowledge interactively.")

    col_q1, col_q2, col_q3 = st.columns([2, 1, 1])

    with col_q1:
        quiz_topic = st.text_input(
            "Quiz Subject or Topic",
            placeholder="e.g., Database Normalization, Computer Networks OSI Model, Binary Trees",
            key="quiz_topic",
        )
        
        # Suggestion chips
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1:
            if st.button("OSI 7-Layer Model", key="chip_osi", use_container_width=True):
                quiz_topic = "OSI 7-Layer Reference Model"
        with col_c2:
            if st.button("SQL & Normalization", key="chip_sql", use_container_width=True):
                quiz_topic = "Relational Database Normalization (1NF, 2NF, 3NF, BCNF)"
        with col_c3:
            if st.button("Graph Algorithms", key="chip_graph", use_container_width=True):
                quiz_topic = "Graph Algorithms: BFS, DFS, Dijkstra, Bellman-Ford"

    with col_q2:
        num_questions = st.slider(
            "Number of Questions",
            min_value=3,
            max_value=10,
            value=5,
            key="quiz_num_questions",
        )

    with col_q3:
        difficulty = st.selectbox(
            "Difficulty Level",
            ["Easy", "Medium", "Hard", "Mixed"],
            index=1,
            key="quiz_difficulty",
        )

    if st.button("🎯 Generate Practice Quiz", type="primary", use_container_width=True):
        if not quiz_topic.strip():
            st.warning("Please enter a subject or topic for the quiz.")
        else:
            with st.spinner("Formulating multiple-choice questions with answer key..."):
                q_res = generate_quiz_feature(
                    topic=quiz_topic,
                    num_questions=num_questions,
                    difficulty=difficulty,
                )
                if q_res["success"]:
                    st.session_state.quiz_data = q_res["quiz_data"]
                    st.session_state.quiz_answers = {}
                    st.session_state.quiz_submitted = False
                    st.success(f"Generated {len(q_res['quiz_data']['questions'])} questions on '{quiz_topic}'!")
                else:
                    st.error(f"{q_res['error']}")

    # Interactive Quiz Display & Scoring
    if st.session_state.quiz_data:
        q_data = st.session_state.quiz_data
        st.markdown("---")
        st.markdown(f"### 📝 Practice Quiz: **{q_data['topic']}** ({q_data['difficulty']} Level)")
        
        with st.form("interactive_quiz_form"):
            for q in q_data["questions"]:
                st.markdown(f"**Question {q['id']}:** {q['question']}")
                opts = [f"({k}) {q['options'][k]}" for k in ("A", "B", "C", "D")]
                
                selected_opt = st.radio(
                    f"Select Answer for Q{q['id']}:",
                    options=opts,
                    key=f"q_choice_{q['id']}",
                    index=None,
                    label_visibility="collapsed",
                )
                st.session_state.quiz_answers[q['id']] = selected_opt
                st.markdown("<br>", unsafe_allow_html=True)

            submit_quiz = st.form_submit_button("📊 Submit Answers & Check Score", type="primary")

        if submit_quiz:
            st.session_state.quiz_submitted = True

        if st.session_state.quiz_submitted:
            correct_count = 0
            total_count = len(q_data["questions"])

            st.markdown("### 🏆 Quiz Evaluation & Results")

            for q in q_data["questions"]:
                user_choice_full = st.session_state.quiz_answers.get(q['id'])
                # Extract chosen letter (A/B/C/D)
                user_letter = user_choice_full[1] if (user_choice_full and len(user_choice_full) > 1) else None
                is_correct = (user_letter == q["correct_answer"])

                if is_correct:
                    correct_count += 1
                    status_badge = "✅ **Correct!**"
                    border_color = "#22C55E"
                else:
                    status_badge = "❌ **Incorrect**"
                    border_color = "#EF4444"

                st.markdown(
                    f"""
                    <div style="border-left: 4px solid {border_color}; background: #F8FAFC; padding: 0.9rem 1.2rem; border-radius: 6px; margin-bottom: 0.8rem;">
                        <strong>Q{q['id']}. {q['question']}</strong><br>
                        {status_badge}<br>
                        <strong>Your Answer:</strong> {user_choice_full or 'Not answered'}<br>
                        <strong>Correct Answer:</strong> ({q['correct_answer']}) {q['options'].get(q['correct_answer'])}<br>
                        <small style="color: #475569;"><strong>Explanation:</strong> {q['explanation']}</small>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            percentage = round((correct_count / total_count) * 100, 1)
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                st.metric("Final Score", f"{correct_count} / {total_count}", f"{percentage}%")
            with col_m2:
                if percentage >= 80:
                    st.success("🌟 Outstanding preparation! You have mastered this topic.")
                elif percentage >= 50:
                    st.info("👍 Good effort! Review the explanations above to strengthen weak points.")
                else:
                    st.warning("📚 More revision needed. Use the Notes Summarizer to review core concepts.")

        # Download Quiz TXT Button
        quiz_txt = format_quiz_to_txt(q_data)
        st.download_button(
            label="📥 Download Quiz & Answer Key (TXT)",
            data=quiz_txt,
            file_name=f"StudyPilot_Quiz_{q_data['topic'].replace(' ', '_')}.txt",
            mime="text/plain",
        )


# =========================================================
# TAB 4: PERSONALIZED STUDY PLANNER (Module D)
# =========================================================
with workspace_by_key["planner"]:
    st.subheader("📅 Personalized Day-by-Day Study Schedule Generator")
    st.caption("Plan your preparation timeline realistically based on your exam date, daily available hours, and revision cycles.")

    col_pl1, col_pl2 = st.columns([1.8, 1.2])

    with col_pl1:
        plan_subjects = st.text_area(
            "Subjects / Topics to Cover:",
            value="1. Operating Systems (Process Scheduling, Deadlocks, Memory Management)\n2. Database Management Systems (SQL, Normalization, Transactions)\n3. Computer Networks (OSI Model, TCP/IP, Routing Protocols)",
            height=130,
            placeholder="Enter subjects and specific modules you must prepare...",
            key="planner_subjects",
        )
        
        study_style = st.selectbox(
            "Preferred Study Session Strategy",
            options=[
                "Pomodoro Technique (25m study / 5m break)",
                "Deep Focus Blocks (50m study / 10m break)",
                "90-Minute Ultradian Cycles (90m intensive / 20m rest)",
                "Spaced Repetition & Active Recall Heavy",
            ],
            index=0,
            key="planner_study_style",
        )

    with col_pl2:
        hours_per_day = st.slider(
            "Available Study Hours Per Day",
            min_value=1.0,
            max_value=12.0,
            value=4.0,
            step=0.5,
            key="planner_hours",
        )
        
        today = date.today()
        start_date = st.date_input(
            "Study Start Date",
            value=today,
            min_value=today - timedelta(days=1),
            key="planner_start_date",
        )
        exam_date = st.date_input(
            "Final Exam Date",
            value=today + timedelta(days=7),
            min_value=start_date,
            key="planner_exam_date",
        )

        days_diff = (exam_date - start_date).days + 1
        est_hours = round(days_diff * hours_per_day, 1)
        st.info(f"📊 **Timeline**: {days_diff} days | **Total Preparation Time**: ~{est_hours} hours")

    if st.button("🚀 Generate Personalized Study Schedule", type="primary"):
        if not plan_subjects.strip():
            st.warning("Please enter at least one subject or topic.")
        elif exam_date < start_date:
            st.error("Invalid dates: Exam date cannot be earlier than the start date.")
        else:
            with st.spinner("Synthesizing personalized timetable with revision and practice slots..."):
                plan_res = generate_study_plan_feature(
                    subjects=plan_subjects,
                    hours_per_day=hours_per_day,
                    start_date=start_date,
                    exam_date=exam_date,
                    study_style=study_style,
                )
                if plan_res["success"]:
                    st.session_state.planner_result = plan_res["plan"]
                    st.success("Study schedule generated successfully!")
                else:
                    st.error(f"{plan_res['error']}")

    if st.session_state.planner_result:
        st.markdown("---")
        st.markdown("### 📋 Your Tailored Study Schedule")
        st.markdown(st.session_state.planner_result)

        # Download Schedule Button
        schedule_txt = (
            "STUDYPILOT AI - PERSONALIZED EXAM PREPARATION SCHEDULE\n"
            f"Generated on: {date.today().strftime('%Y-%m-%d')}\n"
            f"Start Date: {start_date} | Exam Date: {exam_date} | Daily Hours: {hours_per_day}\n"
            + "=" * 70 + "\n\n"
            + st.session_state.planner_result
        )
        st.download_button(
            label="📥 Download Study Schedule (TXT)",
            data=schedule_txt,
            file_name=f"StudyPilot_Schedule_{date.today().strftime('%Y%m%d')}.txt",
            mime="text/plain",
        )


# =========================================================
# TAB 5: SAFE CALCULATOR TOOL (Module E)
# =========================================================
with workspace_by_key["calculator"]:
    st.subheader("🧮 Safe Arithmetic Calculator Tool")
    st.caption(
        "A verifiable, deterministic agent tool built on Python's Abstract Syntax Tree (AST). "
        "Strictly isolated from eval() or exec() with hard limits on exponentiation to prevent CPU denial of service."
    )

    col_calc_in, col_calc_info = st.columns([1.6, 1.2])

    with col_calc_in:
        calc_input = st.text_input(
            "Enter Arithmetic Expression:",
            placeholder="e.g., (1280 * 720) / (1024 * 1024) or 2**16 - 1",
            key="standalone_calc_input",
        )

        col_b1, col_b2, col_b3 = st.columns(3)
        with col_b1:
            if st.button("Sample: 2**16 - 1", use_container_width=True):
                calc_input = "2**16 - 1"
        with col_b2:
            if st.button("Sample: 450 * 18 / 1.5", use_container_width=True):
                calc_input = "450 * 18 / 1.5"
        with col_b3:
            if st.button("Sample: 1024 % 7", use_container_width=True):
                calc_input = "1024 % 7"

        if st.button("⚡ Calculate Expression", type="primary", use_container_width=True):
            if not calc_input.strip():
                st.warning("Please enter an arithmetic expression.")
            else:
                eval_res = calculate(calc_input)
                if eval_res["success"]:
                    st.success(f"**Expression**: `{eval_res['expression']}`  \n**Result**: `{eval_res['result']}`")
                    st.session_state.calc_history.append((eval_res["expression"], eval_res["result"]))
                else:
                    st.error(f"**Error**: {eval_res['error']}")

        # Security Demonstration Box
        with st.expander("🛡️ Security & Sandbox Verification Tests", expanded=True):
            st.markdown(
                """
                **Try submitting unsafe inputs below to verify that the agent safely rejects them:**
                """
            )
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                if st.button("Test: __import__('os')", use_container_width=True):
                    res = calculate("__import__('os').system('ls')")
                    st.warning(f"Rejection result: {res['error']}")
                if st.button("Test: eval('2+2')", use_container_width=True):
                    res = calculate("eval('2+2')")
                    st.warning(f"Rejection result: {res['error']}")
            with col_s2:
                if st.button("Test: Division by Zero (50 / 0)", use_container_width=True):
                    res = calculate("50 / 0")
                    st.warning(f"Rejection result: {res['error']}")
                if st.button("Test: Giant Exponent (99999**99999)", use_container_width=True):
                    res = calculate("99999**99999")
                    st.warning(f"Rejection result: {res['error']}")

    with col_calc_info:
        st.markdown("#### 🔬 Tool Architecture & Specs")
        st.markdown(
            """
            - **Engine**: Python `ast.parse(mode='eval')`
            - **Whitelisted Operators**:
              - Binary: `+`, `-`, `*`, `/`, `//`, `%`, `**`
              - Unary: `+`, `-`
            - **Hard Limits**:
              - Exponent power limit: `1,000`
              - Base magnitude limit: `1,000,000`
              - Result digit threshold: `100 digits`
            - **Forbidden Elements**:
              - Arbitrary method calls, imports, lambda functions, statements.
            """
        )

        if st.session_state.calc_history:
            st.markdown("#### 📜 Recent Calculations")
            for expr, val in reversed(st.session_state.calc_history[-5:]):
                st.code(f"{expr} = {val}", language="text")


# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------
st.markdown(
    """
    <div class="app-footer">
        <strong>StudyPilot AI</strong> — Your personal study assistant
    </div>
    """,
    unsafe_allow_html=True,
)
