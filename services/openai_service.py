"""
Service for interacting with the OpenAI API.
"""

import os
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)

class OpenAIService:
    def __init__(self):
        """
        Initialize the OpenAI service.
        """
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)
        
    def generate_response(self, messages, max_tokens=500, temperature=0.7, model="gpt-3.5-turbo"):
        """
        Generate a response from the OpenAI API.
        
        Args:
            messages (list): List of message dictionaries for the conversation
            max_tokens (int): Maximum number of tokens to generate
            temperature (float): Temperature parameter for generation
            model (str): Model to use for generation
            
        Returns:
            str: The generated response text
        """
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating response from OpenAI API: {e}")
            raise