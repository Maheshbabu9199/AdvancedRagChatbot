from src.utilities.logger import Logger
from src.utilities.constants import ConstantsFetcher
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
import os
import uuid 



logger = Logger().getLogger(__name__)



class DocumentsChunker:

    def __init__(self):

        self.chunk_size = 500
        self.chunk_overlap = 50
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=self.chunk_size,
                                                chunk_overlap=self.chunk_overlap,
                                                length_function=len,
                                                separators=["\n\n", "\n", " ", ""])
        
    

    async def chunk_documents(self, scraped_data: list[dict]):
        try:
            self.documents = []

            for item in scraped_data:
                text = item['content']
                chunks = self.text_splitter.split_text(text)
                metadata = {
                    'url': item['url'],
                    'title': item['title'],
                    'heading': item['heading'],
                    'subheading': item['subheading']
                }
                for chunk in chunks:
                    doc_metadata = metadata.copy()
                    doc_metadata['chunk_index'] = str(uuid.uuid4())
                    self.documents.append(Document(page_content=chunk, metadata=doc_metadata))

            return self.documents

        except Exception as exec: 
            logger.error(f"Error in chunking documents: {exec}")
            raise exec