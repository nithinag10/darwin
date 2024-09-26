import os
import logging
from typing import List, Dict, Any, Optional

from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.schema import Document
import numpy as np

from repositories.DocumentationSourceRepository import DocumentationSourceRepository
from services.blob_storage_service import BlobStorageService

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(
        self,
        db_con,
        embedding_model: str = "huggingface",
        embedding_kwargs: Optional[Dict[str, Any]] = None,
        chroma_persist_directory: str = "chroma_db",
    ):
        """
        Initializes the RAGService with Blob Storage, Documentation Repository, Embedding Model, and Chroma vector store.
        :param db_con: Database connection for DocumentationSourceRepository.
        :param embedding_model: Model name for embeddings (e.g., "huggingface", "groq").
        :param embedding_kwargs: Additional keyword arguments for the embedding model.
        :param chroma_persist_directory: Directory to persist Chroma vector store data.
        """
        self.blob_storage_service = BlobStorageService(
            connection_string=os.getenv('AZURE_STORAGE_CONNECTION_STRING'),
            container_name=os.getenv('AZURE_STORAGE_CONTAINER_NAME')
        )
        self.documentation_source_repo = DocumentationSourceRepository(db_con)
        self.embedding_model_name = embedding_model
        self.embedding_kwargs = embedding_kwargs or {}
        self.chroma_persist_directory = chroma_persist_directory
        self.vector_store = self.initialize_chroma()

    def initialize_chroma(self) -> Chroma:
        """
        Initializes or loads the Chroma vector store.
        :return: Chroma vector store instance.
        """
        logger.info(f"Initializing Chroma vector store with persist directory: {self.chroma_persist_directory}")
        try:
            embeddings = self.get_embedding_instance()
            if os.path.exists(self.chroma_persist_directory):
                logger.info(f"Loading existing Chroma vector store from {self.chroma_persist_directory}.")
                vector_store = Chroma(
                    persist_directory=self.chroma_persist_directory,
                    embedding_function=embeddings
                )
            else:
                logger.info("Creating a new Chroma vector store.")
                vector_store = Chroma(
                    persist_directory=self.chroma_persist_directory,
                    embedding_function=embeddings
                )
                logger.info("Chroma vector store initialized successfully.")
            return vector_store
        except Exception as e:
            logger.error(f"Error initializing Chroma vector store: {e}")
            raise e

    def get_embedding_instance(self) -> HuggingFaceEmbeddings:
        """
        Returns an instance of the embedding model based on the specified model name.
        :return: Embedding instance.
        """
        if self.embedding_model_name.lower() == "huggingface":
            return HuggingFaceEmbeddings(**self.embedding_kwargs)
        elif self.embedding_model_name.lower() == "groq":
            # Placeholder for GroqEmbeddings, replace with actual implementation if available
            from langchain.embeddings import GroqEmbeddings
            return GroqEmbeddings(**self.embedding_kwargs)
        else:
            raise ValueError(f"Unsupported embedding model: {self.embedding_model_name}")

    async def load_knowledge_base(self, product_id: Optional[int] = None):
        """
        Loads documents from Azure Blob Storage, associates them with product IDs, splits them into chunks,
        generates embeddings, and stores them in Chroma. If a product_id is specified, only loads sources for that product.
        :param product_id: (Optional) The product ID to filter documentation sources.
        """
        try:
            sources = await self.documentation_source_repo.get_sources_by_product_id(product_id)
            if product_id:
                logger.info(f"Loading documentation sources for Product ID: {product_id} ({len(sources)} sources).")
            else:
                logger.info(f"Loading all documentation sources ({len(sources)} sources).")

            all_documents = []
            for source in sources:
                blob_url = source.get('storage_url')
                current_product_id = source.get('product_id')
                if not current_product_id:
                    logger.warning(f"Skipping blob '{blob_url}' as it lacks 'product_id'.")
                    continue

                logger.debug(f"Downloading blob: {blob_url}")
                blob_content = await self.blob_storage_service.download_blob_by_url(blob_url)
                # Assuming blob_content is bytes, decode to string
                text_content = blob_content.decode('utf-8')
                documents = self.split_text(text_content, current_product_id)
                all_documents.extend(documents)
                logger.info(f"Prepared {len(documents)} documents from blob '{blob_url}' (Product ID: {current_product_id}).")

            if all_documents:
                logger.info(f"Adding {len(all_documents)} documents to Chroma vector store.")
                self.vector_store.add_documents(all_documents)
                self.vector_store.persist()
                logger.info(f"Chroma vector store persisted to {self.chroma_persist_directory}.")
            else:
                logger.info("No documents to add to Chroma vector store.")

        except Exception as e:
            logger.error(f"Error loading knowledge base: {e}")
            raise e

    def split_text(self, text: str, product_id: int) -> List[Document]:
        """
        Splits text into chunks suitable for embedding and associates each chunk with the given product_id.
        :param text: The raw text to split.
        :param product_id: The product ID associated with the text.
        :return: List of Document objects.
        """
        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        split_text = text_splitter.split_text(text)
        return [
            Document(
                page_content=chunk,
                metadata={
                    "type": "product_info",
                    "product_id": product_id
                }
            )
            for chunk in split_text
        ]

    async def get_documents_by_product_id(self, product_id: int) -> List[Document]:
        """
        Retrieves all documents associated with the given product ID.
        :param product_id: The product ID to query.
        :return: List of relevant Document objects.
        """
        try:
            logger.debug(f"Retrieving documents for Product ID: {product_id}")
            # Access all documents from the Chroma vector store
            # Chroma manages its own methods for retrieval
            retriever = self.vector_store.as_retriever()
            retriever.search_kwargs.update({"k": 10})  # Adjust 'k' as needed
            query = f"product_id:{product_id}"
            filtered_documents = await asyncio.to_thread(retriever.get_relevant_documents, query)
            logger.info(f"Retrieved {len(filtered_documents)} documents for Product ID: {product_id}")
            return filtered_documents
        except Exception as e:
            logger.error(f"Error retrieving documents for Product ID {product_id}: {e}")
            return []

    async def close(self):
        """
        Closes any open resources.
        """
        await self.blob_storage_service.close()
        logger.info("Closed BlobStorageService.")