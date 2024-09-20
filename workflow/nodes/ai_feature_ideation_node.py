import logging
from typing import Dict, List
from workflow.state import EvaluationState
from agents.ai_features_ideation_agent import AIFeatureIdeationAgent

logger = logging.getLogger(__name__)

class AIFeatureIdeationNode:
    def __init__(self, ai_feature_ideation_agent: AIFeatureIdeationAgent):
        self.ai_feature_ideation_agent = ai_feature_ideation_agent

    async def __call__(self, state: EvaluationState) -> EvaluationState:
        interaction_result = state.get("interaction_result", {})
        pain_points: List[str] = interaction_result.get("pain_points", [])
        product_info: str = state.get("product_info", "")

        if not pain_points:
            logger.warning("No pain points found in interaction result.")
            state["ideated_features"] = []
            return state

        if not product_info:
            logger.warning("No product information available.")
            state["ideated_features"] = []
            return state

        logger.debug(f"Starting AI Feature Ideation Node with product_info: {product_info}")

        ideated_features = await self.ai_feature_ideation_agent.ideate_features(pain_points, product_info)
        logger.debug(f"Ideated features: {ideated_features}")

        state["ideated_features"] = ideated_features
        return state