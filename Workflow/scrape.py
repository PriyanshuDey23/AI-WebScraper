from langchain_community.document_loaders.firecrawl import FireCrawlLoader
import os
from dotenv import load_dotenv

load_dotenv()

FIRE_CRAWL_API_KEY = os.getenv("FIRE_CRAWL_API_KEY")


# Function to scrape websites
def scrape_websites(url):

    loader = FireCrawlLoader(
        url=url,
        api_key=FIRE_CRAWL_API_KEY,
        mode="scrape", #crawl
    )

    documents = loader.load() 
    
    return documents


