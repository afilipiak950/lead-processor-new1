# Apify Konfiguration

## Actor Einstellungen

### Input Schema
```json
{
  "startUrls": [
    {
      "url": "https://www.linkedin.com/search/results/people/?keywords=CEO%20OR%20CTO%20OR%20CIO&industry=%5B%2213%22%5D&origin=GLOBAL_SEARCH_HEADER"
    }
  ],
  "maxItems": 10,
  "maxRequestsPerCrawl": 100,
  "proxy": {
    "useApifyProxy": true
  }
}
```

### Output Schema
```json
{
  "name": "string",
  "email": "string",
  "company": "string",
  "position": "string",
  "linkedin_url": "string",
  "domain": "string"
}
```

## Verwendung
1. Erstellen Sie einen neuen Actor in Apify
2. Kopieren Sie die Input/Output Schemas
3. Setzen Sie die API-Key in der .env Datei
4. Aktualisieren Sie die Actor-ID in lead_processor.py 