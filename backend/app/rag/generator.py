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
- Do NOT group citations.
- Write factual paragraphs ONLY based on the provided excerpts.
- EVERY fact MUST be backed by a citation.
- If the LLM reads a diagram or figure, it MUST explicitly say "diagram or figure" and describe what it shows.

====================
CITATION FORMAT (STRICT)
====================
- Citations MUST follow this EXACT format: (Source: CITATION_N, Page: <PDF_PAGE>)
- Example: "The motor requires 5W-30 oil (Source: CITATION_1, Page: 15)."
- Do NOT attempt to write URLs. Use the CITATION_N placeholder only.

====================
ABSTENTION RULE (MANDATORY)
====================
- If the provided excerpts do NOT contain sufficient information to answer a part of the question:
  - You MUST explicitly say: "The provided manuals do not contain information about this topic."
  - You MUST provide some general knowledge stating clearly "However, I can give you some general information".
  - You MUST NOT include citations for that part.
  - If the entire question cannot be answered, you MUST NOT include any fabricated information, citations, or even verified sources


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
    for c in citations:
        idx = c["index"]
        page = c["page"]
        file_name = c["file_name"]

        presigned_url = generate_presigned_pdf_url(
            file_name=file_name,
            page=page
        )

        target = f"(Source: CITATION_{idx}, Page: {page})"

        replacement = (
            f"(Source: "
            f"[{file_name}]({presigned_url}), "
            f"Page: {page})"
        )

        answer = answer.replace(target, replacement)

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
    for token in stream_llm(prompt):
        buffer += token

    citations = []
    for i, c in enumerate(chunks):  
        citations.append({
            "index": i + 1,
            "id": f"CITATION_{i+1}",
            "file_name": c["file_name"],
            "page": c["pdf_page"],
            "source_type": c["source_type"],
        })

    final_answer = resolve_citations(buffer, citations)
    
    # Append the citation metadata so the frontend can show the 'Verified Sources' section
    import json
    payload = f"{final_answer}\n\n<<CITATIONS>>\n{json.dumps({'citations': citations})}"
    
    yield payload