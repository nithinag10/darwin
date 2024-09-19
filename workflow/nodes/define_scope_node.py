import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

from typing import Dict
from workflow.state import EvaluationState

class DefineScopeNode:
    def __init__(self):
        pass

    async def __call__(self, state: EvaluationState) -> Dict:
        evaluation = state["evaluation"]
        evaluation_type = state["evaluation_type"]
        
        # Log evaluation details
        logging.debug(f"Starting evaluation with ID: {evaluation.id}, Type: {evaluation_type}")
        
        # Directly assign evaluation_scope from evaluation_type
        evaluation_scope = evaluation_type
        
        # Log the assigned evaluation scope
        logging.debug(f"Assigned evaluation scope: {evaluation_scope}")
        
        state["evaluation_scope"] = evaluation_scope
        return state