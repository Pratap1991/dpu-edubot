"""
DPU EduBot — Batch Knowledge Management
Admin-uploaded CSVs (Session Schedule, Exam Timetable) scoped to one batch.

Checked between Layer 0 (ERP) and the existing FAQ/Website RAG pipeline:
    ERP  ->  Batch Knowledge (this module)  ->  FAQ  ->  Website

Fully self-contained: does not modify rag/pipeline.py, knowledge_base.json,
or the FAISS index. If no trigger matches, check_batch_knowledge() returns
None and the caller falls through to the existing pipeline unchanged.
"""

import os
import csv
import io

BATCH_KNOWLEDGE_DIR = "data/batch_knowledge"

DOC_TYPES = {
    "session_schedule": {
        "label": "Session Schedule",
        "required_columns": [
            "Program", "Batch", "Semester", "Academic_Year", "Document_Type", "Version",
            "Effective_From", "Effective_To", "Date", "Day", "Course_Code", "Subject",
            "Start_Time", "End_Time", "Session_Mode", "Faculty", "LMS_Link", "Remarks", "Status",
        ],
        "display_columns": ["Date", "Day", "Course_Code", "Subject", "Start_Time", "End_Time",
                             "Session_Mode", "Faculty", "LMS_Link", "Remarks", "Status"],
    },
    "exam_timetable": {
        "label": "Exam Timetable",
        "required_columns": [
            "Program", "Batch", "Semester", "Academic_Year", "Document_Type", "Version",
            "Exam_Type", "Date", "Day", "Course_Code", "Subject", "Start_Time", "End_Time",
            "Duration", "Mode", "Venue", "Instructions", "Status",
        ],
        "display_columns": ["Date", "Day", "Course_Code", "Subject", "Start_Time", "End_Time",
                             "Duration", "Mode", "Venue", "Exam_Type", "Instructions", "Status"],
    },
}

# Checked in this order — exam-specific phrases first, since "exam timetable"
# also contains the word "timetable" which would otherwise match SESSION_TRIGGERS.
EXAM_TRIGGERS = [
    "exam timetable", "exam time table", "exam schedule", "exam dates", "exam date",
    "when is my exam", "exam day", "exam timing",
]
SESSION_TRIGGERS = [
    "session schedule", "class schedule", "lecture schedule", "timetable",
    "lectures", "lecture", "live session", "live class", "when is my class", "class timing",
]
# "subjects" already has a working answer today via the existing Layer 2 FAISS
# data — only take over once a CSV has actually been uploaded (see check_batch_knowledge).
SUBJECT_TRIGGERS = ["subjects", "subject list", "which subjects", "my subjects", "list of subjects"]


def _batch_dir(batch_id: str) -> str:
    return os.path.join(BATCH_KNOWLEDGE_DIR, batch_id)


def _csv_path(batch_id: str, doc_type: str) -> str:
    return os.path.join(_batch_dir(batch_id), f"{doc_type}.csv")


def validate_csv_columns(doc_type: str, header: list) -> list:
    """Return the list of required columns missing from `header` (empty = valid)."""
    required = DOC_TYPES[doc_type]["required_columns"]
    header = header or []
    return [c for c in required if c not in header]


def save_batch_csv(batch_id: str, doc_type: str, file_obj) -> int:
    """Validate and persist an uploaded CSV. Raises ValueError on schema mismatch
    or an empty file. Returns the number of data rows saved."""
    raw = file_obj.read()
    text = raw.decode("utf-8-sig") if isinstance(raw, bytes) else raw

    reader = csv.DictReader(io.StringIO(text))
    missing = validate_csv_columns(doc_type, reader.fieldnames)
    if missing:
        raise ValueError(f"Missing required column(s): {', '.join(missing)}")

    rows = list(reader)
    if not rows:
        raise ValueError("CSV has no data rows.")

    os.makedirs(_batch_dir(batch_id), exist_ok=True)
    with open(_csv_path(batch_id, doc_type), "w", encoding="utf-8", newline="") as f:
        f.write(text)
    return len(rows)


def load_batch_csv(batch_id: str, doc_type: str):
    """Return the CSV rows as a list of dicts, or None if nothing's been uploaded yet."""
    path = _csv_path(batch_id, doc_type)
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def uploaded_status(batch_id: str) -> dict:
    """{'session_schedule': bool, 'exam_timetable': bool} — for the Admin status display."""
    return {dt: os.path.exists(_csv_path(batch_id, dt)) for dt in DOC_TYPES}


def _detect_doc_type(q: str):
    """Returns (doc_type, strict) or (None, False). strict=False means: if no
    CSV is uploaded, the caller should fall through to the existing pipeline
    instead of showing a 'not uploaded' message (preserves req. 6)."""
    if any(t in q for t in EXAM_TRIGGERS):
        return "exam_timetable", True
    if any(t in q for t in SESSION_TRIGGERS):
        return "session_schedule", True
    if any(t in q for t in SUBJECT_TRIGGERS):
        return "session_schedule", False
    return None, False


def _format_rows(rows: list, doc_type: str) -> str:
    cols = DOC_TYPES[doc_type]["display_columns"]
    lines = []
    for r in rows:
        line = " | ".join(f"{c}: {r.get(c, '')}" for c in cols if r.get(c))
        if line:
            lines.append(line)
    return "\n".join(lines)


def _generate_answer(query: str, rows: list, doc_type: str, batch_label: str, student_first_name) -> str:
    from rag.pipeline import client, CHAT_MODEL

    label = DOC_TYPES[doc_type]["label"]
    context = _format_rows(rows, doc_type)
    greeting_rule = f"Address the student as {student_first_name}. " if student_first_name else ""

    system_prompt = f"""You are DPU EduBot answering a {label} question for {batch_label}.

STRICT RULES:
1. Use ONLY the rows below. Never invent a date, time, subject, faculty name, or venue.
2. If what's specifically asked isn't present in these rows, say so plainly and suggest
   contacting the mentor or checking ERP — do not guess or approximate.
3. {greeting_rule}Be warm, concise, and helpful.
4. For multiple matching rows, use a short bullet list.
5. Do not mention that you are reading from a CSV, table, or file.

{label.upper()} DATA FOR {batch_label}:
{context}"""

    try:
        response = client.chat.completions.create(
            model=CHAT_MODEL,
            temperature=0.1,
            max_tokens=500,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query},
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error reaching OpenAI: {str(e)}"


def check_batch_knowledge(query: str, batch_id: str, batch_label: str, student_first_name: str = None):
    """Main entry point. Returns a result dict (same shape as rag.pipeline.answer())
    if this query is a batch-knowledge question, otherwise None."""
    q = query.lower().strip()
    doc_type, strict = _detect_doc_type(q)
    if doc_type is None:
        return None

    rows = load_batch_csv(batch_id, doc_type)
    label = DOC_TYPES[doc_type]["label"]

    if not rows:
        if not strict:
            return None
        return {
            "answer": (
                f"No {label.lower()} has been uploaded yet for {batch_label}. "
                "Please contact your mentor or check ERP for the latest schedule."
            ),
            "sources": [],
            "confidence": 1.0,
            "escalate": False,
            "is_redirect": False,
            "erp_link": None,
            "erp_label": None,
        }

    return {
        "answer": _generate_answer(query, rows, doc_type, batch_label, student_first_name),
        "sources": [f"{batch_label} – {label}"],
        "confidence": 1.0,
        "escalate": False,
        "is_redirect": False,
        "erp_link": None,
        "erp_label": None,
    }
