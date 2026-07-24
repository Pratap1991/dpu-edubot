"""
DPU EduBot — Main Streamlit Application
Roles: Student | Admin | Faculty

Student chat: UNCHANGED
Layer 0 ERP redirect: UNCHANGED — DO NOT MODIFY
Admin: Enhanced with premium enterprise dashboard (Prompt 2 — UI only)
"""

import streamlit as st
import os
import json
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

from dotenv import load_dotenv
load_dotenv()

st.set_page_config(page_title="DPU EduBot", page_icon="🎓", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
[data-testid="stSidebar"]{background:#0a1628!important;border-right:1px solid rgba(255,255,255,0.06)}
[data-testid="stSidebar"] *{color:#c8d4e8!important}
[data-testid="stSidebar"] .stRadio label{color:#c8d4e8!important}
.source-chip{display:inline-block;background:#e6f1fb;color:#185FA5;font-size:11px;padding:2px 8px;border-radius:20px;margin:2px}
.adm-card{background:#0f1f38;border:1px solid rgba(255,255,255,0.07);border-radius:12px;padding:18px 20px;margin-bottom:14px}
.adm-card-title{font-size:13px;font-weight:600;color:#e2e8f4;margin-bottom:14px}
.adm-metric{background:#0f1f38;border:1px solid rgba(255,255,255,0.07);border-radius:10px;padding:14px 16px}
.adm-metric-val{font-size:28px;font-weight:700;color:#ffffff;line-height:1.1}
.adm-metric-lbl{font-size:12px;color:#7a8fa8;margin-top:4px}
.adm-metric-sub{font-size:11px;margin-top:4px}
.sub-green{color:#4ade80}.sub-red{color:#f87171}.sub-amber{color:#fbbf24}.sub-blue{color:#60a5fa}
.tkt-row{background:#0f1f38;border:1px solid rgba(255,255,255,0.06);border-radius:10px;padding:13px 16px;margin-bottom:8px;display:flex;align-items:flex-start;gap:12px}
.tkt-id{font-family:monospace;font-size:11px;color:#4a6fa8;background:rgba(24,95,165,0.15);padding:2px 7px;border-radius:6px;flex-shrink:0;margin-top:2px}
.tkt-q{font-size:13px;color:#dde4f0;line-height:1.5;flex:1}
.tkt-meta{font-size:11px;color:#5a7a9a;margin-top:4px}
.tkt-dept{font-size:11px;color:#60a5fa;margin-top:2px;font-style:italic}
.pri-high{background:rgba(248,113,113,0.15);color:#f87171;font-size:11px;font-weight:600;padding:3px 10px;border-radius:20px;border:1px solid rgba(248,113,113,0.3)}
.pri-medium{background:rgba(251,191,36,0.12);color:#fbbf24;font-size:11px;font-weight:600;padding:3px 10px;border-radius:20px;border:1px solid rgba(251,191,36,0.25)}
.pri-low{background:rgba(74,222,128,0.12);color:#4ade80;font-size:11px;font-weight:600;padding:3px 10px;border-radius:20px;border:1px solid rgba(74,222,128,0.25)}
.status-open{background:rgba(248,113,113,0.1);color:#f87171;font-size:10px;font-weight:600;padding:2px 8px;border-radius:20px}
.status-progress{background:rgba(251,191,36,0.1);color:#fbbf24;font-size:10px;font-weight:600;padding:2px 8px;border-radius:20px}
.status-resolved{background:rgba(74,222,128,0.1);color:#4ade80;font-size:10px;font-weight:600;padding:2px 8px;border-radius:20px}
.sla-wrap{margin-bottom:16px}
.sla-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:6px}
.sla-title{font-size:13px;color:#dde4f0}
.sla-bar-bg{background:rgba(255,255,255,0.08);border-radius:6px;height:8px;overflow:hidden}
.sla-bar-fill{height:100%;border-radius:6px}
.sla-green{background:#10b981}.sla-amber{background:#f59e0b}.sla-red{background:#ef4444}
.sla-meta{font-size:11px;color:#5a7a9a;margin-top:5px}
.cat-chip{display:inline-block;font-size:10px;font-weight:600;padding:2px 8px;border-radius:20px;margin-right:4px}
.cat-accounts{background:rgba(239,68,68,0.15);color:#f87171}
.cat-academic{background:rgba(96,165,250,0.15);color:#60a5fa}
.cat-exam{background:rgba(251,191,36,0.15);color:#fbbf24}
.cat-students{background:rgba(74,222,128,0.15);color:#4ade80}
.cat-dispatch{background:rgba(167,139,250,0.15);color:#a78bfa}
.email-box{background:#0a1628;border:1px solid rgba(255,255,255,0.08);border-radius:10px;padding:16px;font-size:13px;color:#c8d4e8;line-height:1.8;white-space:pre-wrap}
.faq-item{background:#0f1f38;border:1px solid rgba(255,255,255,0.06);border-radius:10px;padding:12px 16px;margin-bottom:8px}
.faq-q{font-size:13px;color:#dde4f0;font-weight:500;margin-bottom:6px}
.faq-a{font-size:12px;color:#7a8fa8;line-height:1.6}
.chart-row{display:flex;align-items:center;gap:10px;margin-bottom:10px}
.chart-lbl{font-size:12px;color:#7a8fa8;width:130px;flex-shrink:0;text-align:right}
.chart-bar-bg{flex:1;background:rgba(255,255,255,0.06);border-radius:4px;height:20px;overflow:hidden}
.chart-bar-fill{height:100%;border-radius:4px;display:flex;align-items:center;padding-left:8px}
.chart-bar-num{font-size:11px;font-weight:600;color:#fff}
.chart-pct{font-size:11px;color:#5a7a9a;width:36px;text-align:right}
.heat-cell{display:inline-block;width:36px;height:28px;border-radius:4px;line-height:28px;text-align:center;font-size:11px;font-weight:600;margin:2px}
.adm-divider{border:none;border-top:1px solid rgba(255,255,255,0.06);margin:12px 0}
.escalate-note{background:#fff0ee;border-left:3px solid #d4522a;padding:10px 14px;border-radius:6px;font-size:13px;margin:6px 0}
.login-icon{width:44px;height:44px;border-radius:12px;background:rgba(183,32,46,0.1);display:flex;align-items:center;justify-content:center;font-size:22px;margin-bottom:10px}
.login-title{font-size:19px;font-weight:700;color:#1a1a2e;margin-bottom:2px}
.login-sub{font-size:12.5px;color:#64748b;margin-bottom:16px}
.role-card{border:1px solid #e2e8f0;border-radius:12px;padding:14px 16px;margin-bottom:10px;display:flex;align-items:center;gap:12px}
.role-card-emoji{font-size:22px}
.role-card-lbl{font-size:14px;font-weight:600;color:#1a1a2e}
.role-card-sub{font-size:11px;color:#64748b}
div[role="dialog"] button[kind="primary"]{background:#b7202e!important;border-color:#b7202e!important;border-radius:10px!important;font-weight:600!important}
div[role="dialog"] button[kind="secondary"]{border-radius:10px!important}
div[role="dialog"] .stTextInput input{border-radius:9px!important}
.sb-locked{font-size:12px;color:#fbbf24;padding:10px;background:rgba(251,191,36,0.08);border-radius:8px;text-align:center;margin-top:8px}
.sb-user{font-size:12px;color:#c8d4e8;padding:10px 12px;background:rgba(255,255,255,0.05);border-radius:8px;line-height:1.6}
</style>
""", unsafe_allow_html=True)

BATCHES = {
    "MBA Jan 2026 — Semester 1": "mba_jan_26_sem1",
    "BBA Jan 2026 — Semester 1": "bba_jan_26_sem1",
}
LANGUAGES = {"English 🇬🇧": "English", "हिंदी 🇮🇳": "Hindi", "मराठी": "Marathi"}
KB_PATH     = "data/knowledge_base.json"
ADMIN_PWD   = os.getenv("ADMIN_PASSWORD",  "admin@dpu2026")
FACULTY_PWD = os.getenv("FACULTY_PASSWORD","faculty@dpu2026")

# Demo ERP directory — ERP ID + first name as password (POC only)
from data.mock_students import MOCK_STUDENTS
STUDENTS = MOCK_STUDENTS

ROLE_ICON = {"Student": "🎓", "Admin": "⚙️", "Faculty": "👩‍🏫"}


def erp_personal_answer(query: str, student: dict, language: str) -> str:
    """Answer a personal ERP query for a logged-in student using their verified
    mock ERP record — same approach as erp_demo.py, reused here so the
    authenticated chat can show real personalised answers, not a blank redirect."""
    from rag.pipeline import client, CHAT_MODEL

    context = f"""=== VERIFIED ERP DATA FOR {student['name']} ===

Student: {student['name']}
Program: {student['program']}
Batch: {student['batch']}, Semester {student['semester']}
Specialization: {student['specialization']}
Mentor: {student['mentor']}

FEES:
- Total program fee: Rs {student['fees']['total']:,}
- Paid so far: Rs {student['fees']['paid']:,}
- Outstanding: Rs {student['fees']['outstanding']:,}
- Sem 1: {student['fees']['sem1']}
- Sem 2: {student['fees']['sem2']}

ASSIGNMENTS:
- Total: {student['assignments']['total']}
- Submitted: {student['assignments']['submitted']}
- Pending: {student['assignments']['pending']}
- Pending list: {', '.join(student['assignments']['pending_list']) if student['assignments']['pending_list'] else 'None'}

EXAMINATION:
- Exam form: {student['exam']['form']}
- Admit card: {student['exam']['admit_card']}
- Exam date: {student['exam']['exam_date']}
- Result: {student['exam']['result']}
- Backlog subjects: {', '.join(student['exam']['backlog']) if student['exam']['backlog'] else 'None'}

ATTENDANCE: {student['attendance']}%

BOOKS DISPATCH: {student['books']}"""

    system_prompt = f"""You are DPU EduBot answering a personal query for an enrolled student.

STRICT RULES:
1. Use ONLY the verified ERP data below. Never invent numbers, dates, or details.
2. Address the student by their first name.
3. Be warm, concise, and helpful — like a kind mentor.
4. If their data shows an issue (overdue fees, pending assignments), be direct but supportive.
5. End with a clear next step where useful.
6. Respond in {language}.

{context}"""

    try:
        response = client.chat.completions.create(
            model=CHAT_MODEL,
            temperature=0.1,
            max_tokens=400,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error reaching OpenAI: {str(e)}"

@st.cache_data
def load_kb():
    with open(KB_PATH, encoding="utf-8") as f:
        return json.load(f)

# ── Sample ticket data (UI only — Prompt 2) ───────────────────────
SAMPLE_TICKETS = [
    {"id":"TKT-001","ts":"Today 09:14","q":"Fee paid via UPI but LMS still shows pending — Rs 50,000 deducted from bank","batch":"MBA Jan 26","cat":"Accounts","sub":"Online Fee Payment Issues","priority":"High","status":"Open","agent":"Vivek Nair","sla_hrs":24,"elapsed_hrs":21},
    {"id":"TKT-002","ts":"Today 11:32","q":"Exam form submitted but not visible under Filled Exam Form section on ERP","batch":"MBA Jan 26","cat":"Examination","sub":"Exam Form & Hall Ticket Related","priority":"High","status":"Open","agent":"Sneha Mehta","sla_hrs":24,"elapsed_hrs":18},
    {"id":"TKT-003","ts":"Today 13:05","q":"Books not received — tracking shows out for delivery for 5 consecutive days","batch":"BBA Jan 26","cat":"Dispatch","sub":"Books Delivery Issue","priority":"Medium","status":"In Progress","agent":"Priya Rao","sla_hrs":72,"elapsed_hrs":8},
    {"id":"TKT-004","ts":"Today 14:20","q":"LMS showing wrong semester subjects — Sem 2 content visible instead of Sem 1","batch":"MBA Jan 26","cat":"Academic","sub":"Content Related (LMS, Books)","priority":"Medium","status":"In Progress","agent":"Arjun Kumar","sla_hrs":48,"elapsed_hrs":6},
    {"id":"TKT-005","ts":"Yesterday","q":"Bonafide certificate needed urgently for visa application this Friday","batch":"BBA Jan 26","cat":"Students Section","sub":"Bonafide Certificate Request","priority":"High","status":"Resolved","agent":"Priya Rao","sla_hrs":24,"elapsed_hrs":22},
]
CAT_COLORS = {"Accounts":"cat-accounts","Academic":"cat-academic","Examination":"cat-exam","Students Section":"cat-students","Dispatch":"cat-dispatch"}

REPLIES = {
    "TKT-001": "Dear Student,\n\nThank you for reaching out to the DPU Student Support Team.\n\nWe understand your concern regarding the UPI payment deduction. Please note that online payments can take up to 2 working hours to reflect on the ERP portal due to payment gateway processing times.\n\nIf the amount has not been updated after this window, kindly share the following with your assigned mentor:\n• UTR (Unique Transaction Reference) number\n• Screenshot or PDF of your bank payment confirmation\n\nYour mentor will coordinate with the Accounts team on priority to get this mapped at the earliest.\n\nWe apologise for the inconvenience caused and assure you of a prompt resolution.\n\nWarm regards,\nDPU Student Support Team\nDr. D.Y. Patil Centre for Online Learning",
    "TKT-002": "Dear Student,\n\nThank you for contacting the DPU Examination Support Team.\n\nWe have noted your concern regarding the exam form submission. Kindly allow 2–4 hours for the submission to reflect under Filled Exam Form on the ERP portal, as the system processes submissions in batches.\n\nIf the issue persists, please raise a support ticket on ERP:\n• Category: Examination\n• Nature of Support: Exam Form & Hall Ticket Related\n\nOur examination team will verify your submission status and confirm within 24 hours.\n\nWarm regards,\nDPU Student Support Team",
    "TKT-003": "Dear Student,\n\nThank you for writing to us regarding your book delivery.\n\nWe have noted that your consignment has been showing 'Out for Delivery' status for the past 5 days. We are escalating this to our dispatch coordination team to investigate with the courier partner immediately.\n\nPlease confirm your current delivery address so we can verify it matches our records. If correct, we will initiate a re-dispatch at the earliest at no additional charge.\n\nWe will update you within 48 hours with a resolution.\n\nWarm regards,\nDPU Dispatch Support Team",
}

def sla_pct(elapsed, total): return min(int((elapsed/total)*100), 100)
def sla_class(pct):
    if pct >= 90: return "sla-red",   "🔴"
    if pct >= 70: return "sla-amber", "🟡"
    return "sla-green", "🟢"
def sla_label(elapsed, total):
    rem = total - elapsed
    if rem <= 0: return "🔴 SLA Breached"
    if rem < 4:  return f"🔴 {rem}h left"
    if rem < 12: return f"🟡 {rem}h left"
    return f"🟢 {rem}h left"

# ── LOGIN GATE ───────────────────────────────────────────────────
# Each role gets its own dedicated sign-in screen — never shown together.
if "auth" not in st.session_state:
    st.session_state.auth = {"logged_in": False, "role": None, "user": None}
if "login_role" not in st.session_state:
    st.session_state.login_role = None

_dialog_fn = getattr(st, "dialog", None) or st.experimental_dialog

@_dialog_fn("Welcome to DPU EduBot")
def role_picker_dialog():
    st.markdown("<div class='login-sub'>Please select how you'd like to sign in</div>", unsafe_allow_html=True)
    if st.button("🎓  Continue as Student", use_container_width=True, key="pick_student"):
        st.session_state.login_role = "Student"; st.rerun()
    if st.button("⚙️  Continue as Admin", use_container_width=True, key="pick_admin"):
        st.session_state.login_role = "Admin"; st.rerun()
    if st.button("👩‍🏫  Continue as Faculty", use_container_width=True, key="pick_faculty"):
        st.session_state.login_role = "Faculty"; st.rerun()

@_dialog_fn("Sign in")
def login_dialog():
    login_role = st.session_state.login_role
    st.markdown(f"<div class='login-icon'>{ROLE_ICON[login_role]}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='login-title'>{login_role} Login</div>", unsafe_allow_html=True)
    if login_role == "Student":
        st.markdown("<div class='login-sub'>Sign in using your DPU ERP credentials</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='login-sub'>Sign in using your DPU {login_role.lower()} password</div>", unsafe_allow_html=True)

    error = None
    with st.form(key=f"login_form_{login_role}", border=False):
        if login_role == "Student":
            erp_id = st.text_input("ERP ID", placeholder="Enter your ERP ID (e.g. ERP001)")
            pwd = st.text_input("Password", type="password", placeholder="Enter first name as password (e.g. Pratap)")
        else:
            erp_id = None
            pwd = st.text_input("Password", type="password", placeholder=f"Enter {login_role.lower()} password")
        submitted = st.form_submit_button("🔐 Sign In", type="primary", use_container_width=True)

    if submitted:
        if login_role == "Student":
            student = STUDENTS.get((erp_id or "").strip().upper())
            if student and (pwd or "").strip().lower() == student["name"].split()[0].lower():
                st.session_state.auth = {"logged_in": True, "role": "Student", "user": {"erp_id": erp_id.strip().upper(), **student}}
                st.session_state.login_role = None
                st.rerun()
            else:
                error = "Invalid ERP ID or password."
        else:
            correct_pwd = ADMIN_PWD if login_role == "Admin" else FACULTY_PWD
            if pwd == correct_pwd:
                st.session_state.auth = {"logged_in": True, "role": login_role, "user": None}
                st.session_state.login_role = None
                st.rerun()
            else:
                error = "Incorrect password."
    if error:
        st.error(error)
    if st.button("← Back", key="back_to_roles"):
        st.session_state.login_role = None; st.rerun()

if not st.session_state.auth["logged_in"]:
    if st.session_state.login_role is None:
        role_picker_dialog()
    else:
        login_dialog()

role = st.session_state.auth["role"]
user = st.session_state.auth["user"]

# ── SIDEBAR ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""<div style='text-align:center;padding:16px 0 20px'>
        <div style='font-size:30px'>🎓</div>
        <div style='font-size:16px;font-weight:700;color:#e2e8f4;margin-top:6px'>DPU EduBot</div>
        <div style='font-size:10px;color:rgba(255,255,255,0.35);margin-top:3px'>Dr. D.Y. Patil Centre for Online Learning</div>
    </div>""", unsafe_allow_html=True)
    st.markdown("<hr style='border-color:rgba(255,255,255,0.06);margin:0 0 12px'>", unsafe_allow_html=True)

    admin_panel = "Dashboard"
    if not st.session_state.auth["logged_in"]:
        st.markdown("<div class='sb-locked'>🔒 Please sign in to continue</div>", unsafe_allow_html=True)
    else:
        who = f"{user['name']}<br/><span style='color:#7a8fa8;font-size:11px'>{user['erp_id']}</span>" if role == "Student" and user else role
        st.markdown(f"<div class='sb-user'>{ROLE_ICON[role]} Logged in as<br/><b>{who}</b></div>", unsafe_allow_html=True)
        if role == "Admin":
            st.markdown("<hr style='border-color:rgba(255,255,255,0.06);margin:10px 0'>", unsafe_allow_html=True)
            st.markdown("<p style='color:rgba(255,255,255,0.35);font-size:10px;text-transform:uppercase;letter-spacing:.08em;margin-bottom:8px'>Admin panels</p>", unsafe_allow_html=True)
            admin_panel = st.radio("Panel", ["📊 Dashboard","🎫 Escalation Queue","⏱️ SLA Tracker","✉️ AI Reply Composer","📚 FAQ Manager","📈 Analytics","🗄️ Knowledge Base","🗂️ Batch Knowledge"], label_visibility="collapsed")
        st.markdown("<hr style='border-color:rgba(255,255,255,0.06);margin:10px 0'>", unsafe_allow_html=True)
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.auth = {"logged_in": False, "role": None, "user": None}
            st.session_state.messages = []
            st.rerun()

    st.markdown("<hr style='border-color:rgba(255,255,255,0.06);margin:10px 0'>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:10px;color:rgba(255,255,255,0.25);text-align:center;line-height:1.8'>🔒 Answers grounded only in<br/>verified DPU data<br/>Personal data → ERP redirect</div>", unsafe_allow_html=True)

if not st.session_state.auth["logged_in"]:
    st.markdown("### 🎓 Student Chat")
    st.caption("Ask anything about your program, exams, fees, LMS, assignments, or support tickets")
    st.markdown("---")
    st.info("👋 **Namaste! I'm DPU EduBot.** Please sign in from the popup to get started.")
    st.stop()


# ══════════════════════════════════════════════════════════════════
# STUDENT VIEW — COMPLETELY UNCHANGED INCLUDING LAYER 0
# ══════════════════════════════════════════════════════════════════
if role == "Student":
    col1, col2, col3 = st.columns([2.5, 1.2, 1])
    with col1:
        st.markdown(f"### 🎓 Student Chat — {user['name']}" if user else "### 🎓 Student Chat")
        st.caption("Ask anything about your program, exams, fees, LMS, assignments, or support tickets")
    with col2:
        batch_keys = list(BATCHES.keys())
        default_idx = 0
        if user and user.get("batch"):
            matches = [i for i, k in enumerate(batch_keys) if k.startswith(user["batch"])]
            if matches: default_idx = matches[0]
        batch_label = st.selectbox("Your batch", batch_keys, index=default_idx, label_visibility="collapsed")
    with col3:
        lang_label = st.selectbox("Language", list(LANGUAGES.keys()), label_visibility="collapsed")
    batch_id = BATCHES[batch_label]
    language = LANGUAGES[lang_label]
    st.markdown("---")
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if not st.session_state.messages:
        with st.chat_message("assistant", avatar="🎓"):
            st.markdown(f"""**Namaste! I'm DPU EduBot 👋**\n\nI'm your official learning assistant for **{batch_label}** at Dr. D.Y. Patil Centre for Online Learning.\n\nI can help you with:\n- 📚 LMS access, live sessions, recordings\n- 📝 Assignment submission process\n- 💰 Fee payment and structure\n- 📋 Exam forms, admit cards, results\n- 🎯 Specialization selection\n- 🎫 Support ticket guidance\n- 📦 Books and dispatch queries\n- 👤 Profile and document updates\n\nTry asking me something! 👇""")
            st.markdown("**Quick questions to try:**")
        st.markdown("""
💬 *Try asking any of these in the chat below:*

- How do I submit my assignment?
- My payment failed — which ticket?
- What are my MBA Sem 1 subjects?
- How do I join a live lecture?
""")
    for msg in st.session_state.messages:
        avatar = "🎓" if msg["role"] == "assistant" else "👤"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])
            if msg.get("sources"):
                st.markdown(" ".join([f'<span class="source-chip">📄 {s}</span>' for s in msg["sources"]]), unsafe_allow_html=True)
            if msg.get("erp_link"):
                st.link_button(f"🔗 {msg.get('erp_label','Open ERP')}", msg["erp_link"])
           # if msg.get("escalate"):
           #     st.warning("⚠️ Low confidence — please verify with your mentor or raise a support ticket on ERP → Student Support Ticket.", icon="⚠️")
    if prompt := st.chat_input(f"Ask about {batch_label.split('—')[0].strip()}..."):
        st.session_state.messages.append({"role":"user","content":prompt})
        with st.chat_message("user", avatar="👤"): st.markdown(prompt)
        with st.chat_message("assistant", avatar="🎓"):
            with st.spinner("Looking up verified DPU information..."):
                from rag.pipeline import answer, check_layer0
                from rag.batch_knowledge import check_batch_knowledge

                # Priority: ERP (Layer 0) -> Batch Knowledge (CSV) -> existing FAQ/Website RAG
                layer0 = check_layer0(prompt)
                if layer0:
                    if user:
                        result = {**layer0,
                                  "answer": erp_personal_answer(prompt, user, language),
                                  "sources": ["DPU ERP Student Record"]}
                    else:
                        result = {**layer0, "sources": []}
                else:
                    batch_hit = check_batch_knowledge(
                        prompt, batch_id, batch_label.replace(" — ", " "),
                        user["name"].split()[0] if user else None
                    )
                    result = batch_hit if batch_hit else answer(prompt, batch_id, language)
            st.markdown(result["answer"])
            if result.get("sources"):
                st.markdown(" ".join([f'<span class="source-chip">📄 {s}</span>' for s in result["sources"]]), unsafe_allow_html=True)
            if result.get("erp_link"):
                st.link_button(f"🔗 {result.get('erp_label','Open ERP')}", result["erp_link"])
           # if result.get("escalate"):
           #     st.warning("⚠️ Low confidence — please verify with your mentor or raise a support ticket on ERP → Student Support Ticket.", icon="⚠️")
        st.session_state.messages.append({"role":"assistant","content":result["answer"],"sources":result.get("sources",[]),"erp_link":result.get("erp_link"),"erp_label":result.get("erp_label",""),"escalate":result.get("escalate",False)})
    if st.session_state.messages:
        if st.button("🗑️ Clear conversation", type="secondary"): st.session_state.messages = []; st.rerun()
    st.markdown("<div style='margin-top:24px;text-align:center'><span style='font-size:11px;color:#888'>🔒 Answers grounded only in verified DPU data &nbsp;·&nbsp; Personal data always redirected to ERP</span></div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# ADMIN VIEW — PREMIUM ENTERPRISE DASHBOARD (Prompt 2 — UI only)
# ══════════════════════════════════════════════════════════════════
elif role == "Admin":
    kb = load_kb()
    total_faqs = sum(len(v["faqs"]) for v in kb["layer_1_faqs"].values())
    from rag.pipeline import index_exists
    index_ready = index_exists()

    # ── DASHBOARD ────────────────────────────────────────────────
    if "Dashboard" in admin_panel:
        st.markdown("<h2 style='color:#e2e8f4;font-size:20px;font-weight:600;margin-bottom:4px'>📊 Operations Dashboard</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#5a7a9a;font-size:13px;margin-bottom:20px'>DPU EduBot · Support Operations Centre · MBA & BBA Jan 2026</p>", unsafe_allow_html=True)
        m1,m2,m3,m4,m5 = st.columns(5)
        for col,val,lbl,sub,cls in [(m1,"247","Queries Today","↑ 18% vs yesterday","sub-green"),(m2,"3","Open Escalations","2 high priority","sub-red"),(m3,"94%","Bot Resolution Rate","↑ 5% this week","sub-green"),(m4,str(total_faqs),"Verified FAQs","Layer 1 knowledge base","sub-blue"),(m5,"✅" if index_ready else "❌","Index Status","FAISS ready" if index_ready else "Rebuild needed","sub-green" if index_ready else "sub-red")]:
            with col: st.markdown(f'<div class="adm-metric"><div class="adm-metric-val">{val}</div><div class="adm-metric-lbl">{lbl}</div><div class="adm-metric-sub {cls}">{sub}</div></div>', unsafe_allow_html=True)
        st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)
        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown('<div class="adm-card"><div class="adm-card-title">📊 Top Query Categories Today</div>', unsafe_allow_html=True)
            chart_data = [("Exam & Results",88,"#3b82f6"),("Fee & Payments",72,"#10b981"),("LMS & Sessions",61,"#f59e0b"),("Assignments",45,"#8b5cf6"),("Books & Dispatch",30,"#ef4444"),("Support Tickets",27,"#06b6d4"),("Specialization",18,"#f97316")]
            total_q = sum(c[1] for c in chart_data)
            for lbl,val,color in chart_data:
                pct = int((val/total_q)*100)
                st.markdown(f'<div class="chart-row"><div class="chart-lbl">{lbl}</div><div class="chart-bar-bg"><div class="chart-bar-fill" style="width:{pct}%;background:{color}"><span class="chart-bar-num">{val}</span></div></div><div class="chart-pct">{pct}%</div></div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with col_r:
            st.markdown('<div class="adm-card"><div class="adm-card-title">🎫 Recent Escalations</div>', unsafe_allow_html=True)
            for t in SAMPLE_TICKETS[:4]:
                cat_cls = CAT_COLORS.get(t["cat"],"cat-academic")
                pri_cls = f"pri-{t['priority'].lower()}"
                st.markdown(f'<div class="tkt-row"><div class="tkt-id">{t["id"]}</div><div style="flex:1"><div class="tkt-q">{t["q"][:70]}{"…" if len(t["q"])>70 else ""}</div><div class="tkt-meta">{t["batch"]} · {t["ts"]}</div><div class="tkt-dept"><span class="cat-chip {cat_cls}">{t["cat"]}</span>{t["sub"]}</div></div><span class="{pri_cls}">{t["priority"]}</span></div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        st.markdown('<div class="adm-card"><div class="adm-card-title">📦 Batch-wise Query Distribution</div>', unsafe_allow_html=True)
        b1,b2,b3 = st.columns(3)
        with b1: st.markdown('<div style="background:#0a1628;border:1px solid rgba(255,255,255,0.06);border-radius:10px;padding:14px 16px;text-align:center"><div style="font-size:24px;font-weight:700;color:#3b82f6">158</div><div style="font-size:12px;color:#5a7a9a;margin-top:4px">MBA Jan 2026 Sem 1</div><div style="font-size:11px;color:#4ade80;margin-top:3px">64% of total</div></div>', unsafe_allow_html=True)
        with b2: st.markdown('<div style="background:#0a1628;border:1px solid rgba(255,255,255,0.06);border-radius:10px;padding:14px 16px;text-align:center"><div style="font-size:24px;font-weight:700;color:#10b981">89</div><div style="font-size:12px;color:#5a7a9a;margin-top:4px">BBA Jan 2026 Sem 1</div><div style="font-size:11px;color:#4ade80;margin-top:3px">36% of total</div></div>', unsafe_allow_html=True)
        with b3: st.markdown('<div style="background:#0a1628;border:1px solid rgba(255,255,255,0.06);border-radius:10px;padding:14px 16px;text-align:center"><div style="font-size:24px;font-weight:700;color:#f59e0b">247</div><div style="font-size:12px;color:#5a7a9a;margin-top:4px">Total today</div><div style="font-size:11px;color:#4ade80;margin-top:3px">↑ 18% vs yesterday</div></div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── ESCALATION QUEUE ─────────────────────────────────────────
    elif "Escalation" in admin_panel:
        st.markdown("<h2 style='color:#e2e8f4;font-size:20px;font-weight:600;margin-bottom:4px'>🎫 Escalation Queue</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#5a7a9a;font-size:13px;margin-bottom:20px'>Tickets auto-created when bot confidence is below threshold or fallback triggered</p>", unsafe_allow_html=True)
        e1,e2,e3,e4 = st.columns(4)
        for col,val,lbl,cls in [(e1,"2","Open","sub-red"),(e2,"2","In Progress","sub-amber"),(e3,"1","Resolved today","sub-green"),(e4,"12","Resolved this week","sub-blue")]:
            with col: st.markdown(f'<div class="adm-metric"><div class="adm-metric-val {cls}">{val}</div><div class="adm-metric-lbl">{lbl}</div></div>', unsafe_allow_html=True)
        st.markdown("<div style='margin-top:16px'></div>", unsafe_allow_html=True)
        filter_status = st.selectbox("Filter by status", ["All","Open","In Progress","Resolved"])
        filtered = SAMPLE_TICKETS if filter_status == "All" else [t for t in SAMPLE_TICKETS if t["status"] == filter_status]
        st.markdown(f"<p style='color:#5a7a9a;font-size:12px;margin-bottom:12px'>Showing {len(filtered)} tickets</p>", unsafe_allow_html=True)
        for t in filtered:
            pri_cls = f"pri-{t['priority'].lower()}"
            cat_cls = CAT_COLORS.get(t["cat"],"cat-academic")
            status_cls = {"Open":"status-open","In Progress":"status-progress","Resolved":"status-resolved"}.get(t["status"],"status-open")
            pct = sla_pct(t["elapsed_hrs"],t["sla_hrs"])
            bar_cls,_ = sla_class(pct)
            with st.expander(f"{t['id']} · {t['q'][:60]}…  [{t['status']}]", expanded=False):
                c1,c2 = st.columns([2,1])
                with c1:
                    st.markdown(f"**Query:** {t['q']}")
                    st.markdown(f"**Batch:** {t['batch']} &nbsp;|&nbsp; **Raised:** {t['ts']}")
                    st.markdown(f"**Department:** <span class='cat-chip {cat_cls}'>{t['cat']}</span> → {t['sub']}", unsafe_allow_html=True)
                    st.markdown(f"**Assigned to:** {t['agent']}")
                with c2:
                    st.markdown(f"**Priority:** <span class='{pri_cls}'>{t['priority']}</span>", unsafe_allow_html=True)
                    st.markdown(f"**Status:** <span class='{status_cls}'>{t['status']}</span>", unsafe_allow_html=True)
                    st.markdown(f"**SLA:** {t['elapsed_hrs']}h / {t['sla_hrs']}h")
                    st.markdown(f'<div class="sla-bar-bg" style="margin-top:6px"><div class="sla-bar-fill {bar_cls}" style="width:{pct}%"></div></div>', unsafe_allow_html=True)
                b1,b2,b3 = st.columns(3)
                with b1: st.button("✉️ Draft Reply",   key=f"r_{t['id']}")
                with b2: st.button("✅ Mark Resolved", key=f"s_{t['id']}")
                with b3: st.button("↗️ Reassign",      key=f"a_{t['id']}")

    # ── SLA TRACKER ──────────────────────────────────────────────
    elif "SLA" in admin_panel:
        st.markdown("<h2 style='color:#e2e8f4;font-size:20px;font-weight:600;margin-bottom:4px'>⏱️ SLA Tracker</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#5a7a9a;font-size:13px;margin-bottom:20px'>Live SLA countdown for open and in-progress tickets</p>", unsafe_allow_html=True)
        st.markdown('<div class="adm-card"><div class="adm-card-title">📋 SLA Rules — DPU Support Policy</div>', unsafe_allow_html=True)
        r1,r2,r3,r4,r5 = st.columns(5)
        for col,cat,hrs,color in [(r1,"Accounts","24 hrs","#ef4444"),(r2,"Academic","48 hrs","#3b82f6"),(r3,"Examination","24 hrs","#f59e0b"),(r4,"Students Sec.","48 hrs","#10b981"),(r5,"Dispatch","72 hrs","#8b5cf6")]:
            with col: st.markdown(f'<div style="text-align:center;padding:10px;background:#0a1628;border-radius:8px;border:1px solid rgba(255,255,255,0.06)"><div style="font-size:18px;font-weight:700;color:{color}">{hrs}</div><div style="font-size:11px;color:#5a7a9a;margin-top:4px">{cat}</div></div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        active = [t for t in SAMPLE_TICKETS if t["status"] != "Resolved"]
        st.markdown('<div class="adm-card"><div class="adm-card-title">🔴 Active SLA Countdowns</div>', unsafe_allow_html=True)
        for t in active:
            pct = sla_pct(t["elapsed_hrs"],t["sla_hrs"])
            bar_cls,_ = sla_class(pct)
            time_lbl = sla_label(t["elapsed_hrs"],t["sla_hrs"])
            cat_cls = CAT_COLORS.get(t["cat"],"cat-academic")
            time_color = "#f87171" if pct>=90 else "#fbbf24" if pct>=70 else "#4ade80"
            st.markdown(f'<div class="sla-wrap"><div class="sla-header"><div><span class="tkt-id" style="margin-right:8px">{t["id"]}</span><span class="sla-title">{t["q"][:62]}{"…" if len(t["q"])>62 else ""}</span></div><span style="font-size:12px;font-weight:600;color:{time_color}">{time_lbl}</span></div><div class="sla-bar-bg"><div class="sla-bar-fill {bar_cls}" style="width:{pct}%"></div></div><div class="sla-meta"><span class="cat-chip {cat_cls}">{t["cat"]}</span>{t["elapsed_hrs"]}h of {t["sla_hrs"]}h SLA &nbsp;·&nbsp; {t["agent"]} &nbsp;·&nbsp; {t["batch"]}</div></div><hr class="adm-divider">', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── AI REPLY COMPOSER ────────────────────────────────────────
    elif "Reply" in admin_panel:
        st.markdown("<h2 style='color:#e2e8f4;font-size:20px;font-weight:600;margin-bottom:4px'>✉️ AI Reply Composer</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#5a7a9a;font-size:13px;margin-bottom:20px'>Select a ticket and generate a professional DPU-tone reply draft</p>", unsafe_allow_html=True)
        tkt_options = {f"{t['id']} — {t['q'][:55]}…": t for t in SAMPLE_TICKETS}
        sel_key = st.selectbox("Select ticket", list(tkt_options.keys()))
        tkt = tkt_options[sel_key]
        cat_cls = CAT_COLORS.get(tkt["cat"],"cat-academic")
        pri_cls = f"pri-{tkt['priority'].lower()}"
        st.markdown(f'<div class="adm-card"><div class="adm-card-title">📋 Ticket Details</div><div class="tkt-q" style="margin-bottom:8px">{tkt["q"]}</div><div class="tkt-meta">Batch: {tkt["batch"]} &nbsp;·&nbsp; Raised: {tkt["ts"]} &nbsp;·&nbsp; Agent: {tkt["agent"]}</div><div style="margin-top:8px"><span class="cat-chip {cat_cls}">{tkt["cat"]}</span><span style="font-size:12px;color:#7a8fa8">{tkt["sub"]}</span>&nbsp;&nbsp;<span class="{pri_cls}">{tkt["priority"]}</span></div></div>', unsafe_allow_html=True)
        default_reply = REPLIES.get(tkt["id"], f"Dear Student,\n\nThank you for reaching out to the DPU Student Support Team.\n\nWe have received your query and your ticket has been assigned to {tkt['agent']} for priority resolution.\n\nPlease allow up to {tkt['sla_hrs']} hours for a complete resolution as per our SLA policy.\n\nWarm regards,\nDPU Student Support Team")
        st.markdown(f'<div class="adm-card"><div class="adm-card-title">🤖 AI-Drafted Reply — DPU Learner Support Tone</div><div class="email-box">{default_reply}</div></div>', unsafe_allow_html=True)
        ba,bb,bc = st.columns(3)
        with ba: st.button("📋 Copy Reply", type="primary")
        with bb: st.button("🔄 Regenerate")
        with bc: st.button("✅ Mark Resolved")
        st.markdown("<p style='color:#5a7a9a;font-size:11px;margin-top:6px'>Review and personalise before sending. AI replies are drafts only.</p>", unsafe_allow_html=True)

    # ── FAQ MANAGER ──────────────────────────────────────────────
    elif "FAQ" in admin_panel:
        st.markdown("<h2 style='color:#e2e8f4;font-size:20px;font-weight:600;margin-bottom:4px'>📚 FAQ Manager</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#5a7a9a;font-size:13px;margin-bottom:20px'>View and manage the DPU EduBot verified knowledge base</p>", unsafe_allow_html=True)
        f1,f2,f3 = st.columns(3)
        with f1: st.markdown(f'<div class="adm-metric"><div class="adm-metric-val sub-blue">{total_faqs}</div><div class="adm-metric-lbl">Total FAQs</div></div>', unsafe_allow_html=True)
        with f2: st.markdown('<div class="adm-metric"><div class="adm-metric-val sub-green">11</div><div class="adm-metric-lbl">Categories</div></div>', unsafe_allow_html=True)
        with f3: st.markdown('<div class="adm-metric"><div class="adm-metric-val sub-amber">✅</div><div class="adm-metric-lbl">Index synced</div></div>', unsafe_allow_html=True)
        st.markdown("<div style='margin-top:16px'></div>", unsafe_allow_html=True)
        all_cats = ["All"] + [v["label"] for v in kb["layer_1_faqs"].values()]
        cat_filter = st.selectbox("Filter by category", all_cats)
        with st.expander("➕ Add new FAQ"):
            new_cat = st.selectbox("Category", list(kb["layer_1_faqs"].keys()))
            new_q   = st.text_input("Question")
            new_a   = st.text_area("Answer", height=100)
            st.text_input("Tags (comma separated)", placeholder="e.g. fees, payment, erp")
            if st.button("💾 Save FAQ", type="primary"):
                if new_q and new_a: st.success("✅ FAQ saved. Click 'Rebuild Index' to activate."); st.info("Live write to knowledge_base.json — coming in Prompt 1 phase.")
                else: st.warning("Question and answer required.")
        for cat_key, cat_data in kb["layer_1_faqs"].items():
            if cat_filter != "All" and cat_data["label"] != cat_filter: continue
            st.markdown(f'<div class="adm-card"><div class="adm-card-title">📂 {cat_data["label"]} <span style="font-size:12px;color:#5a7a9a;font-weight:400">({len(cat_data["faqs"])} FAQs)</span></div>', unsafe_allow_html=True)
            for faq in cat_data["faqs"][:5]:
                st.markdown(f'<div class="faq-item"><div class="faq-q">Q: {faq["q"]}</div><div class="faq-a">A: {faq["a"][:120]}{"…" if len(faq["a"])>120 else ""}</div></div>', unsafe_allow_html=True)
            if len(cat_data["faqs"]) > 5:
                st.markdown(f"<p style='font-size:11px;color:#5a7a9a;text-align:center;margin:4px 0 8px'>+ {len(cat_data['faqs'])-5} more in this category</p>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        st.markdown('<div class="adm-card"><div class="adm-card-title">🔨 Rebuild Index</div>', unsafe_allow_html=True)
        if st.button("🚀 Rebuild FAISS Index", type="primary"):
            with st.spinner("Rebuilding..."):
                try:
                    from rag.pipeline import invalidate_cache; invalidate_cache()
                    from ingestion.build_index import build_index; n = build_index()
                    st.cache_data.clear(); st.success(f"✅ {n} chunks indexed")
                except Exception as e: st.error(f"❌ {e}")
        st.markdown("</div>", unsafe_allow_html=True)

    # ── ANALYTICS ────────────────────────────────────────────────
    elif "Analytics" in admin_panel:
        st.markdown("<h2 style='color:#e2e8f4;font-size:20px;font-weight:600;margin-bottom:4px'>📈 Analytics</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#5a7a9a;font-size:13px;margin-bottom:20px'>Support operations intelligence — weekly view</p>", unsafe_allow_html=True)
        a1,a2,a3,a4 = st.columns(4)
        for col,val,lbl,sub,cls in [(a1,"1,847","Total queries","↑ 22% vs last week","sub-green"),(a2,"94%","Bot resolution rate","Industry avg: 78%","sub-green"),(a3,"6%","Escalation rate","↓ 2% vs last week","sub-green"),(a4,"0.81","Avg confidence","Threshold: 0.68","sub-blue")]:
            with col: st.markdown(f'<div class="adm-metric"><div class="adm-metric-val">{val}</div><div class="adm-metric-lbl">{lbl}</div><div class="adm-metric-sub {cls}">{sub}</div></div>', unsafe_allow_html=True)
        st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)
        col_l,col_r = st.columns(2)
        with col_l:
            st.markdown('<div class="adm-card"><div class="adm-card-title">📅 Daily Query Volume — This Week</div>', unsafe_allow_html=True)
            days_data = [("Mon",210),("Tue",285),("Wed",242),("Thu",310),("Fri",320),("Sat",160),("Sun",85)]
            max_v = max(d[1] for d in days_data)
            for day,val in days_data:
                pct = int((val/max_v)*100); color = "#3b82f6" if day not in ("Sat","Sun") else "#4a6fa8"
                st.markdown(f'<div class="chart-row"><div class="chart-lbl">{day}</div><div class="chart-bar-bg"><div class="chart-bar-fill" style="width:{pct}%;background:{color}"><span class="chart-bar-num">{val}</span></div></div><div class="chart-pct">{pct}%</div></div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with col_r:
            st.markdown('<div class="adm-card"><div class="adm-card-title">🔍 Top Unanswered Queries</div>', unsafe_allow_html=True)
            gaps = [("Re-evaluation after result fail",12,"#ef4444"),("Exam during power cut — makeup?",9,"#f59e0b"),("Company sponsorship via cheque",7,"#f59e0b"),("WES Canada degree verification",6,"#3b82f6"),("Proctoring flag — no wrongdoing",5,"#3b82f6"),("Exam exemption for professionals",4,"#10b981")]
            for q_text,count,color in gaps:
                st.markdown(f'<div class="chart-row"><div class="chart-lbl" style="font-size:11px;width:180px">{q_text}</div><div class="chart-bar-bg"><div class="chart-bar-fill" style="width:{int(count/12*100)}%;background:{color}"><span class="chart-bar-num">{count}x</span></div></div></div>', unsafe_allow_html=True)
            st.markdown("<p style='color:#5a7a9a;font-size:11px;margin-top:8px'>These need answers added to the knowledge base</p></div>", unsafe_allow_html=True)
        st.markdown('<div class="adm-card"><div class="adm-card-title">🌡️ Support Category Heatmap — Queries by Day</div>', unsafe_allow_html=True)
        heatmap = {"Accounts":[45,52,38,61,58,12,5],"Academic":[38,42,55,48,62,22,10],"Examination":[28,55,44,72,68,8,3],"Students Section":[12,15,18,14,20,6,2],"Dispatch":[8,10,9,12,14,4,1]}
        days = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
        html = "<div style='overflow-x:auto'><table style='border-collapse:separate;border-spacing:4px'><tr><td style='width:120px'></td>"
        for d in days: html += f"<td style='text-align:center;font-size:11px;color:#5a7a9a;padding:2px 4px'>{d}</td>"
        html += "</tr>"
        for cat,vals in heatmap.items():
            mv = max(vals); html += f"<tr><td style='font-size:11px;color:#7a8fa8;padding:2px 8px 2px 0;text-align:right'>{cat}</td>"
            for v in vals:
                intensity = int((v/mv)*100)
                if intensity > 75: bg,tc="#1d4ed8","#bfdbfe"
                elif intensity > 50: bg,tc="#1e40af","#93c5fd"
                elif intensity > 25: bg,tc="#1e3a5f","#60a5fa"
                else: bg,tc="#0f1f38","#3b5a8a"
                html += f"<td><div class='heat-cell' style='background:{bg};color:{tc}'>{v}</div></td>"
            html += "</tr>"
        html += "</table></div>"
        st.markdown(html, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── BATCH KNOWLEDGE MANAGEMENT ────────────────────────────────
    # Checked before the generic "Knowledge" match below, since "Batch
    # Knowledge" also contains the substring "Knowledge".
    elif "Batch Knowledge" in admin_panel:
        from rag.batch_knowledge import DOC_TYPES, save_batch_csv, uploaded_status
        st.markdown("<h2 style='color:#e2e8f4;font-size:20px;font-weight:600;margin-bottom:4px'>🗂️ Batch Knowledge Management</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#5a7a9a;font-size:13px;margin-bottom:20px'>Upload the Session Schedule and Exam Timetable CSVs for each batch. Student chat answers timetable/exam questions ONLY from these files.</p>", unsafe_allow_html=True)

        bk_batch_label = st.selectbox("Batch", list(BATCHES.keys()), key="bk_batch_sel")
        bk_batch_id = BATCHES[bk_batch_label]
        status = uploaded_status(bk_batch_id)

        col_s, col_e = st.columns(2)
        for col, doc_type in [(col_s, "session_schedule"), (col_e, "exam_timetable")]:
            with col:
                meta = DOC_TYPES[doc_type]
                st.markdown(f'<div class="adm-card"><div class="adm-card-title">📅 {meta["label"]}</div>', unsafe_allow_html=True)
                if status[doc_type]:
                    st.markdown('<span class="sub-green">✅ Uploaded</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span class="sub-amber">⚠️ Not uploaded yet</span>', unsafe_allow_html=True)
                up = st.file_uploader(f"Upload {meta['label']} CSV", type=["csv"], key=f"bk_upload_{doc_type}")
                if up and st.button(f"💾 Save {meta['label']}", key=f"bk_save_{doc_type}"):
                    try:
                        n = save_batch_csv(bk_batch_id, doc_type, up)
                        st.success(f"✅ Saved — {n} rows")
                        st.rerun()
                    except ValueError as e:
                        st.error(f"❌ {e}")
                st.markdown("</div>", unsafe_allow_html=True)

    # ── KNOWLEDGE BASE ───────────────────────────────────────────
    elif "Knowledge" in admin_panel:
        st.markdown("<h2 style='color:#e2e8f4;font-size:20px;font-weight:600;margin-bottom:4px'>🗄️ Knowledge Base</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#5a7a9a;font-size:13px;margin-bottom:20px'>Manage the DPU EduBot 4-layer knowledge architecture</p>", unsafe_allow_html=True)
        k1,k2,k3,k4 = st.columns(4)
        for col,val,lbl,sub,cls in [(k1,"156","Chunks indexed","FAISS ready","sub-green"),(k2,str(total_faqs),"Verified FAQs","Layer 1","sub-blue"),(k3,"2","Active batches","Layer 2","sub-blue"),(k4,"27","Layer 0 triggers","ERP redirects","sub-amber")]:
            with col: st.markdown(f'<div class="adm-metric"><div class="adm-metric-val">{val}</div><div class="adm-metric-lbl">{lbl}</div><div class="adm-metric-sub {cls}">{sub}</div></div>', unsafe_allow_html=True)
        st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)
        col_a,col_b = st.columns(2)
        with col_a:
            st.markdown('<div class="adm-card"><div class="adm-card-title">🔨 Index Builder</div>', unsafe_allow_html=True)
            if not index_ready: st.markdown('<div style="background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.2);border-radius:8px;padding:10px 14px;font-size:12px;color:#f87171;margin-bottom:10px">⚠️ Index not found — build required</div>', unsafe_allow_html=True)
            if st.button("🚀 Build / Rebuild Index", type="primary"):
                with st.spinner("Building..."):
                    try:
                        from rag.pipeline import invalidate_cache; invalidate_cache()
                        from ingestion.build_index import build_index; n = build_index()
                        st.cache_data.clear(); st.success(f"✅ {n} chunks indexed")
                    except Exception as e: st.error(f"❌ {e}")
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown('<div class="adm-card"><div class="adm-card-title">📤 Upload Batch Document</div>', unsafe_allow_html=True)
            batch_sel = st.selectbox("Batch", list(BATCHES.keys()))
            doc_type  = st.selectbox("Document type", ["academic_calendar","session_schedule","exam_dates","fee_structure","subject_list","general"])
            uploaded  = st.file_uploader("Upload PDF / DOCX / Excel", type=["pdf","docx","xlsx"])
            if uploaded and st.button("📥 Parse & Stage"):
                bid = BATCHES[batch_sel]; tmp = os.path.join(os.environ.get("TEMP", os.getcwd()), uploaded.name.replace(" ", "_"))
                with open(tmp,"wb") as fh: fh.write(uploaded.read())
                with st.spinner(f"Parsing {uploaded.name}..."):
                    from ingestion.parse_docs import parse_pdf,parse_docx,parse_excel
                    if uploaded.name.endswith(".pdf"): chunks = parse_pdf(tmp,bid,doc_type)
                    elif uploaded.name.endswith(".docx"): chunks = parse_docx(tmp,bid,doc_type)
                    else: chunks = parse_excel(tmp,bid,doc_type)
                if chunks: st.success(f"✅ {len(chunks)} chunks extracted"); st.info("Click Rebuild Index to activate.")
                else: st.warning("No content extracted.")
            st.markdown("</div>", unsafe_allow_html=True)
        with col_b:
            st.markdown('<div class="adm-card"><div class="adm-card-title">📊 Knowledge Base Status</div>', unsafe_allow_html=True)
            st.markdown("<p style='color:#7a8fa8;font-size:11px;margin-bottom:8px'>LAYER 1 — VERIFIED FAQs</p>", unsafe_allow_html=True)
            for _,cat_data in kb["layer_1_faqs"].items():
                n = len(cat_data["faqs"])
                st.markdown(f'<div style="display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid rgba(255,255,255,0.04);font-size:12px"><span style="color:#c8d4e8">✅ {cat_data["label"]}</span><span style="color:#4ade80;font-weight:600">{n} FAQs</span></div>', unsafe_allow_html=True)
            st.markdown("<p style='color:#7a8fa8;font-size:11px;margin:12px 0 8px'>LAYER 2 — BATCH DATA</p>", unsafe_allow_html=True)
            for _,batch in kb["layer_2_batch_specific"].items():
                valid = [s for s in batch["subjects"] if "TBD" not in s["code"] and "ADMIN" not in s["code"]]
                ok = len(valid) > 0 and "sem1" in batch.get("fee_structure",{})
                st.markdown(f'<div style="display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid rgba(255,255,255,0.04);font-size:12px"><span style="color:#c8d4e8">{"✅" if ok else "⚠️"} {batch["label"]}</span><span style="color:{"#4ade80" if ok else "#fbbf24"}">{len(valid)} subjects</span></div>', unsafe_allow_html=True)
            st.markdown("<p style='color:#7a8fa8;font-size:11px;margin:12px 0 8px'>LAYER 0 — ERP REDIRECT RULES</p>", unsafe_allow_html=True)
            nt = len(kb["layer_0_redirect_rules"]["triggers"]); nr = len(kb["layer_0_redirect_rules"]["redirects"])
            st.markdown(f'<div style="background:rgba(251,191,36,0.08);border:1px solid rgba(251,191,36,0.15);border-radius:8px;padding:10px 14px;font-size:12px;color:#fbbf24">🔒 {nt} triggers → {nr} ERP redirects<br/><span style="color:#5a7a9a;font-size:11px">Layer 0 locked — personal queries always redirected</span></div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# FACULTY VIEW — UNCHANGED
# ══════════════════════════════════════════════════════════════════
elif role == "Faculty":
    st.markdown("### 👩‍🏫 Faculty Quick Access")
    kb = load_kb()
    c1,c2,c3 = st.columns(3)
    c1.metric("Available Batches", len(BATCHES))
    c2.metric("FAQ Knowledge Base", sum(len(v["faqs"]) for v in kb["layer_1_faqs"].values()))
    c3.metric("Your Role", "Faculty")
    st.markdown("---")
    col_a,col_b = st.columns(2)
    with col_a:
        st.subheader("📅 Batch Quick Reference")
        batch_sel = st.selectbox("Select batch", list(BATCHES.keys()))
        bid = BATCHES[batch_sel]
        if bid in kb["layer_2_batch_specific"]:
            batch = kb["layer_2_batch_specific"][bid]
            st.markdown(f"**Program:** {batch['program']}")
            st.markdown(f"**Semester:** {batch['semester']}")
            valid_subjects = [s for s in batch["subjects"] if "TBD" not in s["code"] and "ADMIN" not in s["code"]]
            if valid_subjects:
                st.markdown("**Subjects this semester:**")
                for s in valid_subjects: st.markdown(f"- `{s['code']}` {s['name']}")
            st.markdown("**Key dates:**")
            for k,v in batch.get("important_dates",{}).items():
                if k != "note": st.markdown(f"- **{k.replace('_',' ').title()}:** {v}")
            st.markdown("**Quick ERP links:**")
            for name,url in batch.get("erp_links",{}).items(): st.markdown(f"- [{name.replace('_',' ').title()}]({url})")
    with col_b:
        st.subheader("📤 Upload Study Material")
        f_batch = st.selectbox("Batch", list(BATCHES.keys()), key="fac_batch")
        f_type  = st.selectbox("Material type", ["session_schedule","academic_calendar","exam_dates","reading_list","assignment_guide","project_guidelines"])
        f_file  = st.file_uploader("Upload PDF / DOCX / Excel", type=["pdf","docx","xlsx"], key="fac_upload")
        if f_file and st.button("📥 Upload and Index", type="primary"):
            bid2 = BATCHES[f_batch]; tmp = os.path.join(os.environ.get("TEMP", os.getcwd()), f_file.name.replace(" ", "_"))
            with open(tmp,"wb") as fh: fh.write(f_file.read())
            with st.spinner("Processing..."):
                from ingestion.parse_docs import parse_pdf,parse_docx,parse_excel
                if f_file.name.endswith(".pdf"): ch = parse_pdf(tmp,bid2,f_type)
                elif f_file.name.endswith(".docx"): ch = parse_docx(tmp,bid2,f_type)
                else: ch = parse_excel(tmp,bid2,f_type)
            st.success(f"✅ {len(ch)} chunks from {f_file.name}"); st.info("Ask Admin to rebuild the index.")
        st.markdown("---")
        st.subheader("📊 Top Student Query Topics")
        for topic,count in [("Exam & Hall Ticket",88),("Fee Payment",72),("Assignment Submission",61),("LMS Access",55),("Support Tickets",45),("Specialization",38),("Books & Dispatch",30)]:
            ct,cb = st.columns([3,1])
            with ct: st.progress(count/100, text=topic)
            with cb: st.caption(f"{count} queries")
