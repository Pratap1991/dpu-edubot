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
import re
from datetime import date, datetime, timedelta

from dateutil import parser as date_parser

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
    "next class", "next session",
]
# "subjects" already has a working answer today via the existing Layer 2 FAISS
# data — only take over once a CSV has actually been uploaded (see check_batch_knowledge).
SUBJECT_TRIGGERS = ["subjects", "subject list", "which subjects", "my subjects", "list of subjects"]


def _batch_dir(batch_id: str) -> str:
    return os.path.join(BATCH_KNOWLEDGE_DIR, batch_id)


def _csv_path(batch_id: str, doc_type: str) -> str:
    return os.path.join(_batch_dir(batch_id), f"{doc_type}.csv")


def _normalize_col(name: str) -> str:
    """Canonicalize a column name for comparison: strip BOM/whitespace, ignore
    case, treat spaces/hyphens as underscores (e.g. 'course code' == 'Course_Code')."""
    return (name or "").strip().lstrip("﻿").lower().replace(" ", "_").replace("-", "_")


def _detect_delimiter(sample: str) -> str:
    """Excel saves CSV with ';' instead of ',' on some regional locales — sniff
    it instead of assuming comma, so a correctly-shaped export isn't rejected."""
    try:
        return csv.Sniffer().sniff(sample, delimiters=",;\t").delimiter
    except Exception:
        return ","


def validate_csv_columns(doc_type: str, header: list) -> list:
    """Return the list of required columns missing from `header` (empty = valid).
    Comparison is whitespace/case/underscore-vs-space tolerant."""
    required = DOC_TYPES[doc_type]["required_columns"]
    normalized_header = {_normalize_col(h) for h in (header or [])}
    return [c for c in required if _normalize_col(c) not in normalized_header]


