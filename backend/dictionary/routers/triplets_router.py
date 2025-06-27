import asyncio
from pydantic import UUID4
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from dictionary.database.engine import get_session
from dictionary.database.models import Triplets
from dictionary.database.queries import (
    save_triplet,
    select_triplets_by_description_id,
    select_description_by_id,
    select_graph_by_description_id,
    select_triplet_by_id,
    delete_triplet_by_id,
)
from dictionary.views import Triplet, TripletsResponse
from dictionary.nlp.triplets import TripletData
from dictionary.nlp.languages import Lang
from dictionary.background_tasks.background_triplets import (
    add_triplet_to_graph,
    remove_triplet_from_graph,
)


router = APIRouter(
    prefix="/triplets",
    tags=["Triplets"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "",
    status_code=status.HTTP_200_OK,
    summary="Add triplet",
    response_model=TripletsResponse,
)
async def create_triplet(
    body_obj: Triplet, session: AsyncSession = Depends(get_session)
):
    description_object = await select_description_by_id(
        id=body_obj.description_id, session=session
    )

    if description_object is None:
        raise HTTPException(
            status_code=404,
            detail=f"Description with {body_obj.description_id=} not found!",
        )

    triplets_object = await save_triplet(
        triplet=Triplets(
            description_id=body_obj.description_id,
            position=body_obj.data.position,
            subject=body_obj.data.subject,
            subject_type=body_obj.data.subject_type,
            predicate=body_obj.data.predicate,
            predicate_type=body_obj.data.predicate_type,
            object=body_obj.data.object,
            object_type=body_obj.data.object_type,
            language=body_obj.data.language.value,
        ),
        session=session,
    )

    graphs_object = await select_graph_by_description_id(
        description_id=body_obj.description_id, session=session
    )

    if graphs_object is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Graphs object with {body_obj.description_id=} not found!",
        )

    asyncio.create_task(
        add_triplet_to_graph(
            graphs_object=graphs_object,
            triplet=TripletData(
                position=triplets_object.position,
                subject=triplets_object.subject,
                subject_type=triplets_object.subject_type,
                predicate=triplets_object.predicate,
                predicate_type=triplets_object.predicate_type,
                object=triplets_object.object,
                object_type=triplets_object.object_type,
                language=Lang(triplets_object.language),
            ),
        )
    )

    return TripletsResponse(
        id=triplets_object.id,
        triplet=Triplet(
            description_id=triplets_object.description_id,
            data=TripletData(
                position=triplets_object.position,
                subject=triplets_object.subject,
                subject_type=triplets_object.subject_type,
                predicate=triplets_object.predicate,
                predicate_type=triplets_object.predicate_type,
                object=triplets_object.object,
                object_type=triplets_object.object_type,
                language=Lang(triplets_object.language),
            ),
        ),
        created_at=triplets_object.created_at,
    )


@router.delete(
    "/{triplet_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete triplet",
)
async def delete_triplet(
    triplet_id: UUID4, session: AsyncSession = Depends(get_session)
):
    triplet_obj = await select_triplet_by_id(id=triplet_id, session=session)

    if triplet_obj is None:
        raise HTTPException(
            status_code=404,
            detail=f"Triplet with id {triplet_id} not found",
        )

    graph_obj = await select_graph_by_description_id(
        description_id=triplet_obj.description_id, session=session
    )

    if graph_obj is None:
        raise HTTPException(
            status_code=500,
            detail=f"Graph for description_id={triplet_obj.description_id} not found",
        )

    await delete_triplet_by_id(id=triplet_id, session=session)

    asyncio.create_task(
        remove_triplet_from_graph(
            graphs_object=graph_obj,
            triplet=TripletData(
                position=triplet_obj.position,
                subject=triplet_obj.subject,
                subject_type=triplet_obj.subject_type,
                predicate=triplet_obj.predicate,
                predicate_type=triplet_obj.predicate_type,
                object=triplet_obj.object,
                object_type=triplet_obj.object_type,
                language=Lang(triplet_obj.language),
            ),
        )
    )


