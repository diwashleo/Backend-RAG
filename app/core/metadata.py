from fastapi import HTTPException
from .models import Document, Chunk

def store_metadata_in_postgres(filename: str, file_type: str, file_size: int, chunking_strategy: str, chunks: list, point_ids: list, db):
    """Store document and chunk metadata in PostgreSQL"""
    try:
        # Store document metadata
        document = Document(
            filename=filename,
            file_type=file_type,
            file_size=file_size,
            chunking_strategy=chunking_strategy,
            total_chunks=len(chunks),
            embedding_model="sentence-transformers/all-MiniLM-L6-v2"
        )
        db.add(document)
        db.commit()
        db.refresh(document)


        #Store chunk metadata
        for i, (chunk, point_id) in enumerate(zip(chunks, point_ids)):
            chunk_record = Chunk(
                document_id=document.id,
                chunk_id=i,
                qdrant_point_id=point_id,
                text_content=chunk,
                chunk_length=len(chunk)
            )
            db.add(chunk_record)
        db.commit()
        return document.id
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error storing metadata in PostgreSQL: {str(e)}")