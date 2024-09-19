from typing import Dict
from services.RAGService import RAGService
from workflow.state import EvaluationState
import logging

logger = logging.getLogger(__name__)

class FetchProductInfoNode:
    def __init__(self, rag_service: RAGService):
        self.rag_service = rag_service

    async def __call__(self, state: EvaluationState) -> Dict:
        product_id = state["product_id"]
        logger.debug(f"Fetching product info for Product ID: {product_id}")
        product_info = await self.rag_service.fetch_relevant_info(product_id)
        state["product_info"] = product_info
        logger.debug("Product info fetched successfully.")
        return state