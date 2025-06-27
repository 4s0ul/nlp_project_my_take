from typing import Optional, List
from pydantic import BaseModel
import stanza
from loguru import logger
from dictionary.nlp.languages import Lang


class Triplet(BaseModel):
    position: int
    subject: str
    subject_type: Optional[str]
    predicate: str
    predicate_type: Optional[str]
    object: str
    object_type: Optional[str]


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


def extract_triplets(text: str, lang: Lang) -> List[Triplet]:
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
                    Triplet(
                        position=i,
                        subject=subj_text,
                        subject_type=subj_type,
                        predicate=predicate,
                        predicate_type=predicate_type,
                        object=obj_text,
                        object_type=obj_type,
                    )
                )

    return triplets


if __name__ == "__main__":
    sample_text = "Дороги в Эквадоре практически идеальные, хотя населенные пункты выглядят очень бедно. На дорогах много интересных машин, например очень много грузовиков - древних Фордов, которые я никогда раньше не видел. А еще несколько раз на глаза попадались старенькие Жигули :) А еще если кого-то обгоняешь и есть встречная машина, она обязательно включает фары. На больших машинах - грузовиках и автобусах, обязательно красуется местный тюнинг: машины разукрашенные, либо в наклейках, и обязательно везде огромное множество светодиодов, как будто новогодние елки едут и переливаются всеми цветами."
    triplets = extract_triplets(text=sample_text, lang=Lang.Russian)
    for triplet in triplets:
        print(triplet)
