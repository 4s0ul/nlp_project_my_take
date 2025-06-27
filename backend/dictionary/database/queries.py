from typing import Sequence, Optional
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from dictionary.database.models import (
    Topics,
    Terms,
    Descriptions,
    Embeddings,
    Triplets,
    Graphs,
)


async def save_topic(topic: Topics, session: AsyncSession) -> Topics:
    session.add(topic)
    await session.commit()
    await session.refresh(topic)
    return topic


async def select_topic_by_name(
    topic_name: str, session: AsyncSession
) -> Optional[Topics]:
    statement = (
        select(Topics)
        .where(
            Topics.name == topic_name,
        )
        .limit(1)
    )
    result = await session.execute(statement)
    return result.scalars().first()


async def select_topic_by_id(
    topic_id: UUID4, session: AsyncSession
) -> Optional[Topics]:
    statement = (
        select(Topics)
        .where(
            Topics.id == topic_id,
        )
        .limit(1)
    )
    result = await session.execute(statement)
    return result.scalars().first()


async def select_all_topics(session: AsyncSession) -> Sequence[Topics]:
    statement = select(Topics)
    result = await session.execute(statement)
    return result.scalars().all()


async def save_term(term: Terms, session: AsyncSession) -> Terms:
    session.add(term)
    await session.commit()
    await session.refresh(term)
    return term


async def select_term_by_raw_test(
    raw_text: str, session: AsyncSession
) -> Optional[Terms]:
    statement = (
        select(Terms)
        .where(
            Terms.raw_text == raw_text,
        )
        .limit(1)
    )
    result = await session.execute(statement)
    return result.scalars().first()


async def select_term_by_cleaned_text(
    cleaned_text: str, session: AsyncSession
) -> Optional[Terms]:
    statement = (
        select(Terms)
        .where(
            Terms.cleaned_text == cleaned_text,
        )
        .limit(1)
    )
    result = await session.execute(statement)
    return result.scalars().first()


async def select_term_by_stemmed_text(
    stemmed_text: str, session: AsyncSession
) -> Optional[Terms]:
    statement = (
        select(Terms)
        .where(
            Terms.stemmed_text == stemmed_text,
        )
        .limit(1)
    )
    result = await session.execute(statement)
    return result.scalars().first()


async def select_terms_by_first_letter(
    first_letter: str, topic_id: UUID4, limit: int, session: AsyncSession
) -> Sequence[Terms]:
    statement = (
        select(Terms)
        .where(
            Terms.first_letter == first_letter,
        )
        .where(Terms.topic_id == topic_id)
        .limit(limit)
    )
    result = await session.execute(statement)
    return result.scalars().all()


async def select_term_by_id(id: UUID4, session: AsyncSession) -> Optional[Terms]:
    statement = (
        select(Terms)
        .where(
            Terms.id == id,
        )
        .limit(1)
    )
    result = await session.execute(statement)
    return result.scalars().first()


async def delete_term_by_id(id: UUID4, session: AsyncSession) -> bool:
    term = await select_term_by_id(id=id, session=session)
    if not term:
        return False

    desc_stmt = select(Descriptions).where(Descriptions.term_id == id)
    desc_result = await session.execute(desc_stmt)
    description = desc_result.scalars().first()

    if description:
        emb_stmt = select(Embeddings).where(Embeddings.description_id == description.id)
        emb_result = await session.execute(emb_stmt)
        embedding = emb_result.scalars().first()
        if embedding:
            await session.delete(embedding)

        trip_stmt = select(Triplets).where(Triplets.description_id == description.id)
        trip_result = await session.execute(trip_stmt)
        triplets = trip_result.scalars().all()
        for triplet in triplets:
            await session.delete(triplet)

        graph_stmt = select(Graphs).where(Graphs.description_id == description.id)
        graph_result = await session.execute(graph_stmt)
        graph = graph_result.scalars().first()
        if graph:
            await session.delete(graph)

        await session.flush()

        await session.delete(description)

    await session.delete(term)
    await session.commit()
    return True


async def delete_topic_by_id(topic_id: UUID4, session: AsyncSession) -> bool:
    topic = await select_topic_by_id(topic_id=topic_id, session=session)
    if not topic:
        return False

    terms_stmt = select(Terms).where(Terms.topic_id == topic_id)
    terms_result = await session.execute(terms_stmt)
    terms = terms_result.scalars().all()

    for term in terms:
        await delete_term_by_id(term.id, session=session)

    await session.delete(topic)
    await session.commit()
    return True


