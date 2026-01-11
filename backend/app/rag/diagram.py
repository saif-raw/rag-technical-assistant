# backend/app/rag/diagram.py
import pdfplumber
import pytesseract
from PIL import Image
import io
import os
from app.services.bedrock import invoke_llm

# Config
TESSERACT_DIR = r"C:\Repo\rag-technical-assistant\tesseract-portable"
TESSERACT_EXE = os.path.join(TESSERACT_DIR, "tesseract.exe")
pytesseract.pytesseract.tesseract_cmd = TESSERACT_EXE
os.environ["TESSDATA_PREFIX"] = os.path.join(TESSERACT_DIR, "tessdata")

def extract_and_describe_diagrams(pdf_path: str):
    diagram_chunks = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_index, page in enumerate(pdf.pages):
            pdf_page = page_index + 1

            page_descriptions = []

            # VECTOR LAYER
            vectors = page.curves + page.lines + page.rects
            if vectors:
                try:
                    x0 = min(float(v["x0"]) for v in vectors)
                    top = min(float(v["top"]) for v in vectors)
                    x1 = max(float(v["x1"]) for v in vectors)
                    bottom = max(float(v["bottom"]) for v in vectors)

                    if (x1 - x0) > 100 and (bottom - top) > 100:
                        img = page.crop((x0, top, x1, bottom)).to_image(300).original
                        ocr = pytesseract.image_to_string(img).strip()
                        page_descriptions.append(
                            process_with_ai(img, ocr, "Vector Diagram")
                        )
                except Exception:
                    pass

            # IMAGE LAYER
            for img in page.images:
                if img["width"] < 100 or img["height"] < 100:
                    continue
                try:
                    cropped = page.crop((img["x0"], img["top"], img["x1"], img["bottom"]))
                    pil = cropped.to_image(300).original
                    ocr = pytesseract.image_to_string(pil).strip()
                    page_descriptions.append(
                        process_with_ai(pil, ocr, "Embedded Diagram")
                    )
                except Exception:
                    pass

            for desc in dict.fromkeys(page_descriptions):
                diagram_chunks.append({
                    "content": desc,
                    "pdf_page": pdf_page
                })

    return diagram_chunks


def process_with_ai(pil_image, ocr_text, diag_type):
    """
    Helper to send context to Bedrock.
    """
    prompt = f"""
You are an expert engineering consultant. Analyze this {diag_type} extracted from a manual.
Describe:
- Components and layout
- Flows, relationships, or mechanical movements
- The core engineering principle or data trend shown

OCR Text detected in diagram:
{ocr_text if ocr_text else "No text detected."}
""".strip()
    
    return invoke_llm(prompt)