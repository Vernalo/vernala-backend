from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LanguageConfig:
    name: str
    lang_code: str  # ISO 639-3 code for African language (e.g., "nnh" for Ngiemboon)
    english_path: str  # URL path for English source (e.g., "browse/browse-english/")
    french_path: str   # URL path for French source (e.g., "browse/francais/")


LANGUAGES: dict[str, LanguageConfig] = {
    "ngiemboon": LanguageConfig(
        name="ngiemboon",
        lang_code="nnh",  # Ngiemboon ISO 639-3 code
        english_path="browse/browse-english/",
        french_path="browse/francais/"
    ),
    "bafut": LanguageConfig(
        name="bafut",
        lang_code="bfd",  # Bafut ISO 639-3 code
        english_path="browse/browse-english/",
        french_path="browse/francais/"
    ),
}
