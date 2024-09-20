
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

        for feature in prioritized_features:
            report, effort = await self.developer_agent.assess_feasibility_and_effort(feature)
            feasibility_reports[feature] = {
                "feasibility_report": report,
                "development_effort": effort
            }

        logger.debug(f"Feasibility reports: {feasibility_reports}")
        state["feasibility_reports"] = feasibility_reports
        return state