from google import genai
from google.genai import types
from app.config import settings
from app.core.logger import logger

class GeminiAgentClient:
    def __init__(self):
        # Initialize the official Google GenAI client
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model_name = settings.GEMINI_MODEL_NAME
        logger.info("Initialized GeminiAgentClient with google-genai SDK.")

    def generate_response(self, contents: list, tools: list = None, system_instruction: str = None) -> types.GenerateContentResponse:
        """
        Sends conversation history to Gemini 2.5 Flash, along with system prompts and native tools.
        """
        # Configure generation settings and tools
        config = types.GenerateContentConfig(
            temperature=0.3,
            max_output_tokens=1024,
            system_instruction=system_instruction
        )
        
        if tools:
            config.tools = tools

        try:
            logger.info(f"Invoking Gemini model '{self.model_name}'...")
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=config
            )
            return response
        except Exception as e:
            logger.error(f"Error calling Gemini API: {str(e)}")
            raise e

gemini_agent_client = GeminiAgentClient()
