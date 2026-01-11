# backend/app/rag/test_diagrams.py
import os
from app.rag.diagram import extract_and_describe_diagrams

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
PDF_PATH = os.path.join(BASE_DIR, "data", "uploads", "DOE_MaterialScience_1.pdf")

if __name__ == "__main__":
    # Safety check to tell you exactly where it is looking
    if not os.path.exists(PDF_PATH):
        print(f"❌ ERROR: File not found at {PDF_PATH}")
    else:
        results = extract_and_describe_diagrams(PDF_PATH)

        print("\n=== DIAGRAM EXTRACTION RESULTS ===\n")

        for page, description in results.items():
            print(f"\n--- PDF PAGE {page} ---\n")
            print(description[:1500])
            print("\n------------------------\n")