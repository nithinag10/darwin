import logging
from typing import Dict, List
from workflow.state import EvaluationState
from agents.product_manager_agent import ProductManagerAgent

logger = logging.getLogger(__name__)

class FeatureSuggestionPrioritizationNode:
    def __init__(self, product_manager_agent: ProductManagerAgent):
        self.product_manager_agent = product_manager_agent

    async def __call__(self, state: EvaluationState) -> EvaluationState:
        ideated_features: List[Dict] = state.get("ideated_features", [])
        pain_points: List[str] = state.get("interaction_result", {}).get("pain_points", [])
        user_feedback: Dict = state.get("interaction_result", {}).get("user_feedback", {})

        if not ideated_features:
            logger.warning("No ideated features to prioritize.")
            state["prioritized_features"] = []
            return state

        prioritized_features = await self.product_manager_agent.prioritize_features(
            features=ideated_features,
            pain_points=pain_points,
            user_feedback=user_feedback
        )
        logger.debug(f"Prioritized features: {prioritized_features}")

        state["prioritized_features"] = prioritized_features
        return state