import json
from pathlib import Path
from typing import List

from .models import DictionaryEntry


def save_letter_json(
    language: str,
    letter: str,
    entries: List[DictionaryEntry],
    source_lang: str = "en",
    base_dir: str = "scraped_data",
) -> None:
    lang_dir = Path(base_dir) / language / source_lang
    lang_dir.mkdir(parents=True, exist_ok=True)

    output_file = lang_dir / f"{letter}.json"

    # Use appropriate key based on source language
    source_key = "french" if source_lang == "fr" else "english"

    with output_file.open("w", encoding="utf-8") as f:
        json.dump(
            [
                {
                    source_key: e.source_word,
                    language: [
                        {"word": t.word, "link": t.link}
                        for t in e.translations
                    ],
                }
                for e in entries
            ],
            f,
            ensure_ascii=False,
            indent=2,
        )