async def save_description(
    description: Descriptions, session: AsyncSession
) -> Descriptions:
    session.add(description)
    await session.commit()
    await session.refresh(description)
    return description


async def select_description_by_raw_text(
    raw_text: str, session: AsyncSession
) -> Optional[Descriptions]:
    statement = (
        select(Descriptions)
        .where(
            Descriptions.raw_text == raw_text,
        )
        .limit(1)
    )
    result = await session.execute(statement)
    return result.scalars().first()


async def select_description_by_cleaned_text(
    cleaned_text: str, session: AsyncSession
) -> Optional[Descriptions]:
    statement = (
        select(Descriptions)
        .where(
            Descriptions.cleaned_text == cleaned_text,
        )
        .limit(1)
    )
    result = await session.execute(statement)
    return result.scalars().first()


async def select_description_by_stemmed_text(
    stemmed_text: str, session: AsyncSession
) -> Optional[Descriptions]:
    statement = (
        select(Descriptions)
        .where(
            Descriptions.stemmed_text == stemmed_text,
        )
        .limit(1)
    )
    result = await session.execute(statement)
    return result.scalars().first()


async def select_description_by_id(
    id: UUID4, session: AsyncSession
) -> Optional[Descriptions]:
    statement = (
        select(Descriptions)
        .where(
            Descriptions.id == id,
        )
        .limit(1)
    )
    result = await session.execute(statement)
    return result.scalars().first()


async def select_description_by_term_id(
    term_id: UUID4, session: AsyncSession
) -> Optional[Descriptions]:
    statement = (
        select(Descriptions)
        .where(
            Descriptions.term_id == term_id,
        )
        .limit(1)
    )
    result = await session.execute(statement)
    return result.scalars().first()


async def save_embedding(embedding: Embeddings, session: AsyncSession) -> Embeddings:
    session.add(embedding)
    await session.commit()
    await session.refresh(embedding)
    return embedding


async def select_embedding_by_description_id(description_id: UUID4, session: AsyncSession) -> Optional[Embeddings]:
    statement = (
        select(Embeddings)
        .where(
            Embeddings.description_id == description_id,
        )
        .limit(1)
    )
    result = await session.execute(statement)
    return result.scalars().first()


async def delete_embedding_by_description_id(description_id: UUID4, session: AsyncSession) -> bool:
    embedding = await select_embedding_by_description_id(description_id=description_id, session=session)
    if not embedding:
        return False
    await session.delete(embedding)
    await session.commit()
    return True


async def save_triplet(triplet: Triplets, session: AsyncSession) -> Triplets:
    session.add(triplet)
    await session.commit()
    await session.refresh(triplet)
    return triplet


async def select_triplet_by_id(id: UUID4, session: AsyncSession) -> Optional[Triplets]:
    statement = (
        select(Triplets)
        .where(
            Triplets.id == id,
        )
        .limit(1)
    )
    result = await session.execute(statement)
    return result.scalars().first()


async def delete_triplet_by_id(id: UUID4, session: AsyncSession) -> bool:
    triplet = await select_triplet_by_id(id=id, session=session)
    if not triplet:
        return False
    await session.delete(triplet)
    await session.commit()
    return True


async def delete_triplets_by_description_id(description_id: UUID4, session: AsyncSession) -> bool:
    triplets = await select_triplets_by_description_id(description_id=description_id, session=session)
    if not triplets:
        return False
    for triplet in triplets:
        await session.delete(triplet)
        await session.commit()
    return True


async def select_triplets_by_description_id(
    description_id: UUID4, session: AsyncSession
) -> Sequence[Triplets]:
    statement = select(Triplets).where(
        Triplets.description_id == description_id,
    )
    result = await session.execute(statement)
    return result.scalars().all()


async def save_graph(graph: Graphs, session: AsyncSession) -> Graphs:
    session.add(graph)
    await session.commit()
    await session.refresh(graph)
    return graph


async def select_graph_by_description_id(
    description_id: UUID4, session: AsyncSession
) -> Optional[Graphs]:
    statement = (
        select(Graphs)
        .where(
            Graphs.description_id == description_id,
        )
        .limit(1)
    )
    result = await session.execute(statement)
    return result.scalars().first()
