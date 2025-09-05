from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import uuid
from fastapi import HTTPException
from .embeddings import create_embeddings


#Initializing Qdrant Clint
client = QdrantClient(host="localhost", port=8888)

#Setting collection name
collection_name = "document_chunks"


def store_in_qdrant(chunks: list, embeddings: list, filename: str):
    """Store chunks and embeddings in Qdrant Vector Database"""
    try:
        embedding_dim = len(embeddings[0])
        #Creating collection
        try:
            #If collection exist
            info = client.get_collection(collection_name)
            existing_dim = info.config.params.vectors["default"].size
            if existing_dim != embedding_dim:
                raise HTTPException(
                    status_code=500,
                    detail=f"Embedding dimension mismatch: collection={existing_dim}, embeddings={embedding_dim}"
                )
        except:
            client.create_collection(
                collection_name = collection_name,
                vectors_config=VectorParams(size=384, distance = Distance.COSINE) # Cosine Similarity
                # vectors_config=VectorParams(size=384, distance = Distance.DOT) # Dot Product

            )
        #Prepareing points for insertion
        points = []
        point_ids = []  
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            point_id = str(uuid.uuid4())  
            point = PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    "filename": filename,
                    "chunk_id": i,
                    "chunk": chunk
                }
            )
            points.append(point)
            point_ids.append(point_id)
        
        # Insert points in Qdrant
        client.upsert(
            collection_name=collection_name,
            points=points
        )

        return point_ids
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error storing in Qdrant: {str(e)}")