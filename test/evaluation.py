import time
from typing import List, Dict, Set
from sqlalchemy.orm import Session
from app.core.retrieval import search_documents
from app.core.vector_db import client, collection_name
from app.core.db import get_db

# Ground Truth Dataset
GROUND_TRUTH = [
    {
        "query": "What is the minimum age to use Dropit app?",
        "relevant_chunks": [3, 4], 
    },
    {
        "query": "Who is responsible for manufacturing defects?",
        "relevant_chunks": [1],  
    },
    {
        "query": "How can I return a product?",
        "relevant_chunks": [15, 16],  
    },
    {
        "query": "Which law governs the Terms & Conditions?",
        "relevant_chunks": [22],  
    },
    {
        "query": "What is Dropit Nepal?",
        "relevant_chunks": [0]
    }
]


def precision(tp: int, fp: int) -> float:
    return tp / (tp + fp) if (tp + fp) > 0 else 0.0


def recall(tp: int, fn: int) -> float:
    return tp / (tp + fn) if (tp + fn) > 0 else 0.0


def f1_score(p: float, r: float) -> float:
    return 2 * (p * r) / (p + r) if (p + r) > 0 else 0.0


def evaluate_queries(db: Session = None, top_k: int = 5):
    results_per_query = []

    for item in GROUND_TRUTH:
        query = item["query"]
        relevant: Set[int] = set(item["relevant_chunks"])
        start_time = time.time()
        retrieved = search_documents(query=query, top_k=top_k, db=db)
        latency = time.time() - start_time

        # Extract chunk_ids 
        retrieved_ids: Set[int] = {r.get("chunk_id") for r in retrieved if r.get("chunk_id") is not None}

        # True Positive, False Positive, False Negatives
        tp = len(retrieved_ids & relevant)
        fp = len(retrieved_ids - relevant)
        fn = len(relevant - retrieved_ids)

        p = precision(tp, fp)
        r = recall(tp, fn)
        f1 = f1_score(p, r)

        results_per_query.append({
            "query": query,
            "precision": p,
            "recall": r,
            "f1_score": f1,
            "latency": latency
        })

        print(f"\nQuery: {query}")
        print(f"Retrieved chunk_ids: {retrieved_ids}")
        print(f"Relevant chunk_ids: {relevant}")

    # Print metrics
    for m in results_per_query:
        print(f"\nQuery: {m['query']}")
        print(f" Precision: {m['precision']:.2f}")
        print(f" Recall: {m['recall']:.2f}")
        print(f" F1: {m['f1_score']:.2f}")
        print(f" Latency: {m['latency']:.3f}s")

    # Overall averages
    avg_p = sum(m["precision"] for m in results_per_query) / len(results_per_query)
    avg_r = sum(m["recall"] for m in results_per_query) / len(results_per_query)
    avg_f1 = sum(m["f1_score"] for m in results_per_query) / len(results_per_query)
    avg_latency = sum(m["latency"] for m in results_per_query) / len(results_per_query)

    print("\n=== Overall Averages ===")
    print(f"Avg Precision: {avg_p:.2f}")
    print(f"Avg Recall: {avg_r:.2f}")
    print(f"Avg F1: {avg_f1:.2f}")
    print(f"Avg Latency: {avg_latency:.3f}s")

if __name__ == "__main__":
    db_gen = get_db()  # generator
    db = next(db_gen)  # get session

    try:
        evaluate_queries(db=db, top_k=2)
    finally:
        db.close()  

# Run by:  uv run -m test.evaluation