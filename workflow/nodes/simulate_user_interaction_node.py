from typing import Dict
from agents.user_agent import UserAgent
from workflow.state import EvaluationState

class InteractionSimulationNode:
    def __init__(self, user_agent: UserAgent):
        self.user_agent = user_agent

    async def __call__(self, state: EvaluationState) -> Dict:
        scenario = state["scenario"]
        product_info = state["product_info"]
        interaction_result = await self.user_agent.simulate_interaction(scenario, product_info)
        state["interaction_result"] = interaction_result
        return state
