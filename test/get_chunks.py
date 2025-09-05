from app.core.vector_db import client, collection_name

def get_chunks_by_filename(filename: str):
    """Fetch chunks and chunk IDs for a given filename"""
    try:
        results = client.scroll(
            collection_name=collection_name,
            scroll_filter={"must": [{"key": "filename", "match": {"value": filename}}]},
            with_payload=True,
            with_vectors=False,
            limit=1000  
        )

        points, _ = results
        chunks = []
        for p in points:
            chunks.append({
                "point_id": p.id,
                "chunk_id": p.payload.get("chunk_id"),
                "chunk_text": p.payload.get("chunk")
            })

        return chunks

    except Exception as e:
        print(f"Error retrieving chunks: {str(e)}")
        return []

if __name__ == "__main__":
    filename = "sample.pdf" 
    chunks = get_chunks_by_filename(filename)

    for c in chunks:
        clean_text = " ".join(c['chunk_text'].split())
        print(f"Chunk ID: {c['chunk_id']} | Point ID: {c['point_id']}")
        print(f"Text: {clean_text}\n{'-'*50}")
