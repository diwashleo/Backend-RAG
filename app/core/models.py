from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship, declarative_mixin
from .db import Base
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

class Document(Base):
    __tablename__= "documents"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String, unique=True, nullable=False)
    file_type = Column(String)
    file_size = Column(Integer)
    chunking_strategy = Column(String)
    total_chunks = Column(Integer)
    embedding_model = Column(String)
    chunks = relationship("Chunk", back_populates="document")

class Chunk(Base):
    __tablename__= "chunks"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"))
    chunk_id = Column(Integer)
    qdrant_point_id = Column(UUID(as_uuid=True))
    text_content = Column(String)
    chunk_length = Column(Integer)
    document = relationship("Document", back_populates="chunks")

@declarative_mixin
class TimestampMixin:
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class InterviewBooking(Base, TimestampMixin):
    __tablename__= "interview_bookings"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True, nullable=True)
    name = Column(String, nullable=False)
    email = Column(String, index=True, nullable=False)
    interview_at_utc = Column(DateTime, nullable=False)