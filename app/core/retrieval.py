from fastapi import HTTPException
from .embeddings import create_embeddings
from .vector_db import client, collection_name
from .models import Document, Chunk
from sqlalchemy.orm import Session
from qdrant_client.models import Filter
from uuid import UUID
from typing import List, Dict


def search_documents(query:str, top_k: int = 5, db: Session= None):
    try:
        #Generate query embedding
        query_embedding = create_embeddings([query])[0]
        if len(query_embedding) != 384:
            raise HTTPException(
                status_code=500,
                detail=f"Query vector size mismatch: expected 384, got {len(query_embedding)}"
            )

        #Search in qdrant
        hits = client.search(
            collection_name=collection_name,
            query_vector = query_embedding,
            limit=top_k
            # query_filter=Filter(must=[])
        )
        if not hits:
            return []

        # Extracting Qdrant Point ids    
        qdrant_ids = [str(i.id) for i in hits]

        #Fetching chunk row in postgres database
        by_qid = {}
        if db:
            rows = db.query(Chunk).filter(Chunk.qdrant_point_id.in_([UUID(x) for x in qdrant_ids])).all()      
            by_qid = {str(r.qdrant_point_id): r for r in rows}

        results: List[Dict] = []
        for h in hits:
            qdrant_id = str(h.id)
            chunk = by_qid.get(qdrant_id) if db else None

            if chunk:
                document: Document = chunk.document
                results.append({
                    "score": h.score,
                    "qdrant_id": qdrant_id,
                    "text": chunk.text_content,
                    "chunk_id": chunk.chunk_id,
                    "chunk_length": chunk.chunk_length,
                    "document": {
                        "id": str(document.id),
                        "filename": document.filename,
                        "file_type": document.file_type,
                        "chunking_strategy": document.chunking_strategy,
                        "embedding_model": document.embedding_model
                    }
                })
            else:
                results.append({
                    "score": h.score,
                    "qdrant_id": qdrant_id,
                    "text": None,
                    "chunk_index": None,
                    "chunk_length": None,
                    "document": None
                })

        return results
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in search : {str(e)}")
