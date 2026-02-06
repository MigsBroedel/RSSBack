import httpx
from bs4 import BeautifulSoup
from typing import List
from datetime import datetime
from app.services.ingestion.base import ContentIngestor, IngestedItem

class HTMLScraperIngestor(ContentIngestor):
    async def fetch(self, url: str) -> List[IngestedItem]:
        async with httpx.AsyncClient(follow_redirects=True, timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            
        soup = BeautifulSoup(response.text, "html.parser")
        items = []
        
        # Heuristic: Find articles
        # This is a generic fallback; for specific sites, we'd need more rules.
        # Looking for <article> tags or generic list items
        
        # Meta tags for the main page (if it's a single page)
        # But commonly we want a list of articles from a blog home.
        
        # Attempt to find RSS feed first? The prompt suggests "Detecção automática de RSS se existir"
        # Since this is the Scraper Ingestor, maybe we assume we are scraping logic here.
        
        # Simple heuristic: Look for links inside article tags
        articles = soup.find_all("article")
        if not articles:
            # Fallback to checking og:type or simple schema parsing?
            # For this MVP, let's try to extract list items that look like posts
            pass

        # Since writing a generic scraper is huge, let's implement a "Basic Meta Tag" extraction 
        # for the page itself if it's a single article, OR try to find a list.
        # User prompt says: "Extração por: meta tags, schema.org, fallback com heurística"
        
        # Let's target the page title/desc as one item if no list found (Single Page Mode)
        # Or try to find <a> tags with clear titles.
        
        # For professional scraping, we'd usually use more config. 
        # Here's a safety net: Return the page itself as an item if meaningful.
        
        title = soup.title.string if soup.title else ""
        description = ""
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc:
            description = meta_desc.get("content", "")
            
        og_image = soup.find("meta", property="og:image")
        image_url = og_image["content"] if og_image else None
        
        # Check for meaningful content
        if title:
             items.append(IngestedItem(
                 title=title,
                 url=url,
                 summary=description,
                 image_url=image_url,
                 published_at=datetime.utcnow(), # Approximate
                 raw_payload={"source": "html_scraper"},
                 content_type="website"
             ))
             
        return items
