# backend/app/main.py

import os

from fastapi import UploadFile, File
from app.rag.ingest import save_uploaded_file
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI(
    title="RAG Technical Assistant",
    description="Serverless RAG system for technical manuals",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    file_path = save_uploaded_file(file)
    return {
        "message": "File uploaded successfully",
        "path": file_path
    }