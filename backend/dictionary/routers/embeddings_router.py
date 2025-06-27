from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from pydantic import BaseModel, UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from dictionary.database.engine import get_session
from dictionary.database.queries import search_terms_by_embedding
from dictionary.nlp.embeddings import vectorize_text
from dictionary.nlp.languages import detect_language, Lang
from dictionary.views import Term, ProcessedTerm, TermsResponse

router = APIRouter(tags=["search"])


class SearchResult(BaseModel):
    id: UUID4
    term: str
    definition: str
    distance: float


@router.post(
    "/search",
    summary="Vector‐search for terms by natural‐language query",
    response_model=List[TermsResponse],
)
async def search_terms(
    query: str,
    k: int = Query(10, ge=1, le=100, description="How many results to return"),
    session: AsyncSession = Depends(get_session),
):
    try:
        lang: Lang = detect_language(query)
    except ValueError as e:
        raise HTTPException(400, f"Language detection failed: {e}")

    vec = vectorize_text(query, lang)
    if vec is None:
        raise HTTPException(500, "Failed to vectorize your query")

    terms_objects = await search_terms_by_embedding(qv=vec, k=k, session=session)

    return [
        TermsResponse(
            id=terms_object.id,
            term=Term(
                topic_id=terms_object.topic_id,
                language=Lang(terms_object.language),
                raw_text=terms_object.raw_text,
                processed_text=ProcessedTerm(
                    cleaned_text=terms_object.cleaned_text,
                    stemmed_text=terms_object.stemmed_text,
                    first_letter=terms_object.first_letter,
                ),
                info=terms_object.info,
            ),
            created_at=terms_object.created_at,
        )
        for terms_object in terms_objects
    ]
