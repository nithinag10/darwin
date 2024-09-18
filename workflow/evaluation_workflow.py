from typing import Dict, Optional
from langgraph.graph import StateGraph
from langgraph.checkpoint.sqlite import SqliteSaver
import logging

from workflow.state import EvaluationState
from workflow.nodes.define_scope_node import DefineScopeNode
from workflow.nodes.fetch_product_info_node import FetchProductInfoNode
from workflow.nodes.simulate_user_interaction_node import InteractionSimulationNode
from agents.project_manager_agent import ProjectManagerAgent
from agents.user_agent import UserAgent
from services.RAGService import RAGService
from models.Evaluation import Evaluation

logger = logging.getLogger(__name__)

async def run_evaluation_workflow(
    evaluation: Evaluation,
    user_agent_definition_id: int,
    evaluation_type: str,
    rag_service: RAGService,
    project_manager_agent: ProjectManagerAgent,
    user_agent: UserAgent
) -> Optional[Dict]:
    """
    Runs the evaluation workflow using LangGraph.
    """
    # Initialize workflow with state_schema
    workflow = StateGraph(state_schema=EvaluationState)

    # Instantiate node classes
    define_scope = DefineScopeNode(project_manager_agent)
    fetch_product_info = FetchProductInfoNode(rag_service)
    interaction_simulation = InteractionSimulationNode(user_agent)

    # Add nodes to the workflow
    workflow.add_node("define_scope", define_scope)
    workflow.add_node("fetch_product_info", fetch_product_info)
    workflow.add_node("interaction_simulation", interaction_simulation)

    # Define edges
    workflow.add_edge("define_scope", "fetch_product_info")
    workflow.add_edge("fetch_product_info", "interaction_simulation")

    # Setup checkpointing with SQLite (optional)
    memory = SqliteSaver.from_conn_string(":memory:")
    workflow.compile(checkpointer=memory)

    # Initialize state
    initial_state: EvaluationState = {
        "evaluation": evaluation,
        "evaluation_type": evaluation_type,
        "user_agent": user_agent,
        "rag_service": rag_service,
        "project_manager_agent": project_manager_agent,
        "scenario": "First-time user exploring the product",
        "evaluation_scope": "",
        "product_info": "",
        "interaction_result": "",
        "product_id": evaluation.product_id
    }

    try:
        # Run the workflow asynchronously
        async for state in workflow.astream(initial_state):
            if workflow.is_finished():
                logger.info("Workflow finished successfully for Evaluation ID: %s", evaluation.id)
                return state

        logger.warning("Workflow did not finish as expected for Evaluation ID: %s", evaluation.id)
        return {}
    except Exception as e:
        logger.error("Error running evaluation workflow for Evaluation ID: %s - %s", evaluation.id, str(e))
        # Handle or re-raise the exception as needed
        raise e