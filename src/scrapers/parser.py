import re
from bs4 import BeautifulSoup, Tag
from typing import List

from .models import DictionaryEntry, VernacularTranslation


def extract_total_pages(soup: BeautifulSoup) -> int:
    pagination = soup.find("div", id="wp_page_numbers")
    if not pagination:
        return 1

    page_info = pagination.find("li", class_="page_info")
    if not page_info:
        return 1

    match = re.search(r"Page \d+ of (\d+)", page_info.get_text(strip=True))
    return int(match.group(1)) if match else 1


def extract_translations(entry: Tag) -> List[VernacularTranslation]:
    results: List[VernacularTranslation] = []

    for sense in entry.find_all("span", class_="sensesr"):
        headword = sense.find("span", class_="headword")
        if not headword:
            continue

        link_el = headword.find("a")
        if not link_el:
            continue

        parts: list[str] = []
        for span in headword.find_all("span", lang="nnh"):
            for a in span.find_all("a"):
                parts.append(a.get_text(strip=True))

        word = "".join(parts)
        link = link_el.get("href")

        if word and link:
            results.append(VernacularTranslation(word, link))

    return results


def extract_entries(soup: BeautifulSoup) -> List[DictionaryEntry]:
    entries: List[DictionaryEntry] = []

    for post in soup.find_all("div", class_="post"):
        rev = post.find("span", class_="reversalform")
        if not rev:
            continue

        english = rev.get_text(strip=True)
        translations = extract_translations(post)

        if english and translations:
            entries.append(DictionaryEntry(english, translations))

    return entries
