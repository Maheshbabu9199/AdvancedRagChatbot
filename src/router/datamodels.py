import os
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any



class ScrapeRequest(BaseModel):
    urls: List[str] = Field(..., description="List of Wikipedia URLs to scrape", example=['https://www.examples.com', 'https://www.abcd.com'])
    #  depth: Optional[int] = Field(1, description="Depth of scraping (default is 1)", example=1)


class ProcessDocuments(BaseModel):

    urls: List[str] = Field(..., description="List of Wikipedia URLs to scrape", example=['https://www.examples.com', 'https://www.abcd.com'])
    depth: Optional[int] = Field(1, description="Depth of scraping (default is 1)", example=1)

