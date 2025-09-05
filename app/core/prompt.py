from typing import List, Dict
from core.memory import get_chat_history, save_chat_history

SYSTEM_PROMPT = """You are a helpful AI assistant that answers questions based on provided context and conversation history.

Instructions:
- Use BOTH the provided context (retrieved documents) and conversation history (previous user and assistant messages) to answer questions.
- If the answer is in history but not in the context, you may still use history.
- If the answer is not in either context or history, clearly state "I don't have enough information to answer this question."
- Cite your sources using the format [filename#chunk_id] when referencing specific information
- Be concise and accurate
- If multiple sources support your answer, cite all relevant sources
"""

# Build chat messages for LLM
def build_messages(session_id: str, query: str, chunks: List[Dict], max_context_chars: int = 6000) -> List[Dict[str, str]]:
    context_pieces = []
    total_chars = 0

    for chunk in chunks:

        if not chunk.get("text") or chunk.get("text") == "Content not found in database":
            continue

        # Getting document information
        doc_info = chunk.get("document", {})
        filename = doc_info.get("filename", "Unknown")
        chunk_id = chunk.get("chunk_id", "0")
        text = chunk.get("text", "").strip()
        text = " ".join(text.split())
        if len(text)> 1000:
            text = text[:1000] + "..."
        context_piece = f"[{filename}#{chunk_id}] {text}"
        if total_chars + len(context_piece) > max_context_chars:
            break
        context_pieces.append(context_piece)
        total_chars += len(context_piece)
    
    if context_pieces:
        context_block = "\n\n".join(context_pieces)
    else:
        context_block = "No relevant context found."

    # Fetch past conversation from memory
    history = get_chat_history(session_id)

    # Starting messages with system prompt
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Append past history
    for h in history:
        messages.append({"role":h["role"], "content": h["message"]})

    # Append current user query
    user_content = f"""
    Question:
    {query}

    Context:
    {context_block}

    Please answer the question using both the conversation history and context. 
    """
    messages.append({"role": "user", "content": user_content})
    return messages