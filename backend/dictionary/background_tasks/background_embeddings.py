from loguru import logger
from pydantic import UUID4
from dictionary.database.engine import async_session
from dictionary.database.models import Embeddings
from dictionary.nlp.languages import Lang
from dictionary.database.queries import save_embedding, select_embedding_by_description_id
from dictionary.nlp.embeddings import vectorize_text


async def create_embedding(text: str, lang: Lang, description_id: UUID4) -> None:
    embedding = vectorize_text(text=text, lang=lang)

    if not embedding:
        logger.error(f"Couldn't vectorize {text=}")
        return

    async with async_session() as session:
        await save_embedding(
            embedding=Embeddings(
                description_id=description_id, embedding=embedding, language=lang.value
            ),
            session=session,
        )


async def update_embedding(text: str, lang: Lang, description_id: UUID4) -> None:
    embedding = vectorize_text(text=text, lang=lang)

    if not embedding:
        logger.error(f"Couldn't vectorize {text=}")
        return

    async with async_session() as session:
        embeddings_object = await select_embedding_by_description_id(description_id=description_id, session=session)
        if not embeddings_object:
            logger.error(f"No embedding for description with {description_id=}")
            return
        embeddings_object.embedding = embedding
        await save_embedding(
            embedding=embeddings_object,
            session=session,
        )
