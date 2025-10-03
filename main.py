from fastapi import FastAPI
from fastapi.responses import JSONResponse
from src.utilities.logger import Logger
from src.router.router import api_router
import os 

logger = Logger.getLogger(__name__)



app = FastAPI(title="AdvancedRagChatbot API", version="1.0.0")

@app.get("/health", response_class=JSONResponse)
async def health_check():
    """
    Health check endpoint to verify the service is running.
    """
    return JSONResponse(content={"status": "ok"}, status_code=200)


app.include_router(api_router, prefix="/api")
