
import logging
from typing import Dict
from workflow.state import EvaluationState
from agents.developer_agent import DeveloperAgent

logger = logging.getLogger(__name__)

class TechnicalFeasibilityAssessmentNode:
    def __init__(self, developer_agent: DeveloperAgent):
        self.developer_agent = developer_agent

    async def __call__(self, state: EvaluationState) -> Dict:
        prioritized_features = state.get("prioritized_features", [])
        feasibility_reports = {}

        if not prioritized_features:
            logger.warning("No prioritized features to assess feasibility.")
            state["feasibility_reports"] = {}
            return state

        logger.debug("Starting Technical Feasibility Assessment Node.")


        reports = await self.developer_agent.assess_feasibility_and_effort(prioritized_features)   
        
        logger.debug(f"Feasibility reports: {reports}")
        state["feasibility_reports"] = reports
        return state