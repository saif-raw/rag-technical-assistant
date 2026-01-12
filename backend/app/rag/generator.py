# backend/app/rag/generator.py
from app.services.bedrock import invoke_llm, stream_llm
from app.rag.retriever import retrieve_context
from app.services.s3 import generate_presigned_pdf_url

def _build_prompt(question: str, chunks: list) -> str:
    """
    Deterministic RAG prompt.
    The LLM NEVER outputs filenames or URLs.
    """

    context_blocks = []

    for idx, c in enumerate(chunks, start=1):
        context_blocks.append(
            f"""
[CITATION_{idx}]
TYPE: {c['source_type']}
FILE_NAME: {c['file_name']}
PDF_PAGE: {c['pdf_page']}

CONTENT:
{c['content'][:800]}
""".strip()
        )

    context = "\n\n".join(context_blocks)

    return f"""
You are the Chief Mechanical Engineer and Technical Authority.

You must answer the question using ONLY the provided manual excerpts.
You must NOT use outside knowledge.
You must NOT invent information.

====================
FORMATTING RULES (MANDATORY)
==================== 
- The response MUST be valid GitHub-Flavored Markdown. 
- ALL section titles MUST start with "##". 
- ALL lists MUST use "-" bullet points. 
- Do NOT write plain paragraphs without Markdown structure.

====================
CRITICAL OUTPUT RULES (NON-NEGOTIABLE)
====================
- Do NOT write paragraphs longer than 3 sentences.
- Do NOT group citations.
- Do NOT place citations at the end of sections.

====================
CITATION FORMAT (STRICT)
====================
- Citations MUST be Markdown URL.
- Citations MUST follow this EXACT format:
    (Source: CITATION_N, Page: <PDF_PAGE>)
- CITATION_N is a placeholder and will be resolved by the system.
- Do NOT alter the citation structure.
- Do NOT place citations at the end of sections or answers.
- Citations MUST be inline Markdown links using the filename as the text.

- Do NOT wrap it in brackets or parentheses yourself; the system will do that.
- Use the CITATION_N that corresponds to the correct manual excerpt.

====================
DIAGRAM RULES (STRICT)
====================
- If a source has TYPE: diagram and you use its information:
  - You MUST explicitly say the word "diagram or figure".
  - You MUST describe what the diagram shows.
  - Example sentence structure:

    "You can refer to the diagram that illustrates <what it shows>."

- Diagram sentences MUST be cited using the diagram's CITATION_<N>.
- Do NOT cite diagrams unless they are clearly relevant.

====================
SECTION STRUCTURE
====================
- Use "##" for section titles.
- Use "-" for lists.
- Do NOT write free-form paragraphs.

====================
PROVIDED MANUAL EXCERPTS
====================
{context}

====================
USER QUESTION
====================
{question}

====================
ANSWER
====================
""".strip()



def resolve_citations(answer: str, citations: list) -> str:
    """
    Resolve citation placeholders into clickable filenames.
    Safely handles both 'index' and 'id' keys.
    """
    for c in citations:
        # Use .get() to avoid KeyError if 'index' is missing
        idx = c.get('index') or c.get('id', '').replace('CITATION_', '')
        placeholder = f"CITATION_{idx}"
        
        # Enterprise-grade formatting
        rendered = f"[{c['file_name']}](<{c['url']}>)"
        
        # Replace the placeholder in the text
        answer = answer.replace(placeholder, rendered)

    return answer

def generate_answer(question: str):
    chunks = retrieve_context(question)
    prompt = _build_prompt(question, chunks)
    raw_answer = invoke_llm(prompt)

    citations = []
    for i, c in enumerate(chunks):
        citations.append({
            "index": i + 1,
            "id": f"CITATION_{i+1}",
            "file_name": c["file_name"],
            "page": c["pdf_page"],
            "url": generate_presigned_pdf_url(c["file_name"], c["pdf_page"])
        })

    final_answer = resolve_citations(raw_answer, citations)

    return {
        "answer": final_answer,
        "citations": citations
    }



def stream_answer(question: str):
    chunks = retrieve_context(question)
    prompt = _build_prompt(question, chunks)

    buffer = ""
    # We collect the full response to resolve citations before sending
    # (Note: For true token-by-token streaming with citations, 
    # we'd need a different approach, but this fix gets you running NOW)
    for token in stream_llm(prompt):
        buffer += token

    citations = []
    for i, c in enumerate(chunks):  
        citations.append({
            "index": i + 1, # Added the missing index key here
            "id": f"CITATION_{i+1}",
            "file_name": c["file_name"],
            "page": c["pdf_page"],
            "source_type": c["source_type"],
            "url": generate_presigned_pdf_url(c["file_name"], c["pdf_page"])
        })

    final_answer = resolve_citations(buffer, citations)
    
    # Append the citation metadata so the frontend can show the 'Verified Sources' section
    import json
    payload = f"{final_answer}\n\n<<CITATIONS>>\n{json.dumps({'citations': citations})}"
    
    yield payload