import asyncio
from pydantic import UUID4
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from dictionary.database.engine import get_session
from dictionary.database.models import Descriptions
from dictionary.views import (
    Description,
    DescriptionsResponse,
    ProcessedDescription,
)
from dictionary.database.queries import (
    save_description,
    select_description_by_id,
    select_description_by_raw_text,
    select_description_by_cleaned_text,
    select_description_by_stemmed_text,
    select_description_by_term_id,
)
from dictionary.nlp.languages import Lang, detect_language
from dictionary.nlp.preprocessing import clean_text
from dictionary.nlp.stemming import stem_tokens
from dictionary.background_tasks.background_embeddings import create_embedding, update_embedding
from dictionary.background_tasks.background_triplets import create_triplets_and_graphs, update_triplets_and_graphs


router = APIRouter(
    prefix="/descriptions",
    tags=["Descriptions"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "",
    status_code=status.HTTP_200_OK,
    summary="Add description to term",
    response_model=DescriptionsResponse,
)
async def create_description(
    body_obj: Description, session: AsyncSession = Depends(get_session)
):
    descriptions_object = await select_description_by_raw_text(
        raw_text=body_obj.raw_text, session=session
    )

    if descriptions_object is None:
        lang = body_obj.language
        if not lang:
            lang = detect_language(text=body_obj.raw_text)
        cleaned_tokens = clean_text(text=body_obj.raw_text, language=lang)
        cleaned_text = " ".join(cleaned_tokens)
        cleaned_text_terms_object = await select_description_by_cleaned_text(
            cleaned_text=cleaned_text, session=session
        )
        if cleaned_text_terms_object:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Description with the same cleaned text already exists.",
            )
        stemmed_tokens = stem_tokens(cleaned_tokens, language=lang)
        stemmed_text = " ".join(stemmed_tokens)
        stemmed_text_terms_object = await select_description_by_stemmed_text(
            stemmed_text=stemmed_text, session=session
        )
        if stemmed_text_terms_object:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Description with the same stemmed text already exists.",
            )
        descriptions_object = Descriptions(
            term_id=body_obj.term_id,
            language=lang.value,
            raw_text=body_obj.raw_text,
            cleaned_text=" ".join(cleaned_tokens),
            stemmed_text=" ".join(stemmed_tokens),
            info=body_obj.info,
        )
        descriptions_object = await save_description(
            description=descriptions_object, session=session
        )
        asyncio.create_task(
            create_embedding(
                text=" ".join(stemmed_tokens),
                lang=lang,
                description_id=descriptions_object.id,
            )
        )
        asyncio.create_task(
            create_triplets_and_graphs(
                text=body_obj.raw_text,
                lang=lang,
                description_id=descriptions_object.id,
            )
        )

    return DescriptionsResponse(
        id=descriptions_object.id,
        description=Description(
            term_id=descriptions_object.term_id,
            language=Lang(descriptions_object.language),
            raw_text=descriptions_object.raw_text,
            processed_text=ProcessedDescription(
                cleaned_text=descriptions_object.cleaned_text,
                stemmed_text=descriptions_object.stemmed_text,
            ),
            info=descriptions_object.info,
        ),
        created_at=descriptions_object.created_at,
    )


@router.put(
    "/raw_text/{new_descriptions_raw_text}",
    status_code=status.HTTP_200_OK,
    summary="Change descriptions text",
    response_model=DescriptionsResponse,
)
async def change_descriptions_raw_text(
    description_id: UUID4, new_descriptions_raw_text: str, session: AsyncSession = Depends(get_session)
):
    descriptions_object = await select_description_by_id(
        id=description_id, session=session
    )

    if descriptions_object is None:
        raise HTTPException(
            status_code=404,
            detail=f"Description with {description_id=} not found!",
        )

    lang=Lang(descriptions_object.language)
    if new_descriptions_raw_text != descriptions_object.raw_text:
        descriptions_object.raw_text = new_descriptions_raw_text

        asyncio.create_task(
            update_triplets_and_graphs(
                text=new_descriptions_raw_text,
                lang=lang,
                description_id=descriptions_object.id,
            )
        )

        cleaned_tokens = clean_text(text=new_descriptions_raw_text, language=lang)
        cleaned_text = " ".join(cleaned_tokens)

        if cleaned_text != descriptions_object.cleaned_text:
            descriptions_object.cleaned_text = cleaned_text

            stemmed_tokens = stem_tokens(cleaned_tokens, language=lang)
            stemmed_text = " ".join(stemmed_tokens)

            if stemmed_text != descriptions_object.stemmed_text:
                descriptions_object.stemmed_text = stemmed_text

                asyncio.create_task(
                    update_embedding(
                        text=stemmed_text,
                        lang=lang,
                        description_id=descriptions_object.id,
                    )
                )

        descriptions_object = await save_description(
            description=descriptions_object, session=session
        )

    return DescriptionsResponse(
        id=descriptions_object.id,
        description=Description(
            term_id=descriptions_object.term_id,
            language=Lang(descriptions_object.language),
            raw_text=descriptions_object.raw_text,
            processed_text=ProcessedDescription(
                cleaned_text=descriptions_object.cleaned_text,
                stemmed_text=descriptions_object.stemmed_text,
            ),
            info=descriptions_object.info,
        ),
        created_at=descriptions_object.created_at,
    )


