import re
import os
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings


def _parse_fys(text: str):
    """Extract FY2024 and FY2023 numbers from a chunk string."""
    # Matches: FY2024: 12345.67 or FY2023: -1,234
    fy24 = re.search(r"FY\s*2024\s*:\s*(-?\d[\d,]*\.?\d*)", text, re.I)
    fy23 = re.search(r"FY\s*2023\s*:\s*(-?\d[\d,]*\.?\d*)", text, re.I)
    to_float = lambda m: float(m.group(1).replace(",", "")) if m else None
    return to_float(fy24), to_float(fy23)


def rag_lookup(company: str, statement_type: str, query: str, k: int = 3):
    """
    Vector search for a given canonical query (line_item) and parse FY values.
    Returns: {"line_item": <canonical>, "fy_2024": <num>, "fy_2023": <num>} or None
    """
    load_dotenv(dotenv_path="../.env")
    openai_key = os.getenv("OPENAI_API_KEY")
    embeddings = OpenAIEmbeddings(openai_api_key=openai_key)

    vectorstore = FAISS.load_local(
        ".",
        embeddings,
        allow_dangerous_deserialization=True,
    )

    search = f"{company} {statement_type} {query}"
    results = vectorstore.similarity_search(search, k=k)

    if not results:
        return None

    # Take first hit and parse
    for doc in results:
        parts = [p.strip() for p in doc.page_content.split("|")]
        if len(parts) < 4:
            continue

        line_item = parts[2]  # "Total current assets"
        values = parts[3]     # "FY24 = 89432.0, FY23 = 70881.0"

        # parse numbers safely
        fy24 = None
        fy23 = None
        try:
            for seg in values.split(","):
                seg = seg.strip()
                if seg.startswith("FY24"):
                    fy24 = float(seg.split("=")[1].strip())
                elif seg.startswith("FY23"):
                    fy23 = float(seg.split("=")[1].strip())
        except Exception:
            pass

        return {
            "line_item": query,           # canonical for downstream KPIs
            "matched_line_item": line_item,  # actual chunk text (optional, for debugging)
            "fy_2024": fy24,
            "fy_2023": fy23,
        }

    return None
