import logging
import json
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from agents.utils.prompt_definitions import DEVELOPER_AGENT_PROMPT
from config import settings

logger = logging.getLogger(__name__)

class DeveloperAgent:
    def __init__(self):
        model_api = settings.model_api
        model_name = settings.model_name

        logger.debug(f"Initializing DeveloperAgent with model_api: {model_api} and model_name: {model_name}")

        if model_api == "groq":
            self.llm = ChatGroq(api_key=settings.model_api_key, temperature=settings.temperature, model_name=model_name)
            logger.debug("Using ChatGroq model for Developer Agent.")
        elif model_api == "openai":
            self.llm = ChatOpenAI(
                api_key=settings.openai_api_key,
                temperature=settings.temperature,
                model_name=model_name
            )
            logger.debug("Using ChatOpenAI model for Developer Agent.")
        else:
            logger.error("Unsupported model API for Developer Agent.")
            raise ValueError("Unsupported model API")

    async def assess_feasibility_and_effort(self, features: str) -> dict:
        logger.debug(f"Assessing feasibility and effort for feature: {features}")
        prompt = DEVELOPER_AGENT_PROMPT.format(features=features)
        messages = [
            HumanMessage(content=prompt),
        ]
        response = await self.llm.ainvoke(messages)
        response_content = response.content.strip()

        logger.debug(f"Received raw response: {response_content}")

        # Extract JSON from the response
        try:
            # Ensure that the response is a valid JSON
            feasibility_data_list = json.loads(response_content)

            logger.debug(f"Feasibility data list: {feasibility_data_list}")

            return feasibility_data_list
        except json.JSONDecodeError as e:
            logger.error("Failed to parse JSON response from Developer Agent.")
            logger.error(f"JSONDecodeError: {e}")
            logger.debug("Attempting to extract JSON manually.")

            # Attempt to extract JSON from the response using regex or other methods if necessary
            # For simplicity, return default values
            return [
                {
                    "feature": "Feature 1",
                    "feasibility_report": "Could not parse feasibility report.",
                    "development_effort": "Unknown"
                }
            ]