from src.utilities.logger import Logger 
from src.utilities.constants import ConstantsFetcher
from src.services.documents_chunker import DocumentsChunker
from src.utilities.vectordb_qdrant import VectorDBQdrant
from src.services.documents_embedding import DocumentsEmbedding
import os 


logger = Logger().getLogger(__name__)



class DocumentsHandler:

    def __init__(self):
        self.chunker = DocumentsChunker()
        self.vectordb = VectorDBQdrant()
        self.embedding = DocumentsEmbedding()
        pass



    async def process_documents(self, scraped_data: list[dict]):
        try:
            logger.info("Starting document chunking process")
            documents = await  self.chunker.chunk_documents(scraped_data)
            embeddings = await self.embedding.generate_embeddings(documents)
            await self.vectordb.upsert_embeddings(documents, embeddings)
            logger.info("Completed processing and storing documents")

        except Exception as exec:
            logger.error(f"Error in processing documents: {exec}")
            raise exec