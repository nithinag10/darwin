import asyncio
from typing import Dict, Optional
from langgraph.graph import StateGraph
import logging

from workflow.state import EvaluationState
from workflow.nodes.define_scope_node import DefineScopeNode
from workflow.nodes.fetch_product_info_node import FetchProductInfoNode
from workflow.nodes.simulate_user_interaction_node import InteractionSimulationNode
from workflow.nodes.features_suggestion_prioritization import FeatureSuggestionPrioritizationNode
from workflow.nodes.technical_feasibility_assessment import TechnicalFeasibilityAssessmentNode
from workflow.nodes.final_report_generation import FinalReportGenerationNode
from workflow.nodes.ai_feature_ideation_node import AIFeatureIdeationNode

from agents.product_manager_agent import ProductManagerAgent
from agents.user_agent import UserAgent
from agents.ai_features_ideation_agent import AIFeatureIdeationAgent
from agents.developer_agent import DeveloperAgent

from services.RAGService import RAGService
from models.Evaluation import Evaluation

logger = logging.getLogger(__name__)

async def run_evaluation_workflow(
    evaluation: Evaluation,
    evaluation_type: str,
    rag_service: RAGService,
    product_manager_agent: ProductManagerAgent,
    user_agent: UserAgent,
    ai_feature_ideation_agent: AIFeatureIdeationAgent,
    developer_agent: DeveloperAgent
) -> Optional[Dict]:
    """
    Runs the evaluation workflow using LangGraph.
    """
    # Initialize workflow with state_schema
    workflow = StateGraph(state_schema=EvaluationState)

    # Instantiate node classes
    define_scope = DefineScopeNode()
    fetch_product_info = FetchProductInfoNode(rag_service)
    interaction_simulation = InteractionSimulationNode(user_agent)
    ai_feature_ideation = AIFeatureIdeationNode(ai_feature_ideation_agent)
    feature_suggestion_prioritization = FeatureSuggestionPrioritizationNode(product_manager_agent)
    technical_feasibility_assessment = TechnicalFeasibilityAssessmentNode(developer_agent)
    final_report_generation = FinalReportGenerationNode(product_manager_agent)

    # Add nodes to the workflow
    workflow.add_node("define_scope", define_scope)
    workflow.add_node("fetch_product_info", fetch_product_info)
    workflow.add_node("interaction_simulation", interaction_simulation)
    workflow.add_node("ai_feature_ideation", ai_feature_ideation)
    workflow.add_node("feature_suggestion_prioritization", feature_suggestion_prioritization)
    workflow.add_node("technical_feasibility_assessment", technical_feasibility_assessment)
    workflow.add_node("final_report_generation", final_report_generation)

    # Set entry and finish points
    workflow.set_entry_point("define_scope")  # Set entry point
    workflow.set_finish_point("final_report_generation")  # Set finish point

    # Define edges
    workflow.add_edge("define_scope", "fetch_product_info")
    workflow.add_edge("fetch_product_info", "interaction_simulation")
    workflow.add_edge("interaction_simulation", "ai_feature_ideation")
    workflow.add_edge("ai_feature_ideation", "feature_suggestion_prioritization")
    workflow.add_edge("feature_suggestion_prioritization", "technical_feasibility_assessment")
    workflow.add_edge("technical_feasibility_assessment", "final_report_generation")

    # Initialize state
    initial_state: EvaluationState = {
        "evaluation": evaluation,
        "evaluation_type": evaluation_type,
        "user_agent": user_agent,
        "rag_service": rag_service,
        "ai_feature_ideation_agent": ai_feature_ideation_agent,
        "developer_agent": developer_agent,
        "product_manager_agent": product_manager_agent,
        "evaluation_scope": evaluation_type,
        "product_info": "",
        "interaction_result": {},
        "ideated_features": [],
        "prioritized_features": [],
        "feasibility_reports": {},
        "final_report": "",
        "product_id": evaluation.product_id
    }

    # Compile the workflow
    compiled_workflow = workflow.compile()

    try:
        # Save the graph to a file for debugging
        graph_image_path = "workflow_graph.png"  # Specify the file path
        compiled_workflow.get_graph().draw_mermaid_png(graph_image_path)  # Save the graph as an image
        logger.info("Workflow graph saved to %s", graph_image_path)
    except Exception as e:
        logger.warning("Could not save workflow graph. Error: %s", str(e))

    final_state = await compiled_workflow.ainvoke(initial_state)
    logger.info("Workflow finished successfully for Evaluation ID: %s", evaluation.id)
    logger.debug(f"Final Report: {final_state.get('final_report')}")
    return final_state