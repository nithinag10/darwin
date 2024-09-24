import os
import logging
from typing import List, Dict, Any, Optional

from azure.storage.blob.aio import BlobServiceClient
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.schema import Document
import faiss
import numpy as np

from repositories.DocumentationSourceRepository import DocumentationSourceRepository
from services.blob_storage_service import BlobStorageService
from pydantic import ValidationError

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(
        self,
        blob_storage_service: BlobStorageService,
        documentation_source_repo: DocumentationSourceRepository,
        embedding_model: str = "huggingface",
        embedding_kwargs: Optional[Dict[str, Any]] = None,
        faiss_index_path: str = "faiss.index"
    ):
        """
        Initializes the RAGService with Blob Storage, Documentation Repository, Embedding Model, and FAISS index.
        :param blob_storage_service: Instance of BlobStorageService for downloading blobs.
        :param documentation_source_repo: Repository to interact with the documentation_sources table.
        :param embedding_model: Model name for embeddings (e.g., "huggingface", "groq").
        :param embedding_kwargs: Additional keyword arguments for the embedding model.
        :param faiss_index_path: Path to save/load the FAISS index.
        """
        self.blob_storage_service = blob_storage_service
        self.documentation_source_repo = documentation_source_repo
        self.embedding_model_name = embedding_model
        self.embedding_kwargs = embedding_kwargs or {}
        self.faiss_index_path = faiss_index_path
        self.vector_store = self.initialize_faiss()

    def initialize_faiss(self) -> FAISS:
        """
        Initializes or loads the FAISS vector store.
        :return: FAISS vector store instance.
        """
        if os.path.exists(self.faiss_index_path):
            logger.info(f"Loading existing FAISS index from {self.faiss_index_path}.")
            vector_store = FAISS.load_local(self.faiss_index_path, self.get_embedding_instance())
        else:
            logger.info("Creating a new FAISS vector store.")
            vector_store = FAISS.from_texts([], self.get_embedding_instance())
        return vector_store

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
        generates embeddings, and stores them in FAISS. If a product_id is specified, only loads sources for that product.
        :param product_id: (Optional) The product ID to filter documentation sources.
        """
        try:
            sources = await self.documentation_source_repo.get_sources_by_product_id(product_id)
            if product_id:
                logger.info(f"Loading documentation sources for Product ID: {product_id} ({len(sources)} sources).")
            else:
                logger.info(f"Loading all documentation sources ({len(sources)} sources).")

            for source in sources:
                blob_name = source['storage_url']
                current_product_id = source.get('product_id')
                if not current_product_id:
                    logger.warning(f"Skipping blob '{blob_name}' as it lacks 'product_id'.")
                    continue

                logger.debug(f"Downloading blob: {blob_name}")
                blob_content = await self.blob_storage_service.download_blob(blob_name)
                documents = self.split_text(blob_content, current_product_id)
                self.vector_store.add_documents(documents)
                logger.info(f"Added {len(documents)} documents from blob '{blob_name}' (Product ID: {current_product_id}) to FAISS index.")

            # Save the FAISS index after loading all documents
            self.vector_store.save_local(self.faiss_index_path)
            logger.info(f"FAISS index saved to {self.faiss_index_path}.")

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
            # Access all documents from the FAISS vector store
            all_documents = self.vector_store.docstore.docs.values()
            # Filter documents by product_id
            filtered_documents = [
                doc for doc in all_documents
                if doc.metadata.get("product_id") == product_id
            ]
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