from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LanguageConfig:
    name: str
    base_url: str


LANGUAGES: dict[str, LanguageConfig] = {
    "ngiemboon": LanguageConfig(
        name="ngiemboon",
        base_url="https://www.webonary.org/ngiemboon/browse/browse-english/"
    ),
    "bafut": LanguageConfig(
        name="bafut",
        base_url="https://www.webonary.org/bafut/browse/browse-english/"
    ),
}
