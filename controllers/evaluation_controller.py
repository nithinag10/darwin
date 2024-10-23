from fastapi import APIRouter, Depends, HTTPException, Form, Body
from typing import Dict, Optional
from services.Evaluation import EvaluationService
from repositories.EvaluationRepository import EvaluationRepository
from services.RAGService import RAGService
from services.UserAgentService import UserAgentService
from agents.product_manager_agent import ProductManagerAgent
from agents.ai_features_ideation_agent import AIFeatureIdeationAgent
from agents.developer_agent import DeveloperAgent
from agents.user_agent import UserAgent
from database import transaction
from config import settings
from logging_config import setup_logging
import logging
from fastapi.encoders import jsonable_encoder
from services.chat_service import ChatService
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq

import json

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

router = APIRouter()

def get_llm():
    if settings.model_api == "groq":
        return ChatGroq(
            api_key=settings.model_api_key,
            temperature=settings.temperature,
            model_name=settings.model_name
        )
    elif settings.model_api == "openai":
        return ChatOpenAI(
            api_key=settings.openai_api_key,
            temperature=settings.temperature,
            model_name=settings.model_name
        )
    else:
        raise ValueError(f"Unsupported model API: {settings.model_api}")

@router.post("/trigger-evaluation", response_model=Dict)
async def trigger_evaluation(
    name: str = Form(...),
    product_id: int = Form(...),
    user_agent_definition_id: int = Form(...),
    evaluation_type: str = Form(...),
    db_con=Depends(transaction),
):
    # Initialize repositories and services
    evaluation_repository = EvaluationRepository(db_con[0])
    rag_service = RAGService(db_con[0])
    product_manager_agent = ProductManagerAgent(agent_characteristics=None)
    user_agent_service = UserAgentService(db_con[0])
    ai_feature_ideation_agent = AIFeatureIdeationAgent()
    developer_agent = DeveloperAgent()

    
    # Fetch user agent definition
    user_agent_definition = await user_agent_service.fetch_user_agent_definition(user_agent_definition_id)
    print("Printifn sample user agent definition", user_agent_definition)
    
    if not user_agent_definition:
        raise HTTPException(status_code=404, detail="User agent definition not found")
    
    # Access characteristics from the dictionary
    user_agent = UserAgent(agent_characteristics=user_agent_definition['characteristics'])
    
    # Initialize EvaluationService 
    evaluation_service = EvaluationService(
        evaluation_repository=evaluation_repository,
        rag_service=rag_service,
        product_manager_agent=product_manager_agent,
        user_agent=user_agent,
        ai_feature_ideation_agent=ai_feature_ideation_agent,
        developer_agent=developer_agent
    )
    
        # Create a new Evaluation and retrieve its ID
    evaluation_id = await evaluation_service.create_evaluation(name=name, product_id=product_id)
    logger.info("Created new evaluation with ID: %s", evaluation_id)
    
    # Trigger the workflow with the newly created evaluation_id
    result = await evaluation_service.trigger_workflow(
        evaluation_id=evaluation_id,
        evaluation_type=evaluation_type
    )
    logger.info("Triggered evaluation workflow with ID: %s", evaluation_id)

    return jsonable_encoder(result)