@router.patch(
    "/new_descriptions_cleaned_text/{new_descriptions_cleaned_text}",
    status_code=status.HTTP_200_OK,
    summary="Change descriptions cleaned text",
    response_model=DescriptionsResponse,
)
async def change_descriptions_cleaned_text(
    description_id: UUID4, new_descriptions_cleaned_text: str, session: AsyncSession = Depends(get_session)
):
    descriptions_object = await select_description_by_id(
        id=description_id, session=session
    )

    if descriptions_object is None:
        raise HTTPException(
            status_code=404,
            detail=f"Description with {description_id=} not found!",
        )

    lang=Lang(descriptions_object.language)
    if new_descriptions_cleaned_text != descriptions_object.cleaned_text:
        descriptions_object.cleaned_text = new_descriptions_cleaned_text

        cleaned_tokens = new_descriptions_cleaned_text.split()
        stemmed_tokens = stem_tokens(cleaned_tokens, language=lang)
        stemmed_text = " ".join(stemmed_tokens)

        if stemmed_text != descriptions_object.stemmed_text:

            descriptions_object.stemmed_text = stemmed_text

            asyncio.create_task(
                update_embedding(
                    text=stemmed_text,
                    lang=lang,
                    description_id=descriptions_object.id,
                )
            )

        descriptions_object = await save_description(
            description=descriptions_object, session=session
        )

    return DescriptionsResponse(
        id=descriptions_object.id,
        description=Description(
            term_id=descriptions_object.term_id,
            language=Lang(descriptions_object.language),
            raw_text=descriptions_object.raw_text,
            processed_text=ProcessedDescription(
                cleaned_text=descriptions_object.cleaned_text,
                stemmed_text=descriptions_object.stemmed_text,
            ),
            info=descriptions_object.info,
        ),
        created_at=descriptions_object.created_at,
    )


@router.patch(
    "/new_descriptions_stemmed_text/{new_descriptions_stemmed_text}",
    status_code=status.HTTP_200_OK,
    summary="Change descriptions stemmed text",
    response_model=DescriptionsResponse,
)
async def change_descriptions_stemmed_text(
    description_id: UUID4, new_descriptions_stemmed_text: str, session: AsyncSession = Depends(get_session)
):
    descriptions_object = await select_description_by_id(
        id=description_id, session=session
    )

    if descriptions_object is None:
        raise HTTPException(
            status_code=404,
            detail=f"Description with {description_id=} not found!",
        )

    lang=Lang(descriptions_object.language)
    if new_descriptions_stemmed_text != descriptions_object.stemmed_text:
        descriptions_object.stemmed_text = new_descriptions_stemmed_text

        descriptions_object = await save_description(
            description=descriptions_object, session=session
        )

        asyncio.create_task(
            update_embedding(
                text=new_descriptions_stemmed_text,
                lang=lang,
                description_id=descriptions_object.id,
            )
        )

    return DescriptionsResponse(
        id=descriptions_object.id,
        description=Description(
            term_id=descriptions_object.term_id,
            language=Lang(descriptions_object.language),
            raw_text=descriptions_object.raw_text,
            processed_text=ProcessedDescription(
                cleaned_text=descriptions_object.cleaned_text,
                stemmed_text=descriptions_object.stemmed_text,
            ),
            info=descriptions_object.info,
        ),
        created_at=descriptions_object.created_at,
    )


# @router.get(
#     "/description_id/{description_id}",
#     status_code=status.HTTP_200_OK,
#     summary="Get description by id",
#     response_model=DescriptionsResponse,
# )
# async def fetch_terms_by_id(
#     description_id: UUID4, session: AsyncSession = Depends(get_session)
# ):
#     descriptions_object = await select_description_by_id(
#         id=description_id, session=session
#     )
#
#     if descriptions_object is None:
#         raise HTTPException(
#             status_code=404, detail=f"Term with {description_id=} not found!"
#         )
#
#     return DescriptionsResponse(
#         id=descriptions_object.id,
#         description=Description(
#             term_id=descriptions_object.term_id,
#             language=Lang(descriptions_object.language),
#             raw_text=descriptions_object.raw_text,
#             processed_text=ProcessedDescription(
#                 cleaned_text=descriptions_object.cleaned_text,
#                 stemmed_text=descriptions_object.stemmed_text,
#             ),
#             info=descriptions_object.info,
#         ),
#         created_at=descriptions_object.created_at,
#     )


@router.get(
    "/{term_id}",
    status_code=status.HTTP_200_OK,
    summary="Get description by term_id",
    response_model=DescriptionsResponse,
)
async def fetch_description_by_term_id(
    term_id: UUID4, session: AsyncSession = Depends(get_session)
):
    descriptions_object = await select_description_by_term_id(
        term_id=term_id, session=session
    )

    if descriptions_object is None:
        raise HTTPException(
            status_code=404, detail=f"Description related with {term_id=} not found!"
        )

    return DescriptionsResponse(
        id=descriptions_object.id,
        description=Description(
            term_id=descriptions_object.term_id,
            language=Lang(descriptions_object.language),
            raw_text=descriptions_object.raw_text,
            processed_text=ProcessedDescription(
                cleaned_text=descriptions_object.cleaned_text,
                stemmed_text=descriptions_object.stemmed_text,
            ),
            info=descriptions_object.info,
        ),
        created_at=descriptions_object.created_at,
    )
