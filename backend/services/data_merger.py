import csv
import json
import logging
import difflib
from collections import defaultdict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataMerger:
    def __init__(self):
        self.all_schools = []
        self.district_map = defaultdict(list)
    
    def load_csv(self, filepath):
        """1. Combine: Loads schools from a CSV dataset"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.all_schools.append({
                        "name": row.get('name', ''),
                        "district": row.get('district', '')
                    })
            logger.info(f"Loaded CSV data from {filepath}")
        except Exception as e:
            logger.error(f"Failed to load CSV {filepath}: {e}")

    def load_json(self, filepath):
        """1. Combine: Loads schools from scraped/OSM json datasets"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.all_schools.extend(data)
            logger.info(f"Loaded JSON data from {filepath}")
        except Exception as e:
            logger.error(f"Failed to load JSON {filepath}: {e}")

    def normalize(self, text):
        """2. Normalize: lowercase and strip"""
        if not text:
            return ""
        return str(text).lower().strip()

    def is_similar(self, name1, name2, threshold=0.85):
        """Fuzzy match logic for deduplication"""
        if name1 == name2:
            return True
        # Calculate string similarity ratio using built-in difflib
        ratio = difflib.SequenceMatcher(None, name1, name2).ratio()
        return ratio >= threshold

    def process(self):
        """Main merging and aggregation pipeline"""
        
        # 2. Normalize inputs
        normalized_schools = []
        for school in self.all_schools:
            normalized_schools.append({
                "name": self.normalize(school.get("name")),
                "district": self.normalize(school.get("district"))
            })

        logger.info(f"Total raw records ready for merging: {len(normalized_schools)}")

        unique_schools = []
        
        # 3. & 4. Group by district directly and deduplicate
        for school in normalized_schools:
            district = school['district']
            name = school['name']
            
            if not district or not name:
                continue

            # 3. Rule: Duplicate if same district AND similar exact/fuzzy name
            is_dup = False
            # We only check against schools already processed in the same district map
            for existing_school in self.district_map[district]:
                if self.is_similar(name, existing_school['name']):
                    is_dup = True
                    break
                    
            if not is_dup:
                self.district_map[district].append(school)
                unique_schools.append(school)

        # 5. Count: Total unique schools
        total_schools = len(unique_schools)
        logger.info(f"Total unique schools after deduplication: {total_schools}")

        # 6. Output: district, schools count
        results = []
        for district, schools in self.district_map.items():
            results.append({
                "district": district,
                "score": 0, # Placeholder for downstream processing
                "schools": len(schools),
                "lat": 0.0, # Placeholder if required by API format later
                "lng": 0.0  # Placeholder if required by API format later
            })
            
        # 7. Ensure: No duplicate districts and no duplicate schools
        # The use of dictionary grouping strictly prevents duplicate districts.
        # The difflib O(N^2) comparison within district subsets strictly prevents duplicate schools.

        return results

    def save_aggregation(self, output_filepath):
        """Utility to dump the final counts to JSON"""
        results = self.process()
        with open(output_filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        logger.info(f"Saved aggregated district counts to {output_filepath}")

if __name__ == "__main__":
    # Example usage
    merger = DataMerger()
    
    # You would pass your specific file paths here:
    # merger.load_csv('path/to/schools.csv')
    # merger.load_json('scraper/osm_schools_data.json')
    # merger.load_json('scraper/schools_org_in_data.json')
    
    # merger.save_aggregation('aggregated_districts.json')
    pass
