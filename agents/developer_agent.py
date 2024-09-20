import logging
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

    async def assess_feasibility_and_effort(self, feature_description: str) -> tuple:
        logger.debug(f"Assessing feasibility and effort for feature: {feature_description}")
        prompt = f"{DEVELOPER_AGENT_PROMPT.format(feature=feature_description)}\n\nAdditionally, estimate the development effort required for this feature (e.g., Low, Medium, High or detailed estimate)."
        messages = [
            HumanMessage(content=prompt),
        ]
        response = await self.llm.ainvoke(messages)
        feasibility_report = response.content.strip()

        # Simplified parsing: Assume the response separates feasibility and effort by a newline
        parts = feasibility_report.split('\n')
        feasibility = parts[0].strip() if len(parts) > 0 else "No feasibility report provided."
        effort = parts[1].strip() if len(parts) > 1 else "No effort estimate provided."

        logger.debug(f"Feasibility report: {feasibility}")
        logger.debug(f"Development effort: {effort}")

        return feasibility, effort