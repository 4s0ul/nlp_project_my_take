from loguru import logger
from typing import Optional, List
import spacy
from dictionary.nlp.languages import Lang
from pydantic import BaseModel


_nlp_en = None
_nlp_ru = None


def _get_nlp(lang: Lang) -> Optional[spacy.language.Language]:
    global _nlp_en, _nlp_ru

    try:
        if lang == Lang.English:
            if _nlp_en is None:
                _nlp_en = spacy.load("en_core_web_md")
                logger.info("en_core_web_md loaded successfully!")
            return _nlp_en

        elif lang == Lang.Russian:
            if _nlp_ru is None:
                _nlp_ru = spacy.load("ru_core_news_md")
                logger.info("ru_core_news_md loaded successfully!")
            return _nlp_ru

    except Exception as e:
        logger.error(f"Failed to load spaCy model for {lang=}: {e}")
        return None

    raise ValueError(f"Unsupported language: {lang}")


def vectorize_text(text: str, lang: Lang) -> Optional[List[float]]:
    nlp = _get_nlp(lang=lang)
    if not nlp:
        logger.error(f"Failed to vectorize {text=}")
        return None
    return nlp(text).vector.tolist()
