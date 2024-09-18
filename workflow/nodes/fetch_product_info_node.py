from typing import Dict
from services.RAGService import RAGService
from workflow.state import EvaluationState

class FetchProductInfoNode:
    def __init__(self, rag_service: RAGService):
        self.rag_service = rag_service

    async def __call__(self, state: EvaluationState) -> Dict:
        product_id = state["product_id"]
        product_info = await self.rag_service.fetch_relevant_info(product_id)
        state["product_info"] = product_info
        return state
