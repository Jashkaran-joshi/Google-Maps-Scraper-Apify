from typing import Any, Dict
from datetime import datetime, timezone

def normalize_business_data(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalizes different variations of raw business data into our stable schema.
    """
    def get_str(keys: list) -> str:
        for k in keys:
            val = raw.get(k)
            if val and isinstance(val, str):
                return val.strip()
        return None
        
    def get_num(keys: list, type_func=float):
        for k in keys:
            val = raw.get(k)
            if val is not None:
                try:
                    return type_func(val)
                except (ValueError, TypeError):
                    pass
        return None

    business_name = get_str(['title', 'businessName', 'name'])
    category = get_str(['categoryName', 'category'])
    address = get_str(['address', 'formattedAddress'])
    city = get_str(['city'])
    state = get_str(['state'])
    country = get_str(['countryCode', 'country'])
    postal_code = get_str(['postalCode', 'zipCode'])
    phone = get_str(['phoneUnformatted', 'phone', 'phoneNumber'])
    website = get_str(['website', 'url'])
    
    rating = get_num(['totalScore', 'rating', 'stars'])
    review_count = get_num(['reviewsCount', 'reviewCount'], int)
    
    google_maps_url = None
    for k in ['url', 'googleMapsUrl', 'placeUrl']:
        val = raw.get(k)
        if val and isinstance(val, str) and ("google.com/maps" in val or "maps.app.goo.gl" in val):
            google_maps_url = val.strip()
            break
            
    # If we didn't find one with google maps in it, let's just grab one if they specifically used googleMapsUrl or placeUrl
    if not google_maps_url:
        google_maps_url = get_str(['googleMapsUrl', 'placeUrl'])

    latitude = get_num(['lat', 'latitude'])
    if latitude is None and raw.get('location'):
        latitude = raw['location'].get('lat')
        
    longitude = get_num(['lng', 'longitude'])
    if longitude is None and raw.get('location'):
        longitude = raw['location'].get('lng')
        
    opening_hours = raw.get('openingHours', {})

    place_id = get_str(['placeId', 'id'])
        
    return {
        "placeId": place_id,
        "businessName": business_name,
        "category": category,
        "address": address,
        "city": city,
        "state": state,
        "country": country,
        "postalCode": postal_code,
        "phone": phone,
        "website": website,
        "rating": rating,
        "reviewCount": review_count,
        "googleMapsUrl": google_maps_url,
        "latitude": latitude,
        "longitude": longitude,
        "openingHours": opening_hours if isinstance(opening_hours, dict) or isinstance(opening_hours, list) else {},
        "source": "google_maps",
        "scrapedAt": datetime.now(timezone.utc).isoformat()
    }
