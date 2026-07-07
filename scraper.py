import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

def scrape_programs():
    url = "https://www.szelrozsatalalkozo.hu/_programs-ajax"
    try:
        # Fetching all programs in a single request
        r = requests.get(url, params={'pagesize': 1000, 'offset': 0}, timeout=15)
        # Ensure we decode Hungarian characters properly
        r.encoding = 'utf-8'
        if r.status_code != 200:
            print(f"Failed to fetch data, status: {r.status_code}")
            return []
    except Exception as e:
        print(f"Error connecting to website: {e}")
        return []
    
    soup = BeautifulSoup(r.text, 'html.parser')
    posts = soup.find_all('div', class_='post')
    
    parsed_programs = []
    
    for p in posts:
        # 1. ID
        p_id = p.get('data-id')
        if p_id:
            try:
                p_id = int(p_id)
            except ValueError:
                pass
        else:
            continue
            
        # 2. Title
        title_el = p.find('h2')
        title = title_el.text.strip() if title_el else "Ismeretlen program"
        
        # 3. Date / Time
        time_el = p.find('time')
        idopont_str = ""
        if time_el:
            idopont_str = time_el.get('datetime', '')
            if not idopont_str:
                idopont_str = time_el.text.strip()
        
        # Parse datetime to double check formatting
        # Expected format: "2026-07-08 15:30:00"
        if idopont_str:
            # Strip seconds if they exist for clean display
            if len(idopont_str) > 16:
                idopont_str = idopont_str[:16]
        
        # 4. Location
        loc_el = p.find('div', class_='label2')
        location = loc_el.text.strip() if loc_el else "Nincs megadva helyszín"
        
        # 5. Description snippet
        intro_el = p.find('div', class_='intro')
        description = intro_el.text.strip() if intro_el else ""
        # Clean up any residual HTML text
        description = re.sub(r'\s+', ' ', description)
        
        # 6. Tags
        tag_items = p.find_all('li')
        tags = []
        for t in tag_items:
            tag_text = t.text.strip()
            if tag_text.startswith('#'):
                tags.append(tag_text[1:])
            else:
                tags.append(tag_text)
                
        # 7. Duration calculation (tartam_perc)
        duration = 60 # Default
        
        # Search text for mentions of duration
        search_text = f"{title} {description}"
        # Try to find "X perc" or "X perces"
        perc_match = re.search(r'\b(\d+)\s*perc', search_text, re.IGNORECASE)
        if perc_match:
            duration = int(perc_match.group(1))
        else:
            # Try to find "X óra" or "X órás" or "X orás"
            ora_match = re.search(r'\b(\d+)\s*(?:óra|ora)', search_text, re.IGNORECASE)
            if ora_match:
                duration = int(ora_match.group(1)) * 60
            else:
                # Fallbacks based on tags and keywords
                lower_title = title.lower()
                tags_lower = [t.lower() for t in tags]
                
                if any(x in tags_lower for x in ['esti koncert', 'koncert', 'zene', 'komolyzene']) or 'koncert' in lower_title:
                    duration = 90
                elif any(x in tags_lower for x in ['színház', 'színdarab', 'filmklub']) or 'színház' in lower_title or 'filmklub' in lower_title:
                    duration = 90
                elif any(x in tags_lower for x in ['kirándulás', 'sport']) or 'kirándulás' in lower_title or 'túra' in lower_title:
                    duration = 120
                elif 'áhítat' in lower_title or 'ima' in lower_title or lower_title.startswith('reggeli'):
                    duration = 45
        
        parsed_programs.append({
            "id": p_id,
            "nev": title,
            "idopont": idopont_str,
            "tartam_perc": duration,
            "helyszin": location,
            "leiras": description,
            "cimkek": tags,
            "urlpath": p.get('data-urlpath', '')
        })
        
    return parsed_programs

def scrape_full_description(urlpath):
    if not urlpath:
        return "Nincs részletes leírás ehhez a programhoz."
    slug = urlpath.lstrip('/')
    detail_url = f"https://www.szelrozsatalalkozo.hu/programok?slug={slug}"
    try:
        r = requests.get(detail_url, timeout=10)
        r.encoding = 'utf-8'
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            text_el = soup.find('div', class_='openContainer')
            if text_el:
                desc_div = text_el.find('div', class_='text')
                if desc_div:
                    img_opened = desc_div.find('div', class_='imageWrapperOpened')
                    if img_opened:
                        img_opened.decompose()
                    
                    full_text = desc_div.text.strip()
                    full_text = re.sub(r'\s+', ' ', full_text)
                    return full_text
            
            # Fallback 1: search inside main body
            post_inner = soup.find('div', class_='postInner')
            if post_inner:
                paragraphs = post_inner.find_all('p')
                if paragraphs:
                    return "\n\n".join([p.text.strip() for p in paragraphs if p.text.strip()])
                    
            return "Nem sikerült feldolgozni a részletes leírást."
    except Exception as e:
        return f"Hiba a leírás betöltése közben: {e}"
        
    return "Nincs részletes leírás."

if __name__ == "__main__":
    print("Testing scraper...")
    progs = scrape_programs()
    print(f"Scraped {len(progs)} programs.")
    if progs:
        print("\nFirst program details:")
        for k, v in progs[0].items():
            print(f"  {k}: {v}")
        print("\nLast program details:")
        for k, v in progs[-1].items():
            print(f"  {k}: {v}")
