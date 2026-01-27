"""
Ngiemboon Dictionary Scraper - With Pagination Support
Extracts all pages for each letter
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re

def scrape_ngiemboon_page(url):
    """
    Scrape a single page and extract word entries
    Returns: (words_list, total_pages)
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        words = []
        
        # Find all post divs (word entries)
        entries = soup.find_all('div', class_='post')
        
        for entry in entries:
            try:
                # Extract English word
                reversalform = entry.find('span', class_='reversalform')
                if not reversalform:
                    continue
                
                english = reversalform.get_text(strip=True)
                
                # Extract all Ngiemboon translations
                ngiemboon_list = []
                sensesr_spans = entry.find_all('span', class_='sensesr')
                
                for sense in sensesr_spans:
                    headword_span = sense.find('span', class_='headword')
                    if not headword_span:
                        continue
                    
                    link_elem = headword_span.find('a')
                    if link_elem:
                        # Get the Ngiemboon word
                        word_parts = []
                        for span in headword_span.find_all('span', lang='nnh'):
                            for a in span.find_all('a'):
                                word_parts.append(a.get_text(strip=True))
                        
                        ngiemboon_word = ''.join(word_parts)
                        link = link_elem.get('href')
                        
                        if ngiemboon_word and link:
                            ngiemboon_list.append({
                                'word': ngiemboon_word,
                                'link': link
                            })
                
                if english and ngiemboon_list:
                    words.append({
                        'english': english,
                        'ngiemboon': ngiemboon_list
                    })
            
            except Exception as e:
                print(f"    ✗ Error processing entry: {e}")
                continue
        
        # Detect total number of pages
        total_pages = 1
        pagination = soup.find('div', id='wp_page_numbers')
        if pagination:
            # Look for "Page X of Y" text
            page_info = pagination.find('li', class_='page_info')
            if page_info:
                text = page_info.get_text(strip=True)
                # Extract "Page 1 of 16" -> 16
                match = re.search(r'Page \d+ of (\d+)', text)
                if match:
                    total_pages = int(match.group(1))
        
        return words, total_pages
    
    except requests.exceptions.RequestException as e:
        print(f"    ✗ Error fetching page: {e}")
        return [], 1

def scrape_letter_all_pages(letter):
    """
    Scrape all pages for a given letter
    """
    base_url = "https://www.webonary.org/ngiemboon/browse/browse-english/?letter={letter}&key=en&pagenr={page}&lang=en"
    
    print(f"\n{'─'*70}")
    print(f"Letter: {letter.upper()}")
    print(f"{'─'*70}")
    
    # First, get page 1 to determine total pages
    first_url = base_url.format(letter=letter, page=1)
    print(f"  Fetching page 1...")
    
    all_words, total_pages = scrape_ngiemboon_page(first_url)
    
    if not all_words:
        print(f"  ⚠ No words found for letter '{letter}'")
        return []
    
    print(f"  ✓ Page 1/{total_pages}: Found {len(all_words)} words")
    
    # If there are more pages, fetch them
    if total_pages > 1:
        print(f"  📄 Letter '{letter}' has {total_pages} pages total")
        
        for page_num in range(2, total_pages + 1):
            page_url = base_url.format(letter=letter, page=page_num)
            print(f"  Fetching page {page_num}/{total_pages}...")
            
            words, _ = scrape_ngiemboon_page(page_url)
            
            if words:
                print(f"  ✓ Page {page_num}/{total_pages}: Found {len(words)} words")
                all_words.extend(words)
            else:
                print(f"  ⚠ Page {page_num}/{total_pages}: No words found")
            
            # Be polite - small delay between pages
            time.sleep(1)
    
    print(f"  ✅ Total for '{letter}': {len(all_words)} words")
    return all_words

def scrape_all_letters():
    """
    Scrape all letters from a-z, handling pagination
    """
    all_words = []
    
    print("\n" + "="*70)
    print("SCRAPING ALL LETTERS (A-Z) WITH PAGINATION")
    print("="*70)
    
    for letter in 'abcdefghijklmnopqrstuvwxyz':
        words = scrape_letter_all_pages(letter)
        
        if words:
            all_words.extend(words)
        
        # Be polite - delay between letters
        time.sleep(2)
    
    return all_words

def scrape_ngiemboon():
    print("="*70)
    print("NGIEMBOON DICTIONARY SCRAPER WITH PAGINATION")
    print("="*70)
    
    # Test with letter 'a' first (which has multiple pages)
    print("\n📖 Testing with letter 'a' (all pages)...")
    
    words = scrape_letter_all_pages('a')
    
    if words and len(words) > 0:
        print("\n" + "="*70)
        print(f"✓ SUCCESS! Extracted {len(words)} word pairs for letter 'a'")
        print("="*70)
        
        # Show first 5 examples
        print("\n📝 First 5 entries:")
        print("─"*70)
        for i, word in enumerate(words[:5], 1):
            print(f"\n{i}. English: {word['english']}")
            print(f"   Ngiemboon translations:")
            for ng in word['ngiemboon']:
                print(f"     • {ng['word']}")
                print(f"       → {ng['link']}")
        
        if len(words) > 5:
            print(f"\n    ... and {len(words) - 5} more entries")
        
        # Save letter 'a' results
        output_file = 'scraped_data/ngiemboon/letter_a.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(words, f, ensure_ascii=False, indent=2)
        print(f"\n✓ Saved to: {output_file}")
        
        # Ask about continuing
        print("\n" + "="*70)
        print("Would you like to scrape all letters (a-z)?")
        print("This will take several minutes (depends on total pages)")
        print("="*70)
        response = input("Continue? (y/n): ").strip().lower()
        
        if response == 'y':
            print("\n🚀 Starting full dictionary scrape...")
            all_words = scrape_all_letters()
            
            if all_words:
                output_file = 'scraped_data/ngiemboon/complete_dictionary.json'
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(all_words, f, ensure_ascii=False, indent=2)
                
                print("\n" + "="*70)
                print(f"✓ COMPLETE! Total words extracted: {len(all_words)}")
                print(f"✓ Saved to: {output_file}")
                print("="*70)
                
                # Statistics
                letters_count = {}
                total_translations = 0
                for word in all_words:
                    first_letter = word['english'][0].lower()
                    letters_count[first_letter] = letters_count.get(first_letter, 0) + 1
                    total_translations += len(word['ngiemboon'])
                
                print(f"\n📊 Statistics:")
                print(f"   Total English entries: {len(all_words)}")
                print(f"   Total Ngiemboon translations: {total_translations}")
                print(f"\n📊 Words per letter:")
                for letter in 'abcdefghijklmnopqrstuvwxyz':
                    count = letters_count.get(letter, 0)
                    if count > 0:
                        print(f"   {letter.upper()}: {count:3d} words")
        else:
            print("\n👍 Okay, stopping here. You have all pages for letter 'a'.")
    
    else:
        print("\n" + "="*70)
        print("✗ FAILED - Could not extract words")
        print("="*70)
        print("\n🔍 Please check your internet connection and try again")