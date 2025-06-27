import re
import string
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from dictionary.nlp.languages import Lang


stopwords_map = {
    "english": set(stopwords.words("english")),
    "russian": set(stopwords.words("russian")),
}


def clean_text(text: str, language: Lang) -> list[str]:
    text = text.lower()
    text = re.sub(r"[^a-zа-яё\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()

    tokens = word_tokenize(text, language=language.value)
    stop_words = stopwords_map[language.value]

    cleaned = [
        token
        for token in tokens
        if token not in stop_words and token not in string.punctuation
    ]

    return cleaned
