from dataclasses import dataclass
from typing import List


@dataclass(slots=True)
class VernacularTranslation:
    word: str
    link: str


@dataclass(slots=True)
class DictionaryEntry:
    english: str
    translations: List[VernacularTranslation]
