import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from agents.utils.prompt_definitions import (
    PROJECT_MANAGER_PROMPT,
    FINAL_REPORT_PROMPT,
    PRIORITIZATION_PROMPT  # Imported the new prompt
)
from agents.utils.prompt_provider import PromptProvider
from config import settings 
from typing import List, Dict
import json

class ProductManagerAgent:
    def __init__(self, agent_characteristics: dict):
        self.characteristics = agent_characteristics
        model_api = settings.model_api  # Retrieved from config.py
        model_name = settings.model_name  # Retrieved from config.py

        logging.debug(f"Initializing ProjectManagerAgent with model_api: {model_api} and model_name: {model_name}")  # {{ edit_3 }}

        if model_api == "groq":
            self.llm = ChatGroq(api_key=settings.model_api_key, temperature=settings.temperature, model_name=model_name)
        elif model_api == "openai":
            self.llm = ChatOpenAI(
                api_key=settings.openai_api_key,
                temperature=settings.temperature,
                model_name=model_name
            )
        else:
            logging.error("Unsupported model API")
            raise ValueError("Unsupported model API")

    async def define_evaluation_scope(self, evaluation_context: str) -> str:
        logging.debug(f"Defining evaluation scope for context: {evaluation_context}")
        messages = [
            HumanMessage(content=PROJECT_MANAGER_PROMPT),
            HumanMessage(content=f"Define the evaluation scope for: {evaluation_context}")
        ]
        response = await self.llm.ainvoke(messages)
        logging.debug(f"Received response: {response.content}")
        return response.content
    
    async def generate_final_report(self, pain_points: str, solutions: str, feasibility_reports: List, prioritized_tasks: str) -> str:
        logging.debug("Generating final report.")
        prompt = FINAL_REPORT_PROMPT.format(
            pain_points=pain_points,
            solutions=solutions,
            development_effort=feasibility_reports,
            prioritized_tasks=prioritized_tasks
        )
        messages = [
            HumanMessage(content=prompt),
        ]
        response = await self.llm.ainvoke(messages)
        final_report = response.content.strip()
        logging.debug("Final report generated successfully.")
        return final_report

    async def prioritize_features(self, features: List[Dict], pain_points: List[str], user_feedback: Dict) -> List[Dict]:
        """
        Prioritizes features based on their impact and effort required.

        Args:
            features (List[Dict]): List of ideated features.
            pain_points (List[str]): List of pain points.
            user_feedback (Dict): User feedback data.

        Returns:
            List[Dict]: List of prioritized features with ranks.
        """
        logging.debug("Starting feature prioritization.")
        
        # Prepare the features string for the prompt
        features_str = "\n".join([f"- {feature['feature_name']}: {feature['description']}" for feature in features])
        pain_points_str = "\n".join([f"- {point}" for point in pain_points])
        # Assuming user_feedback is a dictionary with relevant keys
        user_feedback_str = "\n".join([f"- {key}: {value}" for key, value in user_feedback.items()])

        # Format the prompt with the provided data
        prompt = PRIORITIZATION_PROMPT.format(
            features=features_str,
            pain_points=pain_points_str,
            user_feedback=user_feedback_str
        )

        messages = [
            HumanMessage(content=prompt),
        ]

        logging.debug(f"Sending prioritization prompt to LLM: {prompt}")
        response = await self.llm.ainvoke(messages)
        logging.debug(f"Received prioritization response: {response.content}")

        try:
            response_content = response.content
            prioritized_features = json.loads(response_content)
            logging.debug(f"Parsed prioritized features: {prioritized_features}")
            return prioritized_features
        except ValueError as e:
            logging.error("Failed to parse JSON response from prioritization prompt.")
            raise e