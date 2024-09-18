from typing import Dict
from agents.project_manager_agent import ProjectManagerAgent
from workflow.state import EvaluationState

class DefineScopeNode:
    def __init__(self, project_manager_agent: ProjectManagerAgent):
        self.project_manager_agent = project_manager_agent

    async def __call__(self, state: EvaluationState) -> Dict:
        evaluation = state["evaluation"]
        evaluation_type = state["evaluation_type"]
        evaluation_context = f"Evaluation ID: {evaluation.id}, Type: {evaluation_type}"
        evaluation_scope = await self.project_manager_agent.define_evaluation_scope(evaluation_context)
        state["evaluation_scope"] = evaluation_scope
        return state
