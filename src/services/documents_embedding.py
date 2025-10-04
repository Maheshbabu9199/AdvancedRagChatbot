from langchain.docstore.document import Document
from src.utilities.logger import Logger 
from src.utilities.constants import ConstantsFetcher
from sentence_transformers import SentenceTransformer
import torch 
import os 



logger = Logger().getLogger(__name__)


class DocumentsEmbedding:

    def __init__(self):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model = SentenceTransformer('all-MiniLM-L6-v2', device=self.device)
        logger.info(f"Using device: {self.device} for embedding generation")
        self.embedding_dimension = 384  # Dimension for 'all-MiniLM-L6-v2' model



    async def generate_embeddings(self, documents: list[Document]):
        try:
            texts = [doc.page_content for doc in documents]
            embeddings = self.model.encode(texts, convert_to_tensor=True, show_progress_bar=True)
            return embeddings

        except Exception as exec: 
            logger.error(f"Error in generating embeddings: {exec}")
            raise exec