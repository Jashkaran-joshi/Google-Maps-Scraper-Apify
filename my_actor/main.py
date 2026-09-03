from __future__ import annotations

import asyncio
from apify import Actor, Event

from .source_client import fetch_source_data
from .normalizer import normalize_business_data

async def main() -> None:
    async with Actor:
        # Handle graceful abort
        async def on_aborting() -> None:
            await asyncio.sleep(1)
            await Actor.exit()

        Actor.on(Event.ABORTING, on_aborting)

        # Retrieve the Actor input
        actor_input = await Actor.get_input() or {}
        search_queries = actor_input.get('searchQueries', [])
        
        if not search_queries:
            Actor.log.error('No searchQueries specified in Actor input, exiting...')
            await Actor.fail(status_message="Missing required input: searchQueries")
            return
            
        max_results = actor_input.get('maxResults', 50)
        include_fields = actor_input.get('includeFields', [])
        min_rating = actor_input.get('minRating', 0)
        require_website = actor_input.get('requireWebsite', False)
        require_phone = actor_input.get('requirePhone', False)
        deduplicate = actor_input.get('deduplicate', True)
        language = actor_input.get('language', 'en')

        Actor.log.info(f"Starting execution for {len(search_queries)} queries.")

        # 1. Fetch raw data using source client
        try:
            raw_items = await fetch_source_data(
                search_queries, 
                max_results, 
                language,
                min_rating,
                require_website,
                require_phone
            )
        except Exception as e:
            Actor.log.error(f"Failed to fetch source data: {e}")
            await Actor.fail(status_message="Source data fetching failed.")
            return

        # 2. Normalize Data
        normalized_items = [normalize_business_data(item) for item in raw_items]
        
        # 3. Filter Data
        filtered_items = []
        for item in normalized_items:
            # Filter by rating
            if min_rating > 0:
                rating = item.get('rating')
                if rating is None or float(rating) < min_rating:
                    continue
                    
            # Filter by website
            if require_website and not item.get('website'):
                continue
                
            # Filter by phone
            if require_phone and not item.get('phone'):
                continue
                
            filtered_items.append(item)
            
        # 4. Deduplicate Data
        final_items = []
        if deduplicate:
            seen_identifiers = set()
            for item in filtered_items:
                identifier = item.get('placeId')
                if not identifier:
                    identifier = item.get('googleMapsUrl')
                if not identifier:
                    name = item.get('businessName') or ""
                    addr = item.get('address') or ""
                    if name and addr:
                        identifier = f"{name.lower()}|{addr.lower()}"
                if not identifier:
                    name = item.get('businessName') or ""
                    phone = item.get('phone') or ""
                    if name and phone:
                        identifier = f"{name.lower()}|{phone.lower()}"
                
                if not identifier or identifier not in seen_identifiers:
                    if identifier:
                        seen_identifiers.add(identifier)
                    final_items.append(item)
        else:
            final_items = filtered_items

        # Apply max_results constraint globally
        if len(final_items) > max_results:
            final_items = final_items[:max_results]
            
        # 5. Clean up missing fields and restrict output fields if requested
        cleaned_items = []
        for item in final_items:
            # Remove keys with None values to avoid inventing data
            cleaned = {k: v for k, v in item.items() if v is not None}
            
            # Apply includeFields filter if specified
            if include_fields and isinstance(include_fields, list) and len(include_fields) > 0:
                cleaned = {k: v for k, v in cleaned.items() if k in include_fields}
                
            cleaned_items.append(cleaned)
            
        # 6. Push final data to Apify Dataset
        if cleaned_items:
            await Actor.push_data(cleaned_items)
            
        Actor.log.info("--- SCRAPE SUMMARY ---")
        Actor.log.info(f"Queries processed: {len(search_queries)}")
        Actor.log.info(f"Records received: {len(raw_items)}")
        Actor.log.info(f"Records filtered: {len(raw_items) - len(filtered_items)}")
        Actor.log.info(f"Duplicates removed: {len(filtered_items) - len(final_items) if deduplicate else 0}")
        Actor.log.info(f"Records saved: {len(cleaned_items)}")
        Actor.log.info("----------------------")
