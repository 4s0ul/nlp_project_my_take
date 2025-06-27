from nltk.data import find


def check_nltk_resource(resource_name: str) -> bool:
    try:
        find(resource_name)
        return True
    except LookupError:
        return False