@router.post("/create-persona-chat", response_model=Dict)
async def create_persona_chat(
    data: Dict = Body(...),
    db_con=Depends(transaction),
):
    persona = data.get("persona")
    business_idea = data.get("businessIdea")

    # Initialize LLM for customer persona interaction
    llm = get_llm()

    # Step 1: Refine the business idea
    refinement_prompt = f"""
Please refine the following business idea in clear, concise language, adding necessary details to ensure clarity and focus:
Don't assume anything and write more, just rephrase and write the same. 
{business_idea}
"""
    refined_idea_response = await llm.ainvoke([{"role": "user", "content": refinement_prompt}])
    refined_business_idea = refined_idea_response.content.strip()

    # Step 2: Customer persona interaction
    # Create the customer persona prompt
    customer_persona_prompt = f"""
You are an AI assistant embodying the following customer persona:
Name: {persona['name']}
Summary: {persona['summary']}
Industry: {persona['industry']}
Demographics: {persona['demographics']}
Traits: {', '.join(persona['traits'])}
Goals: {', '.join(persona['goals'])}
Pain Points: {', '.join(persona['painPoints'])}
Emotional Tendencies: {', '.join(persona['emotionalTendencies'])}

You have just used the following product/service:
<service,product>
{refined_business_idea}
</service,product>

Remember: 
1. All you want is to achieve your goal and reduce your pain, you don't care about the business idea how good it is and about others. 
2. Remeber you are a human, you have all the feeling and emotion of a human like selfish, doubt full etc. 
3. Be human when to comes to buying decision making.
4. Don't assume anything about the product, service. Just whatever mentioned. 
5. If the buisness idea is not clear don't answer those question. 

As this customer persona, provide detailed feedback on your experience with the product/service. Focus on aspects such as:

- How well did the product address your pain points and help achieve your goals?
- What features or aspects of the product did you find most valuable or unique?
- Were there any challenges, frustrations, or confusions you encountered while using the product?
- How likely are you to continue using this product, and would you recommend it to others? Why or why not?
- Are there any improvements or additional features you would like to see?

Remember to be honest and detailed in your feedback, expressing your thoughts and feelings as this persona.

"""

    # Get customer feedback
    customer_feedback_response = await llm.ainvoke([{"role": "user", "content": customer_persona_prompt}])
    customer_feedback = customer_feedback_response.content.strip()


    business_expert_prompt = f"""
You are a business strategy expert known for providing out-of-the-box solutions and unconventional ideas. 
Given the customer feedback below and the refined business idea, provide a comprehensive analysis and actionable recommendations for the business owner.

<Customer Feedback>
{customer_feedback}
</Customer Feedback>

<Business Idea>
{refined_business_idea}
</Business Idea>

Your analysis should include:

- Key insights derived from the customer feedback.
- Identification of strengths and weaknesses of the product/service.
- Opportunities for improvement and potential areas for innovation.
- Strategic recommendations to enhance product value, market positioning, and scalability.
- Analysis of how crowded the market is and who the strong players are doing similar things also name them in the response. 
- Analys the strong player business and preapre strategy on how to win against them.
- Suggestions on how to differentiate the product/service and achieve success.
- Any eye-opening data or trends that the business owner should be aware of.
- You are well-versed in business and have read influential books like "Blue Ocean Strategy" and "The Innovator's Dilemma"; recognize patterns and provide solutions.

For each of the above points, provide a rating from 1 to 10 indicating the significance or impact, where 10 is the highest. This rating will be used to display corresponding emojis or indicators on the frontend.

Present your analysis in a clear, structured report without including the customer feedback verbatim. Focus on providing valuable insights and actionable advice to the business owner.

Provide your report in the following JSON format strictly without anything extra:

{{
  "keyInsights": "...",
  "keyInsightsRating": 8,
  "strengths": "...",
  "strengthsRating": 9,
  "weaknesses": "...",
  "weaknessesRating": 7,
  "opportunities": "...",
  "opportunitiesRating": 8,
  "marketAnalysis": "...",
  "marketAnalysisRating": 7,
  "differentiationStrategies": "...",
  "differentiationStrategiesRating": 9,
  "strategicRecommendations": "...",
  "strategicRecommendationsRating": 10,
  "importantTrends": "...",
  "importantTrendsRating": 6
}}

Note:
1. Consider only the features/services that are written in the business idea. 
2. If you don't have much information to answer some areas, convey the same without any assumed information.
3. Also, provide ideas that are outside of the business idea to encourage the user to consider pivoting.
"""

    # Get business expert analysis
    business_expert_response = await llm.ainvoke([{"role": "user", "content": business_expert_prompt}])
    business_expert_report = business_expert_response.content.strip()


    try:
        business_expert_report_json = json.loads(business_expert_report)
    except json.JSONDecodeError:
        business_expert_report_json = {"error": "Failed to parse business expert report JSON"}

    # Save the session and responses in the database
    chat_service = ChatService(db_con[0])
    session_id = await chat_service.save_chat_session(
        persona['id'],
        refined_business_idea,
        customer_persona_prompt,
        business_expert_report
    )

    # Return the structured report
    return {
        "session_id": session_id,
        "refined_business_idea": refined_business_idea,
        "business_expert_report": business_expert_report_json
    }



@router.post("/chat/{session_id}")
async def chat(
    session_id: int,
    data: Dict = Body(...),
    db_con=Depends(transaction),
):
    chat_service = ChatService(db_con[0])
    
    # Get chat session information
    session_info = await chat_service.get_chat_session(session_id)
    if not session_info:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    
    # Get chat history
    chat_history = await chat_service.get_chat_history(session_id)
    
    # Check if the chat limit has been reached
    if len(chat_history) >= 21:  # 1 initial prompt + 10 user messages + 10 AI responses
        return {"response": "Chat limit reached. You can ask a maximum of 10 questions."}
    
    # Initialize LLM
    llm = get_llm()
    
    message = data.get("message")

    # Prepare the business expert prompt
    business_expert_prompt = f"""
    You are a business strategy expert providing advice on the following business idea:

    Business Idea: {session_info['business_idea']}

    Initial Business Analysis:
    {session_info['initial_response']}

    You are now in a conversation with the business owner. Provide expert advice, insights, and answers to their questions based on the business idea, customer persona, and initial analysis. Be concise, practical, and insightful in your responses.

    Current conversation:
    """

    # Prepare messages for LLM
    messages = [{"role": "system", "content": business_expert_prompt}]
    messages.extend([{"role": "user" if msg["is_user"] else "assistant", "content": msg["content"]} for msg in chat_history])
    messages.append({"role": "user", "content": message})

    # Get response from LLM
    response = await llm.ainvoke(messages)

    # Save the new message and response
    await chat_service.save_chat_message(session_id, message, is_user=True)
    await chat_service.save_chat_message(session_id, response.content, is_user=False)

    # Check if this was the last allowed message
    remaining_messages = 10 - (len(chat_history) - 1) // 2
    if remaining_messages <= 1:
        return {"response": response.content, "message": "This was your last question. Chat limit reached."}
    else:
        return {"response": response.content, "remaining_messages": remaining_messages - 1}
