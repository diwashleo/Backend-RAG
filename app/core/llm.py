import os
from typing import List, Dict
from groq import Groq
from dotenv import load_dotenv
from core.memory import save_chat_history

load_dotenv()

GROQ_MODEL = os.getenv("GROQ_MODEL")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

def generate_response(session_id: str, messages: List[Dict[str, str]], temperature: float = 0.2, max_tokens: int = 800) -> str:
    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
        
        answer = response.choices[0].message.content.strip()

        # Save last user + assistant messages into memory
        if messages and messages[-1]["role"] == "user":
            user_question = messages[-1]["content"].split("Question:")[-1].split("Context:")[0].strip()
            save_chat_history(session_id, "user", user_question)
        save_chat_history(session_id, "assistant", answer)

        return answer
        
    except Exception as e:
        raise Exception(f"Failed to generate response: {str(e)}")