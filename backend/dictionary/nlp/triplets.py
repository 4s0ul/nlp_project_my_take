from typing import Optional, List
import stanza
from loguru import logger
from dictionary.nlp.languages import Lang
from pydantic import BaseModel


class TripletData(BaseModel):
    position: int
    subject: str
    subject_type: Optional[str]
    predicate: str
    predicate_type: Optional[str]
    object: str
    object_type: Optional[str]
    language: Lang


for lang_code in ("ru", "en"):
    stanza.download(lang_code, verbose=False)


_nlp_pipelines = {
    Lang.English: stanza.Pipeline(
        lang="en", processors="tokenize,pos,lemma,depparse", use_gpu=False
    ),
    Lang.Russian: stanza.Pipeline(
        lang="ru", processors="tokenize,pos,lemma,depparse", use_gpu=False
    ),
}


def clean_type(t: str) -> Optional[str]:
    return t if t else None


def extract_triplets(text: str, lang: Lang) -> List[TripletData]:
    if lang not in _nlp_pipelines:
        logger.error(f"Unsupported language: {lang}")
        return []

    nlp = _nlp_pipelines[lang]
    doc = nlp(text)
    triplets = []

    for sentence in doc.sentences:
        root = next((w for w in sentence.words if w.head == 0), None)
        if not root:
            continue

        predicate = root.lemma
        predicate_type = clean_type(root.upos)

        subjects = []
        objects = []

        for word in sentence.words:
            if word.head == root.id and word.deprel in ("nsubj", "nsubj:pass"):
                subjects.append((word.text, clean_type(word.upos)))
            elif word.head == root.id and word.deprel in (
                "obj",
                "iobj",
                "obl",
                "xcomp",
                "attr",
            ):
                objects.append((word.text, clean_type(word.upos)))

        for i, (subj_text, subj_type) in enumerate(subjects):
            for obj_text, obj_type in objects:
                triplets.append(
                    TripletData(
                        position=i,
                        subject=subj_text,
                        subject_type=subj_type,
                        predicate=predicate,
                        predicate_type=predicate_type,
                        object=obj_text,
                        object_type=obj_type,
                        language=lang,
                    )
                )

    return triplets