# @router.put(
#     "",
#     status_code=status.HTTP_200_OK,
#     summary="Change triplet",
#     response_model=TripletsResponse,
# )
# async def change_triplet(
#     triplet_id: UUID4, body_obj: Triplet, session: AsyncSession = Depends(get_session)
# ):
#     triplet_obj = await select_triplet_by_id(id=triplet_id, session=session)
#
#     if triplet_obj is None:
#         raise HTTPException(
#             status_code=404,
#             detail=f"Triplet with id {triplet_id} not found",
#         )
#
#     triplet_obj.position = body_obj.data.position
#     triplet_obj.subject = body_obj.data.subject
#     triplet_obj.subject_type = body_obj.data.subject_type
#     triplet_obj.predicate = body_obj.data.predicate
#     triplet_obj.predicate_type = body_obj.data.predicate_type
#     triplet_obj.object = body_obj.data.object
#     triplet_obj.object_type = body_obj.data.object_type
#     triplet_obj.language = body_obj.data.language.value
#
#     triplets_object = await save_triplet(
#         triplet=Triplets(
#             description_id=body_obj.description_id,
#             position=body_obj.data.position,
#             subject=body_obj.data.subject,
#             subject_type=body_obj.data.subject_type,
#             predicate=body_obj.data.predicate,
#             predicate_type=body_obj.data.predicate_type,
#             object=body_obj.data.object,
#             object_type=body_obj.data.object_type,
#             language=body_obj.data.language.value,
#         ),
#         session=session,
#     )
#
#     graphs_object = await select_graph_by_description_id(
#         description_id=body_obj.description_id, session=session
#     )
#
#     if graphs_object is None:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Graphs object with {body_obj.description_id=} not found!",
#         )
#
#     asyncio.create_task(
#         add_triplet_to_graph(
#             graphs_object=graphs_object,
#             triplet=TripletData(
#                 position=triplets_object.position,
#                 subject=triplets_object.subject,
#                 subject_type=triplets_object.subject_type,
#                 predicate=triplets_object.predicate,
#                 predicate_type=triplets_object.predicate_type,
#                 object=triplets_object.object,
#                 object_type=triplets_object.object_type,
#                 language=Lang(triplets_object.language),
#             ),
#         )
#     )
#
#     return TripletsResponse(
#         id=triplets_object.id,
#         triplet=Triplet(
#             description_id=triplets_object.description_id,
#             data=TripletData(
#                 position=triplets_object.position,
#                 subject=triplets_object.subject,
#                 subject_type=triplets_object.subject_type,
#                 predicate=triplets_object.predicate,
#                 predicate_type=triplets_object.predicate_type,
#                 object=triplets_object.object,
#                 object_type=triplets_object.object_type,
#                 language=Lang(triplets_object.language),
#             ),
#         ),
#         created_at=triplets_object.created_at,
#     )


@router.get(
    "/{description_id}",
    status_code=status.HTTP_200_OK,
    summary="Get triplet by description_id",
    response_model=List[TripletsResponse],
)
async def fetch_triplets_by_description_id(
    description_id: UUID4, session: AsyncSession = Depends(get_session)
):
    description_object = await select_description_by_id(
        id=description_id, session=session
    )

    if description_object is None:
        raise HTTPException(
            status_code=404, detail=f"Description with {description_id=} not found!"
        )

    triplets_objects = await select_triplets_by_description_id(
        description_id=description_id, session=session
    )

    return [
        TripletsResponse(
            id=triplets_object.id,
            triplet=Triplet(
                description_id=triplets_object.description_id,
                data=TripletData(
                    position=triplets_object.position,
                    subject=triplets_object.subject,
                    subject_type=triplets_object.subject_type,
                    predicate=triplets_object.predicate,
                    predicate_type=triplets_object.predicate_type,
                    object=triplets_object.object,
                    object_type=triplets_object.object_type,
                    language=Lang(triplets_object.language),
                ),
            ),
            created_at=triplets_object.created_at,
        )
        for triplets_object in triplets_objects
    ]
