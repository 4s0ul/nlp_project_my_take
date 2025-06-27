from pydantic import UUID4
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from dictionary.database.engine import get_session
from dictionary.database.models import Terms
from dictionary.views import Term, ProcessedTerm, TermsResponse
from dictionary.database.queries import (
    save_term,
    select_terms_by_first_letter,
    select_term_by_raw_test,
    select_term_by_cleaned_text,
    select_term_by_stemmed_text,
    select_term_by_id,
    delete_term_by_id,
)
from dictionary.nlp.languages import Lang, detect_language
from dictionary.nlp.preprocessing import clean_text
from dictionary.nlp.stemming import stem_tokens


router = APIRouter(
    prefix="/terms",
    tags=["Terms"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "",
    status_code=status.HTTP_200_OK,
    summary="Add term",
    response_model=TermsResponse,
)
async def create_term(body_obj: Term, session: AsyncSession = Depends(get_session)):
    terms_object = await select_term_by_raw_test(
        raw_text=body_obj.raw_text, session=session
    )

    if terms_object is None:
        lang = body_obj.language
        if not lang:
            lang = detect_language(text=body_obj.raw_text)
        cleaned_tokens = clean_text(text=body_obj.raw_text, language=lang)
        cleaned_text = " ".join(cleaned_tokens)
        cleaned_text_terms_object = await select_term_by_cleaned_text(
            cleaned_text=cleaned_text, session=session
        )
        if cleaned_text_terms_object:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Term with the same cleaned text already exists.",
            )
        stemmed_tokens = stem_tokens(cleaned_tokens, language=lang)
        stemmed_text = " ".join(stemmed_tokens)
        stemmed_text_terms_object = await select_term_by_stemmed_text(
            stemmed_text=stemmed_text, session=session
        )
        if stemmed_text_terms_object:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Term with the same stemmed text already exists.",
            )
        terms_object = Terms(
            topic_id=body_obj.topic_id,
            language=lang.value,
            raw_text=body_obj.raw_text,
            cleaned_text=cleaned_text,
            stemmed_text=stemmed_text,
            first_letter=stemmed_tokens[0][0],
            info=body_obj.info,
        )
        terms_object = await save_term(term=terms_object, session=session)

    return TermsResponse(
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


@router.put(
    "/raw_text/{new_terms_raw_text}",
    status_code=status.HTTP_200_OK,
    summary="Change terms raw text",
    response_model=TermsResponse,
)
async def change_terms_raw_text(term_id: UUID4, new_terms_raw_text: str, session: AsyncSession = Depends(get_session)):
    terms_object = await select_term_by_id(
        id=term_id, session=session
    )

    if terms_object is None:
        raise HTTPException(status_code=404, detail=f"Term with {term_id=} not found!")

    if terms_object.raw_text != new_terms_raw_text:
        terms_object.raw_text = new_terms_raw_text

        lang = Lang(terms_object.language)

        cleaned_tokens = clean_text(text=new_terms_raw_text, language=lang)
        cleaned_text = " ".join(cleaned_tokens)

        if terms_object.cleaned_text != cleaned_text:
            terms_object.cleaned_text = cleaned_text

            stemmed_tokens = stem_tokens(cleaned_tokens, language=lang)
            stemmed_text = " ".join(stemmed_tokens)

            if terms_object.stemmed_text != stemmed_text:
                terms_object.stemmed_text = stemmed_text

        terms_object = await save_term(term=terms_object, session=session)

    return TermsResponse(
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


@router.patch(
    "/cleaned_text/{new_terms_cleaned_text}",
    status_code=status.HTTP_200_OK,
    summary="Change terms cleaned text",
    response_model=TermsResponse,
)
async def change_terms_cleaned_text(term_id: UUID4, new_terms_cleaned_text: str, session: AsyncSession = Depends(get_session)):
    terms_object = await select_term_by_id(
        id=term_id, session=session
    )

    if terms_object is None:
        raise HTTPException(status_code=404, detail=f"Term with {term_id=} not found!")

    if terms_object.cleaned_text != new_terms_cleaned_text:
        terms_object.cleaned_text = new_terms_cleaned_text

        lang = Lang(terms_object.language)

        cleaned_tokens = new_terms_cleaned_text.split()

        stemmed_tokens = stem_tokens(cleaned_tokens, language=lang)
        stemmed_text = " ".join(stemmed_tokens)

        if terms_object.stemmed_text != stemmed_text:
            terms_object.stemmed_text = stemmed_text

        terms_object = await save_term(term=terms_object, session=session)

    return TermsResponse(
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


@router.patch(
    "/stemmed_text/{new_terms_stemmed_text}",
    status_code=status.HTTP_200_OK,
    summary="Change terms stemmed text",
    response_model=TermsResponse,
)
async def change_terms_stemmed_text(term_id: UUID4, new_terms_stemmed_text: str, session: AsyncSession = Depends(get_session)):
    terms_object = await select_term_by_id(
        id=term_id, session=session
    )

    if terms_object is None:
        raise HTTPException(status_code=404, detail=f"Term with {term_id=} not found!")

    if terms_object.stemmed_text != new_terms_stemmed_text:
        terms_object.stemmed_text = new_terms_stemmed_text

        terms_object = await save_term(term=terms_object, session=session)

    return TermsResponse(
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


@router.delete(
    "/{term_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete term",
)
async def delete_term(
    term_id: UUID4, session: AsyncSession = Depends(get_session)
):
    terms_object = await select_term_by_id(id=term_id, session=session)

    if terms_object is None:
        raise HTTPException(
            status_code=404,
            detail=f"Term with {term_id=} not found",
        )
    await delete_term_by_id(id=term_id, session=session)


@router.get(
    "/first_letter/",
    status_code=status.HTTP_200_OK,
    summary="Get term by first letter and topic id",
    response_model=List[TermsResponse],
)
async def fetch_terms_by_letter(
    first_letter: str,
    topic_id: UUID4,
    limit: int = 5,
    session: AsyncSession = Depends(get_session),
):
    terms_objects = await select_terms_by_first_letter(
        first_letter=first_letter, topic_id=topic_id, limit=limit, session=session
    )

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


@router.get(
    "/term_id/",
    status_code=status.HTTP_200_OK,
    summary="Get term by id",
    response_model=TermsResponse,
)
async def fetch_terms_by_id(
    term_id: UUID4, session: AsyncSession = Depends(get_session)
):
    terms_object = await select_term_by_id(id=term_id, session=session)

    if terms_object is None:
        raise HTTPException(status_code=404, detail=f"Term with {term_id=} not found!")

    return TermsResponse(
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
