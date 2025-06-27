from typing import List
from nltk.stem.snowball import SnowballStemmer
from dictionary.nlp.languages import Lang


stemmer_map = {
    "english": SnowballStemmer("english"),
    "russian": SnowballStemmer("russian"),
}


def stem_tokens(tokens: List[str], language: Lang) -> List[str]:
    stemmer = stemmer_map[language.value]

    stemmed = [stemmer.stem(token) for token in tokens]

    return stemmed
