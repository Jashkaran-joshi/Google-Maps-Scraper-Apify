import os
from apify import Actor
from typing import Any, Dict, List

async def fetch_source_data(
    queries: List[str], 
    max_results: int, 
    language: str,
    min_rating: float = 0,
    require_website: bool = False,
    require_phone: bool = False
) -> List[Dict[str, Any]]:
    """
    Calls an external reliable Google Maps Apify Actor to fetch the raw business data.
    """
    source_actor_id = os.getenv('SOURCE_ACTOR_ID', 'compass/crawler-google-places')
    
    Actor.log.info(f"Calling source Actor: {source_actor_id} with {len(queries)} queries.")
    
    # Calculate a reasonable upstream limit to ensure we have enough after filtering
    multiplier = 1.0
    if min_rating > 4.0: multiplier *= 2.5
    elif min_rating > 0: multiplier *= 1.5
    if require_website: multiplier *= 1.5
    if require_phone: multiplier *= 1.2
    
    upstream_max = int(max_results * multiplier)
    
    # Put a hard ceiling to prevent massive accidental API charges
    if upstream_max > max_results * 5:
        upstream_max = max_results * 5
        
    if upstream_max != max_results:
        Actor.log.info(f"Filters applied. Requesting up to {upstream_max} records upstream to return {max_results} matching ones.")
    
    # Prepare input for standard Google Maps scrapers on Apify
    run_input = {
        "searchStringsArray": queries,
        "searchQueries": queries, 
        "maxCrawledPlacesPerSearch": upstream_max,
        "maxResults": upstream_max,
        "language": language,
    }
    
    apify_client = Actor.apify_client
    
    try:
        run = await apify_client.actor(source_actor_id).call(run_input=run_input)
        
        if run is None:
            raise Exception("Source Actor run is None.")
            
        status = getattr(run, 'status', None) or (run.get('status') if isinstance(run, dict) else None)
        if status != 'SUCCEEDED':
            Actor.log.error(f"Source Actor run failed or was aborted: {run}")
            raise Exception(f"Source Actor failed to complete successfully. Status: {status}")
            
        default_dataset_id = getattr(run, 'default_dataset_id', None) or (run.get('defaultDatasetId') if isinstance(run, dict) else None)
        
        if not default_dataset_id:
            raise Exception("Could not find default_dataset_id on the run object.")
        
        # Fetch the results from the source dataset
        dataset_items = await apify_client.dataset(default_dataset_id).list_items()
        
        items = dataset_items.items
        Actor.log.info(f"Successfully retrieved {len(items)} items from source Actor.")
        return items
        
    except Exception as e:
        Actor.log.error(f"Error fetching data from source Actor: {e}")
        raise
