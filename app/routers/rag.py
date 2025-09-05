from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from datetime import datetime
import re

from core.db import SessionLocal, get_db
from core.retrieval import search_documents
from core.prompt import build_messages, SYSTEM_PROMPT
from core.llm import generate_response
from core.memory import save_chat_history, get_chat_history
from core.models import InterviewBooking
from core.email import send_booking_email, EmailSendError
from core.booking import extract_booking_slots, is_booking_intent

router = APIRouter()

class AskRequest(BaseModel):
    session_id: str = Field(..., description="Unique session ID for conversation")
    query: str = Field(..., description="User question")
    top_k: int = 5

class Citation(BaseModel):
    filename: str
    chunk_id: Optional[int]
    score: float
    qdrant_id: str


class AskResponse(BaseModel):
    answer: str
    citations: List[Citation]
    context_found: bool
    query: str

@router.post("/ask", response_model=AskResponse)
def ask(payload: AskRequest, db: Session = Depends(get_db)):
    try:
        user_text = payload.query.strip()

        # ------ Booking intent flow -----
        if is_booking_intent(user_text):
            name, email, event_date, event_time = extract_booking_slots(user_text)
            missing = []
            if not name:
                missing.append("name")
            if not email:
                missing.append("email")
            if not event_date:
                missing.append("date")
            if not event_time:
                missing.append("time")

            if missing:
                ask_str = (
                    "I can help you book an interview. Please provide the following: "
                    f"{', '.join(missing)}. "
                    "Example: 'Book interview, name Diwash, email diwash@gmail.com, 2 sep 2025 3:30 PM'"
                )
                save_chat_history(payload.session_id, "assistant", ask_str)
                return AskResponse(
                    answer=ask_str,
                    citations=[],
                    context_found=False,
                    query=payload.query
                )
            
            interview_dt = datetime.combine(event_date, event_time)
            booking = InterviewBooking(
                session_id=payload.session_id,
                name=name.strip(),
                email=str(email),
                interview_at_utc=interview_dt
            )
            db.add(booking)
            db.commit()
            db.refresh(booking)

            human_time = interview_dt.strftime("%A, %d %B %Y at %I:%M %p")

            subject = "Interview Booking Confirmation"
            body_text = (
                f"Hi {booking.name},\n\n"
                f"Your interview is confirmed for {human_time}.\n\n"
                "If you need to reschedule, reply to this email.\n\nThanks!"
            )
            body_html = (
                f"<p>Hi {booking.name},</p>"
                f"<p>Your interview is <strong>confirmed</strong> for <strong>{human_time}</strong>.</p>"
                "<p>If you need to reschedule, reply to this email.</p><p>Thanks!</p>"
            )
            email_status = "email_sent"
            try:
                send_booking_email(booking.email, subject, body_text, body_html)
            except EmailSendError as e:
                email_status = f"email_failed: {e}"
            answer = f"Booked interview (ID {booking.id} for {booking.name} on {human_time}. Confirmation: {email_status}.)"

            save_chat_history(payload.session_id, "user", payload.query)
            save_chat_history(payload.session_id, "assistant", answer)

            return AskResponse(
                answer=answer,
                citations=[],
                context_found=False,
                query=payload.query
            )


        #  -------Normal Rag Flow -----
        # Do retrieval
        chunks = search_documents(payload.query, payload.top_k, db)

        # Build messages = combine history + context + new query
        messages = build_messages(payload.session_id, payload.query, chunks)

        answer = generate_response(payload.session_id, messages, temperature=0.2, max_tokens=800)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG failed: {e}")

    citations = []
    context_found = False
    for chunk in chunks:
        if chunk.get("text") and chunk.get("text") != "Content not found in database":
            context_found = True

        doc_info = chunk.get("document", {})
        citations.append(Citation(
            filename=doc_info.get("filename", "Unknown"),
            chunk_id=chunk.get("chunk_id"),
            score=chunk.get("score", 0.0),
            qdrant_id=chunk.get("qdrant_id", "")
        ))
    
    return AskResponse(
        answer=answer,
        citations=citations,
        context_found=context_found,
        query=payload.query
    )