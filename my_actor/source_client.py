import os
from apify import Actor
from typing import Any, Dict, List

async def fetch_source_data(
    queries: List[str], 
    max_results: int, 
    language: str
) -> List[Dict[str, Any]]:
    """
    Calls an external reliable Google Maps Apify Actor to fetch the raw business data.
    """
    source_actor_id = os.getenv('SOURCE_ACTOR_ID', 'compass/crawler-google-places')
    
    Actor.log.info(f"Calling source Actor: {source_actor_id} with {len(queries)} queries.")
    
    # Prepare input for standard Google Maps scrapers on Apify
    # Providing both searchStringsArray and searchQueries ensures compatibility
    # with multiple standard implementations.
    run_input = {
        "searchStringsArray": queries,
        "searchQueries": queries, 
        "maxCrawledPlacesPerSearch": max_results,
        "maxResults": max_results,
        "language": language,
    }
    
    apify_client = Actor.apify_client
    
    try:
        run = await apify_client.actor(source_actor_id).call(run_input=run_input)
        
        if run is None or run.get('status') != 'SUCCEEDED':
            Actor.log.error(f"Source Actor run failed or was aborted: {run}")
            raise Exception("Source Actor failed to complete successfully.")
            
        default_dataset_id = run['defaultDatasetId']
        
        # Fetch the results from the source dataset
        dataset_items = await apify_client.dataset(default_dataset_id).list_items()
        
        items = dataset_items.items
        Actor.log.info(f"Successfully retrieved {len(items)} items from source Actor.")
        return items
        
    except Exception as e:
        Actor.log.error(f"Error fetching data from source Actor: {e}")
        raise
