from langchain_huggingface import HuggingFaceEmbeddings
from fastapi import HTTPException

def create_embeddings(chunks: list):
    """Creating embeddings for text chunks"""
    try:
        embeddings_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device':'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        embeddings = embeddings_model.embed_documents(chunks)
        return embeddings
    except Exception as e:
        raise HTTPException(status_code=500, detail= f"Error creating embeddings: {str(e)}")
    