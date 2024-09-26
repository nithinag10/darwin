import logging
from typing import Dict, Any, List, Optional
from langchain.chains.summarize import load_summarize_chain
from langchain.schema import Document
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

import json
from config import settings
from langchain_core.rate_limiters import InMemoryRateLimiter
from langchain.text_splitter import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

class FigmaDataTransformer:
    """
    Transforms Figma JSON data by extracting useful information such as screens, texts, buttons,
    actions, and navigation. Utilizes LangChain's Map-Reduce summarization method with ChatOpenAI to ensure
    comprehensive and relationship-preserving extraction while optimizing for performance and cost.
    """

    def __init__(self):
        """
        Initializes the FigmaDataTransformer with a specified LLM model and temperature.
        """
        self.rate_limiter = InMemoryRateLimiter(
            requests_per_second=0.5,  # Adjusted rate limiter for ChatOpenAI
            check_every_n_seconds=0.1,
            max_bucket_size=5,
        )

        # Initialize ChatOpenAI LLM
        self.llm = ChatOpenAI(
            temperature=settings.temperature,
            model_name="gpt-3.5-turbo",
            openai_api_key=settings.openai_api_key
        )

        # Define the Question Prompt Template
        final_combine_prompt = """Extract and summarize the essential functional components from the following Figma design data to understand the product's workflow and functionality.
Provide a structured JSON output in the format:

{{
  "screens": {{
    "Screen Name": {{
      "texts": ["List of text elements"],
      "buttons": [
        {{
          "name": "Button Name",
          "actions": ["List of actions"],
          "navigation": "Destination Screen Name"
        }}
      ],
      "navigations": ["List of navigations if any"]
    }}
  }}
}}

Data to process:
{text}
"""
        chunks_prompt="""
You are export figma design reader, Extract and summarize the essential functional components from the following Figma design data to understand the product's workflow and functionality fully just by seeing it. 
DesignCode:`{text}'
Summary:
"""
        map_prompt_template=PromptTemplate(input_variables=['text'],
                                    template=chunks_prompt)
        
        final_combine_prompt_template=PromptTemplate(input_variables=['text'],
                                             template=final_combine_prompt)

        # Initialize Text Splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=10000,
            chunk_overlap=20
        )

        # Load the summarize chain with 'map_reduce' type
        self.chain = load_summarize_chain(
            llm=self.llm,
            chain_type="map_reduce",
            map_prompt=map_prompt_template,
            combine_prompt=final_combine_prompt_template,
            verbose=True
        )

    def extract_useful_info(self, figma_data: dict) -> Dict[str, Any]:
        """
        Extracts useful information from Figma data using a two-step process:
        initial extraction and map-reduce summarization.

        :param figma_data: The raw Figma JSON data.
        :return: A dictionary containing the structured and refined information.
        """

        # Initial extraction to filter out non-essential data while preserving structure
        initial_extracted = self._first_level_transfer(figma_data)
        logger.debug(f"Initial extraction result: {initial_extracted}")

        # Write initial_extracted to a file
        with open('initial_extracted.json', 'w') as f:
            json.dump(initial_extracted, f, indent=2)  # Save as JSON with indentation

        print(json.dumps(initial_extracted))

        # Convert the extracted data to a text format
        extracted_text = self._figma_json_to_text(initial_extracted)
        logger.debug(f"Extracted text for LLM processing: {extracted_text}")

        # Split the text into manageable chunks
        chunks = self.text_splitter.split_text(extracted_text)
        logger.debug(f"Number of chunks created: {len(chunks)}")

        documents = self.text_splitter.create_documents(chunks)

        length_of_text = len(documents)

        for chunk in chunks:
            print(self.llm.get_num_tokens(chunk))

        # Run the summarize chain
        try:
            summarized_text = self.chain.run(documents)
    
            # Write summarized_text to a file
            with open('summarized_text.txt', 'w') as f:
                f.write(summarized_text)  # Save summarized text 

            logger.debug(f"Summarized text: {summarized_text}")
            structured_data = self._parse_summary(summarized_text)
            logger.debug(f"Structured Data after parsing summary: {structured_data}")
            return structured_data
        except Exception as e:
            logger.error(f"Error during summarization: {e}")
            return {}

    def _figma_json_to_text(self, figma_data: dict) -> str:
        """
        Converts Figma JSON data to a plain text string suitable for LLM processing.

        :param figma_data: The raw Figma JSON data.
        :return: A string representation of the Figma data.
        """
        return json.dumps(figma_data, indent=2)

    def _parse_summary(self, summary: str) -> dict:
        """
        Parses the LLM summary into a structured dictionary.

        :param summary: The summary string returned by the LLM.
        :return: A structured dictionary containing screens, texts, buttons, actions, and navigations.
        """
        try:
            structured_data = json.loads(summary)
            return structured_data
        except json.JSONDecodeError:
            logger.warning("LLM summary is not in JSON format. Returning raw summary.")
            return {"summary": summary}

    def _first_level_transfer(self, figma_data: dict) -> dict:
        """
        Extracts useful information from Figma JSON data while retaining the tree structure and hierarchy.
        Removes unuseful data such as UI-specific details (colors, text placement, etc.).

        :param figma_data: The raw Figma JSON data.
        :return: A dictionary containing the extracted useful information with preserved hierarchy.
        """
        useful_info = {
            "screens": {}
        }

        def traverse(node, parent_screen: Optional[str] = None):
            node_type = node.get('type')
            node_name = node.get('name', 'Unnamed')

            # Identify screens (e.g., FRAME, PAGE, CANVAS)
            if node_type in ['FRAME', 'PAGE', 'CANVAS', 'DOCUMENT']:
                current_screen = node_name
                if current_screen not in useful_info["screens"]:
                    useful_info["screens"][current_screen] = {
                        "children": [],
                        "texts": [],
                        "buttons": [],
                        "navigations": []
                    }
                logger.debug(f"Identified screen: {current_screen}")
            else:
                current_screen = parent_screen

            extracted_node = {}
            if current_screen:
                # Retain the node's type and name
                extracted_node["type"] = node_type
                extracted_node["name"] = node_name

                # Extract text elements
                if node_type == 'TEXT':
                    text_content = node.get('characters', '').strip()
                    if text_content:
                        extracted_node["text"] = text_content
                        useful_info["screens"][current_screen]["texts"].append(text_content)
                        logger.debug(f"Extracted text: '{text_content}' on screen: {current_screen}")

                # Extract interactive elements like buttons
                elif node_type in ['BUTTON', 'COMPONENT', 'RECTANGLE', 'VECTOR', 'ELLIPSE', 'POLYGON', 'STAR']:
                    interactions = node.get('interactions', [])
                    for interaction in interactions:
                        trigger = interaction.get('trigger', {}).get('type')
                        action_type = interaction.get('action', {}).get('type')
                        destination_id = interaction.get('action', {}).get('destinationId')

                        if trigger and action_type:
                            destination = self._map_destination(destination_id, figma_data) if destination_id else None
                            button_info = {
                                "name": node_name,
                                "actions": [action_type],
                                "navigation": destination
                            }
                            useful_info["screens"][current_screen]["buttons"].append(button_info)
                            logger.debug(f"Extracted button: {button_info} on screen: {current_screen}")

                # Extract navigations if available
                navigations = node.get('navigation', [])
                if navigations:
                    useful_info["screens"][current_screen]["navigations"].extend(navigations)
                    logger.debug(f"Extracted navigations: {navigations} on screen: {current_screen}")

                # Retain relevant children
                children = node.get('children', [])
                if children:
                    extracted_node["children"] = []
                    for child in children:
                        child_extracted = traverse(child, current_screen)
                        if child_extracted:
                            extracted_node["children"].append(child_extracted)

                if extracted_node:
                    useful_info["screens"][current_screen]["children"].append(extracted_node)

            else:
                # If not within a recognized screen, still traverse children without extraction
                children = node.get('children', [])
                for child in children:
                    traverse(child, current_screen)

            return extracted_node if extracted_node else None

        document = figma_data.get('document', {})
        traverse(document)

        return useful_info

    def _map_destination(self, destination_id: str, figma_data: dict) -> str:
        """
        Maps destinationId to the corresponding screen name.

        :param destination_id: The destination node ID from Figma interactions.
        :param figma_data: The raw Figma JSON data.
        :return: The name of the destination screen if found, else the destination_id itself.
        """
        # Traverse the document to find the node with the given ID
        def find_node(node, target_id):
            if node.get('id') == target_id:
                return node.get('name', 'Unnamed')
            for child in node.get('children', []):
                result = find_node(child, target_id)
                if result:
                    return result
            return None

        screen_name = find_node(figma_data.get('document', {}), destination_id)
        if screen_name:
            logger.debug(f"Mapped destination ID {destination_id} to screen: {screen_name}")
            return screen_name
        else:
            logger.warning(f"Could not map destination ID {destination_id} to any screen.")
            return destination_id  # Fallback to ID if mapping not found