def save_batch_csv(batch_id: str, doc_type: str, file_obj) -> int:
    """Validate and persist an uploaded CSV. Raises ValueError (with the columns
    actually found, for diagnosis) on schema mismatch or an empty file. Rewrites
    the file with canonical column names/order so downstream code can always
    rely on the exact required_columns names regardless of source formatting.
    Returns the number of data rows saved."""
    raw = file_obj.read()
    text = raw.decode("utf-8-sig") if isinstance(raw, bytes) else raw
    text = text.lstrip("﻿")

    delimiter = _detect_delimiter(text[:2000])
    reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)
    header = [h.strip() for h in (reader.fieldnames or []) if h]

    missing = validate_csv_columns(doc_type, header)
    if missing:
        found = ", ".join(header) if header else "(none — the file may be empty or use an unrecognized format)"
        raise ValueError(f"Missing required column(s): {', '.join(missing)}. Columns found in your file: {found}")

    rows = list(reader)
    if not rows:
        raise ValueError("CSV has no data rows.")

    required = DOC_TYPES[doc_type]["required_columns"]
    norm_to_actual = {_normalize_col(h): h for h in header}
    canonical_rows = [
        {col: row.get(norm_to_actual.get(_normalize_col(col), col), "") for col in required}
        for row in rows
    ]

    os.makedirs(_batch_dir(batch_id), exist_ok=True)
    with open(_csv_path(batch_id, doc_type), "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=required)
        writer.writeheader()
        writer.writerows(canonical_rows)
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


# ── Session Schedule date engine ────────────────────────────────────
# A session_schedule row is a WEEKLY recurring class (same weekday/time,
# every week from Effective_From to Effective_To) — not a one-off event on
# its literal Date value. "When is my next lecture" needs real date
# arithmetic, not an LLM guessing from a single sample date, so this is
# computed deterministically in Python and never passed through the LLM.

WEEKDAY_INDEX = {"monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
                  "friday": 4, "saturday": 5, "sunday": 6}

_DATE_HINT_RE = re.compile(
    r"\b(jan|january|feb|february|mar|march|apr|april|may|jun|june|jul|july|aug|august|"
    r"sep|sept|september|oct|october|nov|november|dec|december)\b"
    r"|\d{1,2}[-/]\d{1,2}([-/]\d{2,4})?"
    r"|\d{4}-\d{2}-\d{2}",
    re.IGNORECASE,
)

DATE_INTENT_TRIGGERS = ["today", "tomorrow", "yesterday", "next lecture",
                         "next class", "next session", "upcoming"]


def _is_date_computable(q: str) -> bool:
    """Whether this session_schedule query needs real date arithmetic
    (vs. a broad 'show me my whole schedule' style question)."""
    if any(t in q for t in DATE_INTENT_TRIGGERS):
        return True
    if "next" in q and any(t in q for t in ["lecture", "class", "session"]):
        return True
    return bool(_DATE_HINT_RE.search(q))


def _parse_flexible_date(value: str):
    """Parse a date string in whatever format the admin's CSV uses
    (ISO, DD-M-YY, DD/MM/YYYY, ...). Returns a datetime.date or None."""
    if not value or not value.strip():
        return None
    try:
        return date_parser.parse(value.strip(), dayfirst=True).date()
    except Exception:
        return None


def _parse_flexible_time(value: str):
    """Parse a time-of-day string for sorting purposes. Returns datetime.time or None."""
    if not value or not value.strip():
        return None
    try:
        return date_parser.parse(value.strip()).time()
    except Exception:
        return None


def _extract_reference_date(query: str, year_anchor: date):
    """Figure out what date the student means by 'today' in this message.
    year_anchor supplies the year/context for a bare phrase like '25th feb'
    (the batch's own term, not necessarily the real current year).

    An explicit date always anchors first (e.g. "today is 23-01-2026, what's
    tomorrow's lecture?" -> anchor=23 Jan, tomorrow=24 Jan) — 'tomorrow' /
    'yesterday' are only relative to the real current date when no explicit
    date was also given."""
    q = query.lower()
    real_today = date.today()
    anchor = None

    if _DATE_HINT_RE.search(q):
        try:
            default_dt = datetime(year_anchor.year, real_today.month, real_today.day)
            anchor = date_parser.parse(query, fuzzy=True, default=default_dt, dayfirst=True).date()
        except Exception:
            anchor = None

    base = anchor if anchor is not None else real_today

    if "tomorrow" in q:
        return base + timedelta(days=1)
    if "yesterday" in q:
        return base - timedelta(days=1)

    return base


def _next_occurrence(ref_date: date, weekday_name: str, effective_from, effective_to):
    """Smallest date >= ref_date (clipped to the term start) that falls on
    weekday_name and is still within [effective_from, effective_to]. None if
    there's no such occurrence left in the term."""
    wd = WEEKDAY_INDEX.get((weekday_name or "").strip().lower())
    if wd is None or effective_from is None or effective_to is None:
        return None
    start = max(ref_date, effective_from)
    occurrence = start + timedelta(days=(wd - start.weekday()) % 7)
    if occurrence > effective_to:
        return None
    return occurrence


def _format_single_session(occ_date: date, row: dict, student_first_name) -> str:
    greeting = f"Hi {student_first_name}! " if student_first_name else ""
    return (
        f"{greeting}Your next session is:\n\n"
        f"- **Subject:** {row.get('Subject', '')} ({row.get('Course_Code', '')})\n"
        f"- **Date:** {occ_date.strftime('%A, %d %b %Y')}\n"
        f"- **Time:** {row.get('Start_Time', '')} – {row.get('End_Time', '')}\n"
        f"- **Mode:** {row.get('Session_Mode', '')}"
    )


def _answer_session_schedule_date_query(query: str, rows: list, batch_label: str, student_first_name):
    """Deterministic (no LLM call) answer for date-aware session schedule
    questions — 'today', 'tomorrow', 'next lecture', or an explicit date."""
    q = query.lower()
    greeting = f"Hi {student_first_name}! " if student_first_name else ""

    anchors = [d for d in (_parse_flexible_date(r.get("Effective_From", "")) for r in rows) if d]
    year_anchor = anchors[0] if anchors else date.today()
    ref_date = _extract_reference_date(query, year_anchor)

    wants_next = "next" in q or "upcoming" in q

    if wants_next:
        candidates = []
        for r in rows:
            ef = _parse_flexible_date(r.get("Effective_From", ""))
            et = _parse_flexible_date(r.get("Effective_To", ""))
            occ = _next_occurrence(ref_date, r.get("Day", ""), ef, et)
            if occ:
                candidates.append((occ, _parse_flexible_time(r.get("Start_Time", "")) or datetime.max.time(), r))
        if not candidates:
            return (f"{greeting}I couldn't find any upcoming sessions in the uploaded schedule for "
                     f"{batch_label} on or after {ref_date.strftime('%d %b %Y')}. "
                     "Please contact your mentor or check ERP.")
        candidates.sort(key=lambda c: (c[0], c[1]))
        occ_date, _, row = candidates[0]
        return _format_single_session(occ_date, row, student_first_name)

    # "today" / "tomorrow" / "yesterday" / an explicit date -> what's on that date
    matches = []
    for r in rows:
        ef = _parse_flexible_date(r.get("Effective_From", ""))
        et = _parse_flexible_date(r.get("Effective_To", ""))
        wd = WEEKDAY_INDEX.get((r.get("Day", "") or "").strip().lower())
        if ef and et and wd is not None and ef <= ref_date <= et and ref_date.weekday() == wd:
            matches.append(r)

    if not matches:
        return (f"{greeting}There's no session scheduled on {ref_date.strftime('%A, %d %b %Y')} for "
                 f"{batch_label} based on the uploaded schedule. Please check ERP or contact your mentor.")

    matches.sort(key=lambda r: _parse_flexible_time(r.get("Start_Time", "")) or datetime.max.time())
    if len(matches) == 1:
        return _format_single_session(ref_date, matches[0], student_first_name)

    lines = "\n".join(
        f"- **{r.get('Subject', '')}** ({r.get('Course_Code', '')}): "
        f"{r.get('Start_Time', '')} – {r.get('End_Time', '')}, {r.get('Session_Mode', '')}"
        for r in matches
    )
    return f"{greeting}Here's what's scheduled on {ref_date.strftime('%A, %d %b %Y')}:\n\n{lines}"


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

    if doc_type == "session_schedule" and _is_date_computable(q):
        answer_text = _answer_session_schedule_date_query(query, rows, batch_label, student_first_name)
    else:
        answer_text = _generate_answer(query, rows, doc_type, batch_label, student_first_name)

    return {
        "answer": answer_text,
        "sources": [f"{batch_label} – {label}"],
        "confidence": 1.0,
        "escalate": False,
        "is_redirect": False,
        "erp_link": None,
        "erp_label": None,
    }
