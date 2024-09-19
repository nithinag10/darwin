import asyncio
from typing import Dict, Optional
from langgraph.graph import StateGraph
import logging

from workflow.state import EvaluationState
from workflow.nodes.define_scope_node import DefineScopeNode
from workflow.nodes.fetch_product_info_node import FetchProductInfoNode
from workflow.nodes.simulate_user_interaction_node import InteractionSimulationNode
from agents.project_manager_agent import ProjectManagerAgent
from agents.user_agent import UserAgent
from services.RAGService import RAGService
from models.Evaluation import Evaluation
from IPython.display import Image, display

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

    # Set entry and finish points
    workflow.set_entry_point("define_scope")  # Set entry point
    workflow.set_finish_point("interaction_simulation")  # Set finish point

    # Define edges
    workflow.add_edge("define_scope", "fetch_product_info")
    workflow.add_edge("fetch_product_info", "interaction_simulation")

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

    # Compile the workflow
    compiled_workflow = workflow.compile()

    try:
        # Save the graph to a file for debugging
        graph_image_path = "workflow_graph.png"  # Specify the file path
        compiled_workflow.get_graph().draw_mermaid_png(graph_image_path)  # Save the graph as an image
        logger.info("Workflow graph saved to %s", graph_image_path)
    except Exception:
        logger.warning("Could not save workflow graph.")

    final_state = await compiled_workflow.ainvoke(initial_state)
    logger.info("Workflow finished successfully for Evaluation ID: %s", evaluation.id)
    return final_state
