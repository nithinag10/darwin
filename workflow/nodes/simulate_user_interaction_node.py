from typing import Dict
from agents.user_agent import UserAgent
from workflow.state import EvaluationState
import json
import logging

logger = logging.getLogger(__name__)

class InteractionSimulationNode:
    def __init__(self, user_agent: UserAgent):
        self.user_agent = user_agent

    async def __call__(self, state: EvaluationState) -> Dict:
        product_info = state["product_info"]
        logger.debug("Starting interaction simulation node.")
        
        interaction_result_json = await self.user_agent.simulate_interaction(product_info)
        logger.debug(f"Received interaction result: {interaction_result_json}")
        
        try:
            interaction_result = json.loads(interaction_result_json)
            logger.debug("Parsed interaction result successfully. interaction_result: {interaction_result}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse interaction result: {e}")
            interaction_result = {"error": "Invalid response format."}
        
        state["interaction_result"] = interaction_result
        return state