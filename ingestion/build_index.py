"""
DPU EduBot — Build FAISS Index from knowledge_base.json
Run this once after setup: python ingestion/build_index.py
"""

import json
import os
import sys
import pickle
import numpy as np

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
EMBED_MODEL = "text-embedding-3-small"
INDEX_PATH = "data/faiss_index/index.faiss"
CHUNKS_PATH = "data/faiss_index/chunks.pkl"
KB_PATH = "data/knowledge_base.json"


def embed_text(text: str) -> np.ndarray:
    """Get embedding vector for a text string."""
    res = client.embeddings.create(input=[text], model=EMBED_MODEL)
    return np.array(res.data[0].embedding, dtype="float32")


def build_chunks_from_kb(kb: dict) -> list:
    """Convert knowledge base JSON into flat list of text chunks."""
    chunks = []

    # ── Layer 1: All FAQs ──────────────────────────────────────────
    print("  Processing Layer 1 FAQs...")
    for cat_key, cat_data in kb["layer_1_faqs"].items():
        for faq in cat_data["faqs"]:
            text = f"Q: {faq['q']}\nA: {faq['a']}"
            chunks.append({
                "text": text,
                "source": "DPU Official FAQ",
                "category": cat_key,
                "category_label": cat_data["label"],
                "batch_id": "all",
                "layer": "layer_1",
                "tags": faq.get("tags", [])
            })

    # ── Layer 2: Batch-specific data ───────────────────────────────
    print("  Processing Layer 2 Batch data...")
    for batch_id, batch in kb["layer_2_batch_specific"].items():
        label = batch["label"]

        # Subjects
        valid_subjects = [
            s for s in batch["subjects"]
            if "TBD" not in s["code"] and "ADMIN" not in s["code"]
        ]
        if valid_subjects:
            subj_list = ", ".join([f"{s['code']} - {s['name']}" for s in valid_subjects])
            chunks.append({
                "text": f"Subjects for {label} (Semester {batch['semester']}): {subj_list}",
                "source": label,
                "category": "subjects",
                "batch_id": batch_id,
                "layer": "layer_2",
                "tags": ["subjects", "courses", "sem1"]
            })

        # Fee structure
        fees = batch.get("fee_structure", {})
        if "sem1" in fees:
            fee_text = (
                f"Fee structure for {label}: "
                f"Semester 1 = Rs {fees['sem1']:,} | "
                f"Semester 2 = Rs {fees['sem2']:,} | "
                f"Semester 3 = Rs {fees['sem3']:,} | "
                f"Semester 4 = Rs {fees['sem4']:,} | "
                f"Total program fee = Rs {fees['total']:,}. {fees.get('note','')}"
            )
            chunks.append({
                "text": fee_text,
                "source": label,
                "category": "fees",
                "batch_id": batch_id,
                "layer": "layer_2",
                "tags": ["fees", "fee structure", "amount"]
            })

        # Important dates
        dates = batch.get("important_dates", {})
        date_parts = []
        for k, v in dates.items():
            if k != "note" and v and "TBD" not in str(v) and "ADMIN" not in str(v):
                date_parts.append(f"{k.replace('_', ' ')}: {v}")
        if date_parts:
            date_text = f"Key dates for {label}: " + " | ".join(date_parts)
            chunks.append({
                "text": date_text,
                "source": label,
                "category": "dates",
                "batch_id": batch_id,
                "layer": "layer_2",
                "tags": ["dates", "calendar", "schedule", "exam dates"]
            })

        # Specializations
        specs = batch.get("specializations", [])
        if specs:
            spec_text = (
                f"Specializations available for {label}: "
                + ", ".join(specs)
            )
            chunks.append({
                "text": spec_text,
                "source": label,
                "category": "specializations",
                "batch_id": batch_id,
                "layer": "layer_2",
                "tags": ["specialization", "options"]
            })

        # ERP Links
        erp = batch.get("erp_links", {})
        if erp:
            erp_text = (
                f"ERP portal links for {label}: "
                f"Assignments: {erp.get('assignments','')} | "
                f"Payments: {erp.get('payments','')} | "
                f"Examination: {erp.get('examination','')} | "
                f"Support Ticket: {erp.get('support_ticket','')} | "
                f"LMS: {erp.get('lms','')}"
            )
            chunks.append({
                "text": erp_text,
                "source": label,
                "category": "erp_links",
                "batch_id": batch_id,
                "layer": "layer_2",
                "tags": ["links", "erp portal", "url"]
            })

    # ── Support ticket taxonomy ────────────────────────────────────
    print("  Processing Support Ticket Taxonomy...")
    for category, subtypes in kb["support_ticket_taxonomy"].items():
        for subtype in subtypes:
            text = (
                f"To raise a support ticket for '{subtype}': "
                f"Go to ERP — Student Support Ticket — "
                f"Support Category: {category} — "
                f"Nature of Support: {subtype}"
            )
            chunks.append({
                "text": text,
                "source": "DPU ERP Support System",
                "category": "support_ticket",
                "batch_id": "all",
                "layer": "layer_1",
                "tags": ["ticket", category.lower(), subtype.lower()]
            })

    # ── Layer 3: Website topics ────────────────────────────────────
    print("  Processing Layer 3 Website data...")
    for topic in kb["layer_3_website"]["key_topics"]:
        chunks.append({
            "text": topic,
            "source": "dypatilonline.com",
            "category": "website",
            "batch_id": "all",
            "layer": "layer_3",
            "tags": ["website", "general", "program info"]
        })

    return chunks


def build_index():
    """Main function to build and save the FAISS index."""
    try:
        import faiss
    except ImportError:
        print("ERROR: faiss-cpu not installed. Run: pip install faiss-cpu")
        return 0

    print("\n🔨 Building DPU EduBot FAISS index...")

    # Load knowledge base
    with open(KB_PATH, encoding="utf-8") as f:
        kb = json.load(f)

    # Build chunks
    chunks = build_chunks_from_kb(kb)
    print(f"\n  Total chunks to embed: {len(chunks)}")

    # Embed all chunks
    print("\n  Embedding chunks (this may take 1-2 minutes)...")
    vectors = []
    for i, chunk in enumerate(chunks):
        vec = embed_text(chunk["text"])
        vectors.append(vec)
        if (i + 1) % 10 == 0 or (i + 1) == len(chunks):
            print(f"  Progress: {i+1}/{len(chunks)} chunks embedded")

    # Build and save FAISS index
    vectors_np = np.array(vectors, dtype="float32")
    faiss.normalize_L2(vectors_np)

    dim = vectors_np.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(vectors_np)

    os.makedirs("data/faiss_index", exist_ok=True)
    faiss.write_index(index, INDEX_PATH)
    with open(CHUNKS_PATH, "wb") as f:
        pickle.dump(chunks, f)

    print(f"\n✅ Index built successfully!")
    print(f"   Chunks indexed: {len(chunks)}")
    print(f"   Index saved to: {INDEX_PATH}")
    print(f"   Chunks saved to: {CHUNKS_PATH}")
    return len(chunks)


if __name__ == "__main__":
    count = build_index()
    if count > 0:
        print(f"\n🎓 DPU EduBot is ready with {count} knowledge chunks!")
        print("   Run the app: streamlit run app/main.py")
