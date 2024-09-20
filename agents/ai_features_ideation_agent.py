import logging
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from agents.utils.prompt_definitions import AI_FEATURE_IDEATION_PROMPT
from config import settings
import json

logger = logging.getLogger(__name__)

class AIFeatureIdeationAgent:
    def __init__(self):
        model_api = settings.model_api
        model_name = settings.model_name

        logger.debug(f"Initializing AIFeatureIdeationAgent with model_api: {model_api} and model_name: {model_name}")

        if model_api == "groq":
            self.llm = ChatGroq(api_key=settings.model_api_key, temperature=settings.temperature, model_name=model_name)
            logger.debug("Using ChatGroq model for AI Feature Ideation.")
        elif model_api == "openai":
            self.llm = ChatOpenAI(
                api_key=settings.openai_api_key,
                temperature=settings.temperature,
                model_name=model_name
            )
            logger.debug("Using ChatOpenAI model for AI Feature Ideation.")
        else:
            logger.error("Unsupported model API for AI Feature Ideation Agent.")
            raise ValueError("Unsupported model API")

    async def ideate_features(self, feature_gaps: list, product_info: str) -> list:
        logger.debug(f"Ideating features based on gaps: {feature_gaps}")
        prompt = AI_FEATURE_IDEATION_PROMPT.format(feature_gaps=", ".join(feature_gaps), product_info=product_info)
        messages = [
            HumanMessage(content=prompt),
        ]
        response = await self.llm.ainvoke(messages)
        logger.debug(f"Received feature ideation response: {response.content}")
        # Assuming the response is a JSON list of features
        try:
            ideated_features = json.loads(response.content)
            if isinstance(ideated_features, list):
                logger.debug(f"Ideated features: {ideated_features}")
                return ideated_features
            else:
                logger.warning("Ideated features response is not a list.")
                return []
        except json.JSONDecodeError:
            # Fallback: Split by lines
            ideated_features = response.content.split('\n')
            state_features = [feature.strip() for feature in ideated_features if feature.strip()]
            logger.debug(f"Ideated features: {state_features}")
            return state_features