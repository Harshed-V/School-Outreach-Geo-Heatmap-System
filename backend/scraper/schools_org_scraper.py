import requests
from bs4 import BeautifulSoup
import time
import json
import logging
from urllib.parse import urljoin

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SchoolsOrgScraper:
    def __init__(self):
        self.base_url = "https://schools.org.in/"
        self.start_url = "https://schools.org.in/tamil-nadu/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.results = []

    def normalize_district(self, name):
        """Normalize district names for consistency"""
        if not name:
            return ""
        name = name.lower().replace("the ", "").strip()
        if name.endswith(' district'):
            name = name[:-9].strip()
        return name

    def get_soup(self, url):
        """Fetch URL with delay and parse with BeautifulSoup"""
        try:
            logger.info(f"Fetching: {url}")
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            time.sleep(0.5)  # 8. Avoid blocking: add delay
            return BeautifulSoup(response.content, 'html.parser')
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            time.sleep(2)  # Back off on error
            return None

    def extract_district_links(self):
        """Extract all district links from the main Tamil Nadu page"""
        soup = self.get_soup(self.start_url)
        if not soup:
            return []

        district_links = []
        # Usually, district links are contained within table rows or specific list structures.
        # This targets generic anchor tags that point to district subpages.
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            # Assuming district links look like /tamil-nadu/district-name/ or similar
            if '/tamil-nadu/' in href and href != self.start_url and href != '/tamil-nadu':
                full_url = urljoin(self.base_url, href)
                district_name = a_tag.text.strip()
                if district_name and full_url not in [d['url'] for d in district_links]:
                    district_links.append({
                        'name': self.normalize_district(district_name),
                        'url': full_url
                    })
        
        logger.info(f"Found {len(district_links)} district links.")
        return district_links

    def extract_schools_from_page(self, soup, district_name):
        """Extract school data from a single district/block page"""
        schools = []
        # Assuming schools are listed in a table, list, or div cards.
        # This is a generalized extraction targeting common structures on schools.org.in
        school_elements = soup.find_all(['tr', 'div'], class_=lambda x: x and ('school' in x.lower() or 'list' in x.lower()))
        
        # If the above doesn't work, fallback to finding links that look like school profiles
        if not school_elements:
            for a_tag in soup.find_all('a', href=True):
                # School profiles typically have a UDISE code or specific pattern
                if a_tag.text and len(a_tag.text) > 5 and ('school' in a_tag.text.lower() or 'vidyalaya' in a_tag.text.lower()):
                    schools.append({
                        "name": a_tag.text.strip(),
                        "district": district_name
                    })
        else:
            for el in school_elements:
                name_tag = el.find('a')
                if name_tag and name_tag.text:
                    schools.append({
                        "name": name_tag.text.strip(),
                        "district": district_name
                    })
                    
        return schools

    def scrape_district(self, district):
        """Scrape all schools for a given district, handling pagination"""
        current_url = district['url']
        
        while current_url:
            soup = self.get_soup(current_url)
            if not soup:
                break
                
            schools = self.extract_schools_from_page(soup, district['name'])
            self.results.extend(schools)
            logger.info(f"Extracted {len(schools)} schools from {district['name']} page.")
            
            # 7. Handle pagination if present
            next_link = soup.find('a', string=lambda t: t and 'next' in t.lower())
            if next_link and next_link.get('href'):
                current_url = urljoin(self.base_url, next_link['href'])
            else:
                # Alternative pagination check
                pagination = soup.find('ul', class_='pagination')
                if pagination:
                    active = pagination.find('li', class_='active')
                    if active and active.find_next_sibling('li'):
                        next_a = active.find_next_sibling('li').find('a')
                        if next_a and next_a.get('href'):
                            current_url = urljoin(self.base_url, next_a['href'])
                            continue
                current_url = None

    def run(self):
        """Main execution flow"""
        logger.info("Starting schools.org.in scraper...")
        districts = self.extract_district_links()
        
        for idx, district in enumerate(districts):
            logger.info(f"Scraping district {idx+1}/{len(districts)}: {district['name']}")
            self.scrape_district(district)
            
        self.save_results()

    def save_results(self):
        """Save extracted data to JSON"""
        output_file = 'schools_org_in_data.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        logger.info(f"Scraping complete. Saved {len(self.results)} schools to {output_file}")

if __name__ == "__main__":
    scraper = SchoolsOrgScraper()
    scraper.run()
