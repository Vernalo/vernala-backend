from dataclasses import dataclass
from typing import List


@dataclass(slots=True)
class VernacularTranslation:
    word: str
    link: str


@dataclass(slots=True)
class DictionaryEntry:
    source_word: str  # English or French word being translated
    translations: List[VernacularTranslation]
