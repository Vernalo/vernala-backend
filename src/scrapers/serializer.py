import json
from pathlib import Path
from typing import List

from .models import DictionaryEntry


def save_letter_json(
    language: str,
    letter: str,
    entries: List[DictionaryEntry],
    base_dir: str = "scraped_data",
) -> None:
    lang_dir = Path(base_dir) / language
    lang_dir.mkdir(parents=True, exist_ok=True)

    output_file = lang_dir / f"{letter}.json"

    with output_file.open("w", encoding="utf-8") as f:
        json.dump(
            [
                {
                    "english": e.english,
                    "ngiemboon": [
                        {"word": t.word, "link": t.link}
                        for t in e.ngiemboon
                    ],
                }
                for e in entries
            ],
            f,
            ensure_ascii=False,
            indent=2,
        )
