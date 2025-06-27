from pydantic import UUID4
import uuid
from datetime import datetime
from typing import Optional, List, Dict
from sqlmodel import Field, SQLModel, Column
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import JSONB


DEFAULT_VECTOR_DIM = 300


class Topics(SQLModel, table=True):
    __tablename__ = "topics"
    id: UUID4 = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(unique=True)
    info: Optional[str] = Field(default=None, nullable=True)
    created_at: datetime = Field(default_factory=datetime.now)


class Terms(SQLModel, table=True):
    __tablename__ = "terms"
    id: UUID4 = Field(default_factory=uuid.uuid4, primary_key=True)
    topic_id: UUID4 = Field(foreign_key="topics.id", index=True)
    language: str = Field(nullable=False)
    raw_text: str = Field(nullable=False)
    cleaned_text: str = Field(nullable=False)
    stemmed_text: str = Field(nullable=False)
    first_letter: str = Field(max_length=1)
    info: Optional[str] = Field(default=None, nullable=True)
    created_at: datetime = Field(default_factory=datetime.now)


class Descriptions(SQLModel, table=True):
    __tablename__ = "descriptions"
    id: UUID4 = Field(default_factory=uuid.uuid4, primary_key=True)
    term_id: UUID4 = Field(foreign_key="terms.id", index=True, unique=True)
    raw_text: str = Field(nullable=False, unique=True)
    cleaned_text: str = Field(nullable=False, unique=True)
    stemmed_text: str = Field(nullable=False, unique=True)
    language: str = Field(nullable=False)
    info: Optional[str] = Field(default=None, nullable=True)
    created_at: datetime = Field(default_factory=datetime.now)


class Embeddings(SQLModel, table=True):
    __tablename__ = "embeddings"
    id: UUID4 = Field(default_factory=uuid.uuid4, primary_key=True)
    description_id: UUID4 = Field(foreign_key="descriptions.id", unique=True, index=True)
    embedding: List[float] = Field(sa_column=Column(Vector(DEFAULT_VECTOR_DIM)))
    language: str = Field(nullable=False)
    info: Optional[str] = Field(default=None, nullable=True)
    created_at: datetime = Field(default_factory=datetime.now)


class Triplets(SQLModel, table=True):
    __tablename__ = "triplets"
    id: UUID4 = Field(default_factory=uuid.uuid4, primary_key=True)
    description_id: UUID4 = Field(foreign_key="descriptions.id", index=True)
    position: int = Field(nullable=False)
    subject: str = Field(nullable=False)
    subject_type: Optional[str] = Field(default=None, nullable=True)
    predicate: str = Field(nullable=False)
    predicate_type: Optional[str] = Field(default=None, nullable=True)
    object: str = Field(nullable=False)
    object_type: Optional[str] = Field(default=None, nullable=True)
    language: str = Field(nullable=False)
    info: Optional[str] = Field(default=None, nullable=True)
    created_at: datetime = Field(default_factory=datetime.now)


class Graphs(SQLModel, table=True):
    __tablename__ = "graphs"
    id: UUID4 = Field(default_factory=uuid.uuid4, primary_key=True)
    description_id: UUID4 = Field(foreign_key="descriptions.id", unique=True, index=True)
    triplet_count: int = Field(nullable=False, default=0)
    graph: Dict = Field(sa_type=JSONB, nullable=False)
    language: str = Field(nullable=False)
    info: Optional[str] = Field(default=None, nullable=True)
    created_at: datetime = Field(default_factory=datetime.now)
