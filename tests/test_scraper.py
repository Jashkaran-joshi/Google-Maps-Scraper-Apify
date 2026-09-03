import unittest
from my_actor.normalizer import normalize_business_data

class TestScraper(unittest.TestCase):
    def test_normalization_and_types(self):
        # Mocked source response
        raw = {
            "title": "Dental Clinic",
            "categoryName": "Dentist",
            "address": "123 Street",
            "rating": "4.5",  # String rating should be converted to float
            "reviewsCount": "12", # String count should be converted to int
            "phoneUnformatted": "+123456789",
            "website": "http://example.com",
            "url": "https://www.google.com/maps/place/xyz",
            "lat": "28.0",
            "lng": 73.3
        }
        
        normalized = normalize_business_data(raw)
        
        self.assertEqual(normalized['businessName'], "Dental Clinic")
        self.assertEqual(normalized['category'], "Dentist")
        self.assertEqual(normalized['address'], "123 Street")
        self.assertEqual(normalized['rating'], 4.5)
        self.assertIsInstance(normalized['rating'], float)
        self.assertEqual(normalized['reviewCount'], 12)
        self.assertIsInstance(normalized['reviewCount'], int)
        self.assertEqual(normalized['phone'], "+123456789")
        self.assertEqual(normalized['website'], "http://example.com")
        self.assertEqual(normalized['googleMapsUrl'], "https://www.google.com/maps/place/xyz")
        self.assertEqual(normalized['latitude'], 28.0)
        self.assertEqual(normalized['longitude'], 73.3)
        self.assertEqual(normalized['source'], "google_maps")
        
    def test_url_normalization(self):
        raw = {
            "url": "https://some-other-site.com/maps", # Not google maps
            "placeUrl": "https://google.com/maps/abc"
        }
        normalized = normalize_business_data(raw)
        self.assertEqual(normalized['googleMapsUrl'], "https://google.com/maps/abc")

    def test_missing_fields(self):
        raw = {
            "title": "Empty Business"
        }
        normalized = normalize_business_data(raw)
        self.assertEqual(normalized['businessName'], "Empty Business")
        self.assertIsNone(normalized['phone'])
        self.assertIsNone(normalized['rating'])
        
    def test_filtering_logic(self):
        # We can't directly test main() since it's an async actor workflow, 
        # but we can test the filtering logic matching exactly what's in main.py
        items = [
            {"businessName": "A", "rating": 3.0, "website": None, "phone": "123"},
            {"businessName": "B", "rating": 4.5, "website": "x.com", "phone": "456"},
            {"businessName": "C", "rating": 5.0, "website": "y.com", "phone": None}
        ]
        
        # Scenario: require website, min rating 4.0
        filtered = [
            item for item in items 
            if item.get('rating') and item['rating'] >= 4.0 and item.get('website')
        ]
        
        self.assertEqual(len(filtered), 2)
        self.assertEqual(filtered[0]['businessName'], "B")
        self.assertEqual(filtered[1]['businessName'], "C")

    def test_deduplication_logic(self):
        items = [
            {"placeId": "1", "businessName": "A"},
            {"placeId": "1", "businessName": "A"},
            {"placeId": None, "googleMapsUrl": "maps/1", "businessName": "B"},
            {"placeId": None, "googleMapsUrl": "maps/1", "businessName": "B_Dup"},
            {"placeId": None, "googleMapsUrl": None, "businessName": "C", "address": "123 St"},
            {"placeId": None, "googleMapsUrl": None, "businessName": "c", "address": "123 st"},
        ]
        
        final_items = []
        seen_identifiers = set()
        for item in items:
            identifier = item.get('placeId')
            if not identifier:
                identifier = item.get('googleMapsUrl')
            if not identifier:
                name = item.get('businessName') or ""
                addr = item.get('address') or ""
                if name and addr:
                    identifier = f"{name.lower()}|{addr.lower()}"
            
            if not identifier or identifier not in seen_identifiers:
                if identifier:
                    seen_identifiers.add(identifier)
                final_items.append(item)
                
        self.assertEqual(len(final_items), 3)
        self.assertEqual(final_items[0]['businessName'], "A")
        self.assertEqual(final_items[1]['businessName'], "B")
        self.assertEqual(final_items[2]['businessName'], "C")

if __name__ == '__main__':
    unittest.main()
