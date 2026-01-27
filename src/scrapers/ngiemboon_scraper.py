"""
Ngiemboon Dictionary Scraper - Refactored Version
Extracts English words, Ngiemboon translations, and their links
"""

import json
import time
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://www.webonary.org/ngiemboon/browse/browse-english/?letter={letter}&key=en&lang=en"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}


def fetch_page(url: str) -> Optional[BeautifulSoup]:
    """
    Fetch a webpage and return a BeautifulSoup object.
    """
    try:
        print(f"Fetching: {url}")
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        print(f"✓ Status code: {response.status_code}")
        return BeautifulSoup(response.content, 'html.parser')
    except requests.RequestException as e:
        print(f"✗ Error fetching page: {e}")
        return None


def extract_ngiemboon_words(entry: Tag) -> Optional[Dict[str, any]]:
    """
    Extract English word and Ngiemboon translations from a single entry div.
    """
    reversalform = entry.find('span', class_='reversalform')
    if not reversalform:
        return None

    english_word = reversalform.get_text(strip=True)
    ngiemboon_list = []

    sensesr_spans = entry.find_all('span', class_='sensesr')
    for sense in sensesr_spans:
        headword_span = sense.find('span', class_='headword')
        if not headword_span:
            continue

        link_elem = headword_span.find('a')
        if not link_elem:
            continue

        # Combine all sub-span texts to form the Ngiemboon word
        word_parts = [
            a.get_text(strip=True)
            for span in headword_span.find_all('span', lang='nnh')
            for a in span.find_all('a')
        ]
        ngiemboon_word = ''.join(word_parts)
        link = link_elem.get('href')

        if ngiemboon_word and link:
            ngiemboon_list.append({"word": ngiemboon_word, "link": link})

    if not ngiemboon_list:
        return None

    return {"english": english_word, "ngiemboon": ngiemboon_list}


def scrape_ngiemboon_dictionary(url: str) -> List[Dict[str, any]]:
    """
    Scrape the Ngiemboon dictionary page for English-Ngiemboon pairs.
    """
    soup = fetch_page(url)
    if not soup:
        return []

    # Optional: save HTML for debugging
    with open('page_source.html', 'w', encoding='utf-8') as f:
        f.write(soup.prettify())

    entries = soup.find_all('div', class_='post')
    print(f"✓ Found {len(entries)} entries")

    words = []
    for i, entry in enumerate(entries):
        try:
            data = extract_ngiemboon_words(entry)
            if data:
                words.append(data)
                if i < 3:  # Show first 3 entries for debugging
                    print(f"\nEntry {i + 1}: English: {data['english']}")
                    for ng in data['ngiemboon']:
                        print(f"  • {ng['word']}: {ng['link']}")
        except Exception as e:
            print(f"✗ Error processing entry {i}: {e}")
            continue

    print(f"\n✓ Successfully extracted {len(words)} word pairs")
    return words


def scrape_letter(letter: str) -> List[Dict[str, any]]:
    """
    Scrape words for a single letter.
    """
    url = BASE_URL.format(letter=letter)
    return scrape_ngiemboon_dictionary(url)


def scrape_all_letters() -> List[Dict[str, any]]:
    """
    Scrape all letters from a-z.
    """
    all_words: List[Dict[str, any]] = []
    print("\n🚀 Scraping all letters (A-Z)...")

    for letter in 'abcdefghijklmnopqrstuvwxyz':
        print(f"\n{'─'*50}\nLetter: {letter.upper()}\n{'─'*50}")
        words = scrape_letter(letter)
        if words:
            print(f"✓ Extracted {len(words)} words for letter '{letter}'")
            all_words.extend(words)
        else:
            print(f"⚠ No words found for letter '{letter}'")
        time.sleep(2)  # Be polite to the server

    return all_words


def save_json(data: List[Dict[str, any]], filename: str):
    """
    Save extracted words to a JSON file.
    """
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✓ Saved to: {filename}")