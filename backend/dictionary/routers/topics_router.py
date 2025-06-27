from pydantic import UUID4
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from dictionary.database.engine import get_session
from dictionary.database.models import Topics
from dictionary.database.queries import (
    select_topic_by_name,
    save_topic,
    select_topic_by_id,
    select_all_topics,
    delete_topic_by_id,
)
from dictionary.views import Topic, TopicsResponse


router = APIRouter(
    prefix="/topics",
    tags=["Topics"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "",
    status_code=status.HTTP_200_OK,
    summary="Add topic",
    response_model=TopicsResponse,
)
async def create_topic(body_obj: Topic, session: AsyncSession = Depends(get_session)):
    topics_object = await select_topic_by_name(
        topic_name=body_obj.name, session=session
    )

    if topics_object is None:
        topics_object = await save_topic(
            topic=Topics(name=body_obj.name, info=body_obj.info), session=session
        )

    return TopicsResponse(
        id=topics_object.id,
        topic=Topic(name=topics_object.name, info=topics_object.info),
        created_at=topics_object.created_at,
    )


@router.put(
    "",
    status_code=status.HTTP_200_OK,
    summary="Change topic",
    response_model=TopicsResponse,
)
async def change_topic(
    topic_id: UUID4, body_obj: Topic, session: AsyncSession = Depends(get_session)
):
    topics_object = await select_topic_by_id(topic_id=topic_id, session=session)

    if topics_object is None:
        raise HTTPException(
            status_code=404, detail=f"Topic with {topic_id=} not found!"
        )

    topics_object.name = body_obj.name
    topics_object.info = body_obj.info

    topics_object = await save_topic(topic=topics_object, session=session)

    return TopicsResponse(
        id=topics_object.id,
        topic=Topic(name=topics_object.name, info=topics_object.info),
        created_at=topics_object.created_at,
    )


@router.delete(
    "/{topic_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete topic",
)
async def delete_topic(
    topic_id: UUID4, session: AsyncSession = Depends(get_session)
):
    topics_object = await select_topic_by_id(topic_id=topic_id, session=session)

    if topics_object is None:
        raise HTTPException(
            status_code=404,
            detail=f"Topic with id {topic_id} not found",
        )
    await delete_topic_by_id(topic_id=topic_id, session=session)


@router.get(
    "",
    status_code=200,
    summary="Get topics",
    response_model=List[TopicsResponse],
)
async def fetch_topics(session: AsyncSession = Depends(get_session)):
    topics_objects = await select_all_topics(session=session)

    return [
        TopicsResponse(
            id=topics_object.id,
            topic=Topic(name=topics_object.name, info=topics_object.info),
            created_at=topics_object.created_at,
        )
        for topics_object in topics_objects
    ]


@router.get(
    "/id/{topic_id}",
    status_code=200,
    summary="Get topic by id",
    response_model=TopicsResponse,
)
async def fetch_topic_by_id(
    topic_id: UUID4, session: AsyncSession = Depends(get_session)
):
    topics_object = await select_topic_by_id(topic_id=topic_id, session=session)

    if topics_object is None:
        raise HTTPException(
            status_code=404, detail=f"Topic with {topic_id=} not found!"
        )

    return TopicsResponse(
        id=topics_object.id,
        topic=Topic(name=topics_object.name, info=topics_object.info),
        created_at=topics_object.created_at,
    )


@router.get(
    "/name/{topic_name}",
    status_code=200,
    summary="Get topic by name",
    response_model=TopicsResponse,
)
async def fetch_topic_by_name(
    topic_name: str, session: AsyncSession = Depends(get_session)
):
    topics_object = await select_topic_by_name(topic_name=topic_name, session=session)

    if topics_object is None:
        raise HTTPException(
            status_code=404, detail=f"Topic with {topic_name=} not found!"
        )

    return TopicsResponse(
        id=topics_object.id,
        topic=Topic(name=topics_object.name, info=topics_object.info),
        created_at=topics_object.created_at,
    )
