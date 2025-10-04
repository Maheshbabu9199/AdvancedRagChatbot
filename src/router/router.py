from fastapi import FastAPI, APIRouter
from fastapi.responses import JSONResponse
from ..router.datamodels import ScrapeRequest, ProcessDocuments
from ..services.documents_handler import DocumentsHandler
from ..services.scrape_data import ScrapeData
from ..utilities.logger import Logger
import os 



logger = Logger.getLogger(__name__)

api_router = APIRouter()
scrapper = ScrapeData()
documents_handler = DocumentsHandler()


@api_router.api_route("/scrape", methods=['POST'])
async def scrape_wikipedia(request: ScrapeRequest):
    """
    endpoint to scrape wikipedia pages and return structured data chunks.
    """
    try:
        scraped_data = await scrapper.scrape_wikipedia_pages(request.urls)
        return JSONResponse(content={"data": scraped_data, "status": "successful"}, status_code=200)
    
    except Exception as e:
        logger.error(f"Error during scraping: {e}")
        return JSONResponse(content={"error": str(e), "status": "Unsuccessful"}, status_code=500)
    


@api_router.api_route("/process_documents", methods=['POST'])
async def scrape_wikipedia(request: ProcessDocuments):
    """
    endpoint to scrape wikipedia pages, process them into embeddings and vectorize into the vectordb.
    """
    try:
        scraped_data = await scrapper.scrape_wikipedia_pages(request.urls)
        result = await documents_handler.process_documents(scraped_data)

        return JSONResponse(content={"data": result, "status": "successful"}, status_code=200)
    
    except Exception as e:
        logger.error(f"Error during scraping: {e}")
        return JSONResponse(content={"error": str(e), "status": "Unsuccessful"}, status_code=500)