from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Document Ingestion Worker")

class DocPayload(BaseModel):
    source: str  # 'gdrive', 'notion'
    doc_id: str
    content: str
    permissions: list[str]

@app.post("/ingest/doc")
async def ingest_document(doc: DocPayload):
    """
    Ingests static documents.
    Extracts metadata for PostgreSQL and semantics for Qdrant.
    """
    # TODO: Chunking, embedding, inserting to Qdrant & Postgres
    return {"status": "queued_for_processing"}
