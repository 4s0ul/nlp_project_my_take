from loguru import logger
from pydantic import UUID4
from dictionary.database.engine import async_session
from dictionary.database.models import Triplets, Graphs
from dictionary.nlp.languages import Lang
from dictionary.database.queries import save_triplet, save_graph, select_graph_by_description_id, delete_triplets_by_description_id
from dictionary.nlp.triplets import extract_triplets, TripletData
from dictionary.nlp.graphs import (
    create_graph,
    add_triplets_to_graph,
    remove_triplets_from_graph,
    serialize_graph,
    deserialize_graph,
)


async def create_triplets_and_graphs(
    text: str, lang: Lang, description_id: UUID4
) -> None:
    triplets = extract_triplets(text=text, lang=lang)

    if not triplets:
        logger.error(f"Couldn't extract triplets from {text=}")

    graph = await create_graph()
    graph = await add_triplets_to_graph(graph=graph, triplets=triplets)
    serialized_graph = await serialize_graph(graph)

    async with async_session() as session:
        await save_graph(
            Graphs(
                description_id=description_id,
                triplet_count=len(triplets),
                graph=serialized_graph,
                language=lang.value,
            ),
            session=session,
        )

        for triplet in triplets:
            logger.info(triplet)
            await save_triplet(
                triplet=Triplets(
                    description_id=description_id,
                    position=triplet.position,
                    subject=triplet.subject,
                    subject_type=triplet.subject_type,
                    predicate=triplet.predicate,
                    predicate_type=triplet.predicate_type,
                    object=triplet.object,
                    object_type=triplet.object_type,
                    language=lang.value,
                ),
                session=session,
            )


async def update_triplets_and_graphs(
    text: str, lang: Lang, description_id: UUID4
) -> None:
    triplets = extract_triplets(text=text, lang=lang)

    if not triplets:
        logger.error(f"Couldn't extract triplets from {text=}")

    graph = await create_graph()
    graph = await add_triplets_to_graph(graph=graph, triplets=triplets)
    serialized_graph = await serialize_graph(graph)

    async with async_session() as session:
        graphs_object = await select_graph_by_description_id(description_id=description_id, session=session)
        if not graphs_object:
            logger.error(f"No embedding for description with {description_id=}")
            return
        graphs_object.graph = serialized_graph
        await save_graph(graph=graphs_object, session=session)

        await delete_triplets_by_description_id(description_id=description_id, session=session)
        for triplet in triplets:
            logger.info(triplet)
            await save_triplet(
                triplet=Triplets(
                    description_id=description_id,
                    position=triplet.position,
                    subject=triplet.subject,
                    subject_type=triplet.subject_type,
                    predicate=triplet.predicate,
                    predicate_type=triplet.predicate_type,
                    object=triplet.object,
                    object_type=triplet.object_type,
                    language=lang.value,
                ),
                session=session,
            )


async def add_triplet_to_graph(graphs_object: Graphs, triplet: TripletData) -> None:
    graph = await deserialize_graph(graph_data=graphs_object.graph)
    graph = await add_triplets_to_graph(graph=graph, triplets=[triplet])

    graphs_object.graph = await serialize_graph(graph)
    graphs_object.triplet_count += 1

    async with async_session() as session:
        session.add(graphs_object)
        await session.commit()
        await session.refresh(graphs_object)


async def remove_triplet_from_graph(
    graphs_object: Graphs, triplet: TripletData
) -> None:
    graph = await deserialize_graph(graph_data=graphs_object.graph)
    graph = await remove_triplets_from_graph(graph=graph, triplets=[triplet])

    graphs_object.graph = await serialize_graph(graph)
    graphs_object.triplet_count -= 1

    async with async_session() as session:
        session.add(graphs_object)
        await session.commit()
        await session.refresh(graphs_object)
