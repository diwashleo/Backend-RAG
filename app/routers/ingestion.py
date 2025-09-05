from fastapi import UploadFile, HTTPException, Form, APIRouter, Depends
from pathlib import Path
from enum import Enum
from core.extraction import extract_text_from_pdf, extract_text_from_txt
from core.chunking import fixed_chunking, recursive_chunking
from core.embeddings import create_embeddings
from core.vector_db import store_in_qdrant
from core.metadata import store_metadata_in_postgres
from core.db import get_db, SessionLocal

router = APIRouter()

#Allowed File Types
ALLOWED_EXTENSIONS = {".pdf", ".txt"}

class ChunkingStrategy(str, Enum):
    fixed = "fixed"
    recursive = "recursive"

@router.post("/")
async def upload_file(
    uploaded_file: UploadFile,
    chunking_strategy: ChunkingStrategy = Form(description="Choose chunking strategy"),
    db: SessionLocal = Depends(get_db)
):
    chunk_size = 800
    chunk_overlap = 200

    #Validata Chunking strategy
    if chunking_strategy not in ["fixed", "recursive"]:
        raise HTTPException(
            status_code=400,
            detail="chunking_strategy must be either 'fixed' or 'recursive'"
        )

    # Validate file extension
    file_extension = Path(uploaded_file.filename).suffix.lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Only {', '.join(ALLOWED_EXTENSIONS)} files are accepted."
        )
    
    #Reading content from uploaded documents
    file_content = await uploaded_file.read()

    try:
        #Extracting content from file content
        if file_extension == ".pdf":
            text_content = extract_text_from_pdf(file_content)
        elif file_extension == ".txt":
            text_content = extract_text_from_txt(file_content)
        
        # Chunking the text contents
        if chunking_strategy == "fixed":
            chunks = fixed_chunking(text_content, chunk_size, chunk_overlap)
            strategy_used = "Fixed Character text splitter"
        else:
            chunks = recursive_chunking(text_content, chunk_size, chunk_overlap)
            strategy_used = "Recursive Character text splitter"

        #Embeddings the chunks
        embeddings = create_embeddings(chunks)

        #Store in Qdrant vector database
        point_ids = store_in_qdrant(chunks, embeddings, uploaded_file.filename)

        file_size = len(file_content)

        #Store metedata in postgres database
        doc_id = store_metadata_in_postgres(uploaded_file.filename, file_extension, file_size, chunking_strategy, chunks, point_ids, db)

        return {"document_id": str(doc_id), "message": "Document and chunks stored sucessfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail = f"Internal server error: {str(e)}")
