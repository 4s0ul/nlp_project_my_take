from enum import Enum
import langid


class Lang(Enum):
    Russian = "russian"
    English = "english"


langid.set_languages(["en", "ru"])


def detect_language(text: str) -> Lang:
    code, _ = langid.classify(text)
    if code == "en":
        return Lang.English
    elif code == "ru":
        return Lang.Russian
    else:
        raise ValueError(f"Unsupported language: {code}")
