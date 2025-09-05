import redis
import json
from typing import List, Dict

#Connect to redis
memory = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Append a message to chat history
def save_chat_history(session_id: str, role: str, message: str):
    chat_entry = json.dumps({"role": role, "message": message})
    memory.rpush(session_id, chat_entry)

# Retrive chat history 
def get_chat_history(session_id: str) -> List[Dict[str, str]]:
    messages = memory.lrange(session_id, 0, -1)
    return [json.loads(m) for m in messages]