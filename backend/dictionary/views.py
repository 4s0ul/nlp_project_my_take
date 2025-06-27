from pydantic import BaseModel, UUID4
from typing import Optional, Any, Dict
from datetime import datetime
from dictionary.nlp.languages import Lang
from dictionary.nlp.triplets import TripletData


class Topic(BaseModel):
    name: str
    info: Optional[str] = None


class TopicsResponse(BaseModel):
    id: UUID4
    topic: Topic
    created_at: datetime


class ProcessedTerm(BaseModel):
    cleaned_text: Optional[str] = None
    stemmed_text: Optional[str] = None
    first_letter: Optional[str] = None


class Term(BaseModel):
    topic_id: UUID4
    raw_text: str
    processed_text: Optional[ProcessedTerm] = None
    language: Optional[Lang] = None
    info: Optional[str] = None


class TermsResponse(BaseModel):
    id: UUID4
    term: Term
    created_at: datetime


class ProcessedDescription(BaseModel):
    cleaned_text: Optional[str] = None
    stemmed_text: Optional[str] = None


class Description(BaseModel):
    term_id: UUID4
    raw_text: str
    processed_text: Optional[ProcessedDescription] = None
    language: Optional[Lang] = None
    info: Optional[str] = None


class DescriptionsResponse(BaseModel):
    id: UUID4
    description: Description
    created_at: datetime


class Triplet(BaseModel):
    description_id: UUID4
    data: TripletData
    info: Optional[str] = None


class TripletsResponse(BaseModel):
    id: UUID4
    triplet: Triplet
    created_at: datetime


class Graph(BaseModel):
    description_id: UUID4
    triplet_count: int
    graph: Dict[str, Any]
    info: Optional[str] = None
    language: Optional[Lang] = None


class GraphsResponse(BaseModel):
    id: UUID4
    graph: Graph
    created_at: datetime
