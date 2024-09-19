import logging  # {{ edit_1 }}

# Configure logging
logging.basicConfig(level=logging.DEBUG)  # {{ edit_2 }}

from typing import Dict
from agents.project_manager_agent import ProjectManagerAgent
from workflow.state import EvaluationState

class DefineScopeNode:
    def __init__(self, project_manager_agent: ProjectManagerAgent):
        self.project_manager_agent = project_manager_agent

    async def __call__(self, state: EvaluationState) -> Dict:
        evaluation = state["evaluation"]
        evaluation_type = state["evaluation_type"]
        
        # Log evaluation details
        logging.debug(f"Starting evaluation with ID: {evaluation.id}, Type: {evaluation_type}")  # {{ edit_3 }}
        
        evaluation_context = f"Evaluation ID: {evaluation.id}, Type: {evaluation_type}"
        evaluation_scope = await self.project_manager_agent.define_evaluation_scope(evaluation_context)
        
        # Log the defined evaluation scope
        logging.debug(f"Defined evaluation scope: {evaluation_scope}")
        
        state["evaluation_scope"] = evaluation_scope
        return state
