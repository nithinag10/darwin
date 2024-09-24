from typing import Dict
from services.RAGService import RAGService
from workflow.state import EvaluationState
import logging
import asyncio

logger = logging.getLogger(__name__)

class FetchProductInfoNode:
    def __init__(self, rag_service: RAGService):
        """
        Initializes the FetchProductInfoNode with an instance of RAGService.
        
        :param rag_service: Instance of RAGService for retrieval operations.
        """
        self.rag_service = rag_service
        self._knowledge_base_loaded = False  # Flag to prevent multiple loadings

    async def _load_knowledge_base_if_needed(self, product_id: int):
        """
        Loads the knowledge base by downloading and chunking documents for the given product_id if not already loaded.
        
        :param product_id: The product ID for which to load the knowledge base.
        """
        if not self._knowledge_base_loaded:
            logger.debug(f"Loading knowledge base for Product ID: {product_id}...")
            await self.rag_service.load_knowledge_base(product_id=product_id)
            self._knowledge_base_loaded = True
            logger.debug("Knowledge base loaded successfully.")
        else:
            logger.debug("Knowledge base already loaded. Skipping re-load.")

    async def __call__(self, state: EvaluationState) -> Dict:
        """
        Executes the node to fetch product information based on the provided EvaluationState.
        
        :param state: The current evaluation state containing the product_id.
        :return: Updated EvaluationState with fetched product_info.
        """
        product_id = state.get("product_id")
        if not product_id:
            logger.error("Product ID not found in state.")
            raise ValueError("Product ID is required to fetch product info.")

        logger.debug(f"Fetching product info for Product ID: {product_id}")

        # Ensure the knowledge base is loaded for the specific product
        await self._load_knowledge_base_if_needed(product_id)

        # Retrieve relevant product documents
        product_info_docs = await self.rag_service.get_documents_by_product_id(product_id)
        if not product_info_docs:
            logger.warning(f"No documents found for Product ID: {product_id}")
            state["product_info"] = "No product information available."
        else:
            product_info = "\n".join([doc.page_content for doc in product_info_docs])
            state["product_info"] = product_info
            logger.debug("Product info fetched successfully.")

        return state