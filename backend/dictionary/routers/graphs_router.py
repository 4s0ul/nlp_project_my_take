from pydantic import UUID4
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from dictionary.database.engine import get_session
from dictionary.database.queries import (
    select_description_by_id,
    select_graph_by_description_id,
)
from dictionary.views import Graph, GraphsResponse
from dictionary.nlp.languages import Lang


router = APIRouter(
    prefix="/graphs",
    tags=["Graphs"],
    responses={404: {"description": "Not found"}},
)


@router.get(
    "/{description_id}",
    status_code=status.HTTP_200_OK,
    summary="Get graph by description_id",
    response_model=GraphsResponse,
)
async def fetch_graph_by_description_id(
    description_id: UUID4, session: AsyncSession = Depends(get_session)
):
    description_object = await select_description_by_id(
        id=description_id, session=session
    )

    if description_object is None:
        raise HTTPException(
            status_code=404, detail=f"Description with {description_id=} not found!"
        )

    graphs_object = await select_graph_by_description_id(
        description_id=description_id, session=session
    )
    
    if graphs_object is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Graphs object with {description_id=} not found!",
        )

    return GraphsResponse(
            id=graphs_object.id,
            graph=Graph(
                description_id=graphs_object.description_id,
                triplet_count=graphs_object.triplet_count,
                graph=graphs_object.graph,
                info=graphs_object.info,
                language=Lang(graphs_object.language),
            ),
            created_at=graphs_object.created_at,
        )
