# Google Maps Business Lead Scraper

Scrape clean, structured business lead data from Google Maps quickly and reliably.

## What it does

This Actor allows you to search for businesses on Google Maps by keyword and location (e.g., "dentists in Delhi") and returns structured, actionable lead data. Instead of returning raw unstructured HTML, it normalizes and cleans the data into a stable format perfect for CRMs, sales prospecting, and market research.

Under the hood, this Actor delegates the heavy lifting to Apify's robust ecosystem of Google Maps scrapers and acts as a powerful orchestrator that standardizes the schema, enforces data deduplication, and filters results based on your strict criteria (like minimum rating or requiring a website/phone number).

## Features

- **Keyword & Location Search**: Pass multiple queries at once.
- **Data Normalization**: Consistently structured data regardless of source changes.
- **Smart Deduplication**: Avoids charging or storing duplicate businesses that appear across multiple search queries.
- **Filtering**: Filter out businesses with low ratings, or missing phone numbers and websites.
- **Field Selection**: Choose exactly which fields you want in your final dataset to keep it clean.
- **Safe & Reliable**: Does not rely on brittle internal endpoints or CAPTCHA bypasses.

## Input

Here is an example of how to configure the input:

```json
{
  "searchQueries": [
    "dentists in Delhi",
    "gyms in Jaipur"
  ],
  "maxResults": 100,
  "minRating": 4.0,
  "requireWebsite": true,
  "requirePhone": true,
  "deduplicate": true,
  "language": "en"
}
```

### Input Fields Explanation

- `searchQueries` (Array): List of search phrases (e.g., "real estate agents in London").
- `maxResults` (Integer): Total maximum number of unique results to scrape.
- `includeFields` (Array): Optional list of fields to include in the output. If empty, all available fields are returned.
- `minRating` (Number): Minimum acceptable star rating (0-5).
- `requireWebsite` (Boolean): If true, skips businesses without a website.
- `requirePhone` (Boolean): If true, skips businesses without a phone number.
- `deduplicate` (Boolean): Removes duplicate places found across different queries.
- `language` (String): The language code to use for scraping (default "en").

## Output

The Actor stores results in the Apify default dataset. 

Example Output:

```json
{
  "placeId": "ChIJb-X_L-V9QTkR75G58m9D",
  "businessName": "Smile Dental Clinic",
  "category": "Dentist",
  "address": "123 Health Ave, New Delhi, Delhi",
  "city": "New Delhi",
  "state": "Delhi",
  "country": "IN",
  "postalCode": "110001",
  "phone": "+91 98765 43210",
  "website": "https://smiledentaldelhi.example.com",
  "rating": 4.8,
  "reviewCount": 142,
  "googleMapsUrl": "https://www.google.com/maps/place/?q=place_id:ChIJb-X_L-V9QTkR75G58m9D",
  "latitude": 28.6139,
  "longitude": 77.2090,
  "openingHours": {
    "Monday": "9:00 AM - 5:00 PM"
  },
  "source": "google_maps",
  "scrapedAt": "2023-11-20T14:22:15Z"
}
```
*(Note: This is example data, not an actual scrape)*

## Use Cases

- **Lead Generation**: Compile lists of prospects matching specific criteria.
- **Local Business Research**: Analyze competitors and average ratings in a specific region.
- **Market Research**: Discover underserved markets based on rating data.
- **Sales Prospecting**: Build lists of leads with phone numbers and websites for cold outreach.
- **Local SEO Research**: Identify businesses lacking reviews or optimized profiles.

## API Usage

You can run this Actor programmatically via the Apify API using your Apify API Token. By using environment variables and Apify Secrets, you never need to hardcode your credentials in source code.

```bash
curl -X POST "https://api.apify.com/v2/acts/YOUR-ACTOR-ID/runs?token=YOUR-APIFY-TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"searchQueries":["dentists in Delhi"], "maxResults": 10}'
```

## Limitations

- The availability of data like `city`, `state`, or `postalCode` strictly depends on how the business entered their address into Google Maps. Sometimes, complex addresses are not fully parsed.
- `maxResults` is an upper limit. If Google Maps only finds 15 results for your query, the Actor will return 15 results, even if you set `maxResults` to 100.
- Certain Google Maps fields (like detailed opening hours or deep review data) may be unavailable or limited by the upstream data source.

## Responsible Use

Users are responsible for complying with applicable laws, website terms of service, privacy requirements (such as GDPR or CCPA regarding personal data like phone numbers or emails), and data-protection obligations. This Actor facilitates access to public data and does not promise unrestricted access to Google Maps. Always respect limits and use scraped data ethically.
