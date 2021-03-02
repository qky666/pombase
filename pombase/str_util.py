from __future__ import annotations

import re
import unicodedata
import typing


def clean(s: str) -> str:
    s = s.lower()
    s = re.sub('á', 'a', s)
    s = re.sub('é', 'e', s)
    s = re.sub('í', 'i', s)
    s = re.sub('ó', 'o', s)
    s = re.sub('ú', 'u', s)
    s = re.sub('ñ', 'n', s)

    # Invalid characters
    s = re.sub('[^0-9a-zA-Z_]', '_', s)

    # Remove leading characters until we find a letter or underscore
    s = re.sub('^[^a-zA-Z_]+', '', s)

    return s


def normalize_caseless(text: str) -> str:
    return unicodedata.normalize("NFKD", text.casefold())


def caseless_equal(left, right) -> bool:
    return normalize_caseless(left) == normalize_caseless(right)


def caseless_text_in_list(text: str, text_list: typing.List[str]) -> bool:
    normalized_list = [normalize_caseless(t) for t in text_list]
    normalized_text = normalize_caseless(text)
    return normalized_text in normalized_list


def expand_list_replacing_spaces_and_underscores(text_list: typing.List[str]) -> typing.List[str]:
    expanded_list = text_list
    expanded_list = expanded_list + [t.replace("_", " ") for t in text_list]
    expanded_list = expanded_list + [t.replace(" ", "_") for t in text_list]
    expanded_list = list(dict.fromkeys(expanded_list))
    return expanded_list
