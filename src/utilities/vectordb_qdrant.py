from src.utilities.logger import Logger 
from src.utilities.constants import  ConstantsFetcher
from langchain.docstore.document import Document
from qdrant_client import QdrantClient
from qdrant_client.http import models
from dotenv import load_dotenv
import torch
import os

load_dotenv()
logger = Logger().getLogger(__name__)


class VectorDBQdrant:

    def __init__(self):
        self.qdrant_host = os.getenv('QDRANT_HOST', 'localhost')
        self.qdrant_port = int(os.getenv('QDRANT_PORT', 6333))
        self.collection_name = os.getenv('QDRANT_COLLECTION_NAME', 'Wikipedia_collection')
        self.embedding_dimension = 384  # Dimension for 'all-MiniLM-L6-v2' model
        self.client = QdrantClient(host=self.qdrant_host, port=self.qdrant_port)
        self.__ensure_collection()


    def __ensure_collection(self):
        """
        checks whether the collection exists, if not create new one with predefined name.
        """
        try:
            if not self.client.get_collection(self.collection_name):
                self.client.recreate_collection(
                    collection_name=self.collection_name,
                    vectors=models.VectorParams(size=self.embedding_dimension, distance=models.Distance.COSINE))
                
                logger.info(f"Created new collection: {self.collection_name}")
            else:
                logger.info(f"Collection {self.collection_name} already exists.")
        except Exception as exec:
            logger.error(f"Error in ensuring collection: {exec}")
            raise exec


    async def upsert_embeddings(self, documents: list[Document], embeddings: list[torch.Tensor]):
        """
        adds the embeddings, documents to the vector db.

        args:
            documents (list[Document])  :  list of documents 
            embeddings (list[torch.Tensor]) : list of embeddings 

        returns:
            None
        """
        try:
            points = []
            for doc, emb in zip(documents, embeddings):
                point = models.PointStruct(
                    id=doc.metadata['chunk_index'],
                    vector=emb.tolist(),
                    payload=doc.metadata.update({'content': doc.page_content}))
                points.append(point)

            self.client.upsert(
                collection_name=self.collection_name,
                points=points)
            
            logger.info(f"Upserted {len(points)} points to collection {self.collection_name}")

        except Exception as exec: 
            logger.error(f"Error in upserting embeddings: {exec}")
            raise exec