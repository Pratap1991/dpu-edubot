"""
DPU EduBot — ERP Personalised Queries (Standalone POC)
=======================================================
Run this AS A SEPARATE PAGE:
    streamlit run erp_demo.py

This file is COMPLETELY INDEPENDENT of the main EduBot app.
It does NOT touch app/main.py, rag/pipeline.py, or knowledge_base.json.
If anything breaks here, your main EduBot keeps working perfectly.

Demo flow:
1. Student picks ERP ID from dropdown (auto-detected in production)
2. Dashboard shows their personal data
3. Chat box answers personal queries using OpenAI + verified ERP data
"""

import streamlit as st
import os
import sys
from dotenv import load_dotenv
from openai import OpenAI

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data.mock_students import MOCK_STUDENTS

load_dotenv()

st.set_page_config(
    page_title="DPU EduBot — ERP Demo",
    page_icon="🎓",
    layout="wide"
)

# ─── OpenAI client ─────────────────────────────────────────────────
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ════════════════════════════════════════════════════════════════════
# STYLING
# ════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
.banner {background:#0f2744;color:#fff;padding:14px 20px;border-radius:10px;margin-bottom:14px}
.banner h2 {margin:0;font-size:18px;font-weight:600}
.banner p {margin:4px 0 0;font-size:12px;opacity:0.75}
.profile-card {background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:14px 18px;margin-bottom:10px}
.section-title {font-size:12px;font-weight:700;color:#0f2744;text-transform:uppercase;letter-spacing:.05em;margin-bottom:8px}
.kv {display:flex;justify-content:space-between;font-size:13px;padding:3px 0;border-bottom:1px dashed #e2e8f0}
.kv:last-child {border:none}
.kv-k {color:#64748b}
.kv-v {color:#0f2744;font-weight:500}
.poc-tag {background:#fef3c7;color:#92400e;padding:3px 10px;border-radius:20px;font-size:11px;font-weight:600;display:inline-block;margin-left:8px}
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════
# HEADER
# ════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="banner">
  <h2>🎓 DPU EduBot — Personalised Queries POC <span class="poc-tag">DEMO MODE</span></h2>
  <p>Sign in with your ERP ID to ask personal questions about your fees, assignments, exams, and more</p>
</div>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════
# ERP ID PICKER (in production this is auto-detected from ERP URL)
# ════════════════════════════════════════════════════════════════════
col_a, col_b = st.columns([1, 2])
with col_a:
    erp_id = st.selectbox(
        "🔐 Select your ERP ID",
        options=[""] + list(MOCK_STUDENTS.keys()),
        index=0,
        help="In production, this will be auto-detected from the ERP portal session"
    )
with col_b:
    st.markdown("")
    st.caption(
        "ℹ️ **Demo:** Manually select an ERP ID. "
        "In production inside the ERP portal, EduBot reads your ID automatically — no login needed here."
    )


# Stop until ERP ID selected
if not erp_id:
    st.info("👆 Please select an ERP ID above to start. Try **ERP001** for a typical mid-program student, or **ERP003** to see how the bot handles a student with overdue fees.")
    st.stop()


student = MOCK_STUDENTS[erp_id]

# ════════════════════════════════════════════════════════════════════
# STUDENT DASHBOARD
# ════════════════════════════════════════════════════════════════════
st.success(f"✅ Welcome **{student['name']}** — {student['program']}, {student['batch']}, Semester {student['semester']}")

st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="profile-card">
      <div class="section-title">👤 Profile</div>
      <div class="kv"><span class="kv-k">ERP ID</span><span class="kv-v">{student['name']}</span></div>
      <div class="kv"><span class="kv-k">PRN</span><span class="kv-v">{student['prn']}</span></div>
      <div class="kv"><span class="kv-k">Specialization</span><span class="kv-v">{student['specialization']}</span></div>
      <div class="kv"><span class="kv-k">Mentor</span><span class="kv-v">{student['mentor']}</span></div>
      <div class="kv"><span class="kv-k">Attendance</span><span class="kv-v">{student['attendance']}%</span></div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="profile-card">
      <div class="section-title">💰 Fees</div>
      <div class="kv"><span class="kv-k">Total fee</span><span class="kv-v">Rs {student['fees']['total']:,}</span></div>
      <div class="kv"><span class="kv-k">Paid</span><span class="kv-v">Rs {student['fees']['paid']:,}</span></div>
      <div class="kv"><span class="kv-k">Outstanding</span><span class="kv-v">Rs {student['fees']['outstanding']:,}</span></div>
      <div class="kv"><span class="kv-k">Sem 1</span><span class="kv-v">{student['fees']['sem1'][:30]}…</span></div>
      <div class="kv"><span class="kv-k">Sem 2</span><span class="kv-v">{student['fees']['sem2'][:30]}…</span></div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="profile-card">
      <div class="section-title">📚 Academic</div>
      <div class="kv"><span class="kv-k">Assignments submitted</span><span class="kv-v">{student['assignments']['submitted']} / {student['assignments']['total']}</span></div>
      <div class="kv"><span class="kv-k">Pending assignments</span><span class="kv-v">{student['assignments']['pending']}</span></div>
      <div class="kv"><span class="kv-k">Exam form</span><span class="kv-v">{student['exam']['form'][:25]}…</span></div>
      <div class="kv"><span class="kv-k">Admit card</span><span class="kv-v">{student['exam']['admit_card'][:25]}…</span></div>
      <div class="kv"><span class="kv-k">Books</span><span class="kv-v">{student['books'][:25]}…</span></div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")


# ════════════════════════════════════════════════════════════════════
# CHAT BOX
# ════════════════════════════════════════════════════════════════════
st.markdown("### 💬 Ask me anything about your account")
st.caption("Try: *What is my fee status?*  •  *What assignments are pending?*  •  *When is my exam?*  •  *Have I submitted all assignments?*")

# Quick-pick buttons
qc1, qc2, qc3, qc4 = st.columns(4)
sample_questions = []
with qc1:
    if st.button("💰 My fee status"):
        sample_questions.append("What is my fee status?")
with qc2:
    if st.button("📝 Pending assignments"):
        sample_questions.append("What assignments are pending?")
with qc3:
    if st.button("📋 Exam status"):
        sample_questions.append("When is my exam and is my admit card available?")
with qc4:
    if st.button("📦 Books status"):
        sample_questions.append("Have my books been delivered?")

# Chat session per ERP ID
chat_key = f"chat_{erp_id}"
if chat_key not in st.session_state:
    st.session_state[chat_key] = []

# Show chat history
for msg in st.session_state[chat_key]:
    with st.chat_message(msg["role"], avatar="🎓" if msg["role"] == "assistant" else "👤"):
        st.markdown(msg["content"])

# Handle quick-pick OR typed input
prompt = sample_questions[0] if sample_questions else st.chat_input(f"Ask about your account, {student['name'].split()[0]}…")

if prompt:
    # User message
    st.session_state[chat_key].append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # Build verified context for OpenAI
    context = f"""=== VERIFIED ERP DATA FOR {student['name']} ===

Student: {student['name']}
ERP ID: {erp_id}
PRN: {student['prn']}
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
5. End with a clear next step where useful (e.g. "You can pay online at ERP — Payments section").
6. If the question is NOT about their personal data (e.g. general FAQ like 'is internship mandatory'), reply: "For general questions please use the main EduBot chat. This page is for your personal account queries."

{context}"""

    # Call OpenAI
    with st.chat_message("assistant", avatar="🎓"):
        with st.spinner("Looking up your verified ERP data…"):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    temperature=0.1,
                    max_tokens=400,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user",   "content": prompt}
                    ]
                )
                answer = response.choices[0].message.content
            except Exception as e:
                answer = f"⚠️ Error reaching OpenAI: {str(e)}"

        st.markdown(answer)
        st.caption("📄 Source: DPU ERP — verified student record")

    # Save to history
    st.session_state[chat_key].append({"role": "assistant", "content": answer})

# Clear button
if st.session_state[chat_key]:
    if st.button("🗑️ Clear chat"):
        st.session_state[chat_key] = []
        st.rerun()


# ════════════════════════════════════════════════════════════════════
# FOOTER
# ════════════════════════════════════════════════════════════════════
st.markdown("---")
st.caption(
    "🔬 **POC Note:** This page uses mock data for 5 sample students. "
    "When ERP API/database integration is complete, this same UI will work with real student data. "
    "The main EduBot chat (for general FAQs) remains unchanged and works as usual."
)
