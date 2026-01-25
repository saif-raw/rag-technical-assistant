# backend/app/main.py
import os
from fastapi import UploadFile, File, HTTPException
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, RedirectResponse
from pydantic import BaseModel
from urllib.parse import unquote

from app.rag.ingest import save_uploaded_file, process_document
from app.rag.retriever import retrieve_context
from app.rag.generator import generate_answer, stream_answer
from app.services.s3 import generate_presigned_pdf_url

load_dotenv()

app = FastAPI(
    title="RAG Technical Assistant",
    description="Serverless RAG system for technical manuals",
    version="0.2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    file_path = save_uploaded_file(file)
    result = process_document(file_path)

    return {
        "message": "File uploaded and processed",
        "file_path": file_path,
        "pages": result["pages"],
        "chunks": result["chunks"]
    }


@app.post("/query")
def query_docs(req: QueryRequest):
    results = retrieve_context(req.query)
    return {"results": results}


@app.post("/ask")
def ask_question(req: QueryRequest):
    return generate_answer(req.query)


@app.post("/ask/stream")
async def ask_stream(payload: QueryRequest):
    def token_generator():
        for token in stream_answer(payload.query):
            yield token

    return StreamingResponse(
        token_generator(),
        media_type="text/plain; charset=utf-8",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )


# PDF endpoint that redirects to presigned S3 URL
@app.get("/pdf/{file_name}")
def serve_pdf(file_name: str, page: int = 1):
    """
    Redirect to S3 presigned PDF URL
    """
    try:
        file_name = unquote(file_name)
        presigned_url = generate_presigned_pdf_url(file_name, page)
        return RedirectResponse(presigned_url)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"PDF not found: {e}")
