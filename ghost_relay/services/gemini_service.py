"""
Gemini 3 Flash API Integration.
Securely sends prompts to Google Gemini and receives AI responses.
"""

import os
import logging
from typing import Optional
import time

logger = logging.getLogger(__name__)


class GeminiService:
    """
    Service for interfacing with Google's Gemini 3 Flash API.
    """

    def __init__(self):
        """Initialize Gemini service."""
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model_name = "gemini-1.5-flash"
        self.client = None
        self.max_retries = 3
        
        self._initialize_client()

    def _initialize_client(self):
        """Initialize Gemini client."""
        try:
            if not self.api_key:
                logger.error("GEMINI_API_KEY environment variable not set")
                return
            
            import google.generativeai as genai
            
            genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel(self.model_name)
            
            logger.info(f"Gemini client initialized with model: {self.model_name}")
            
        except ImportError:
            logger.error("google-generativeai not installed. Run: pip install google-generativeai")
        except Exception as e:
            logger.error(f"Error initializing Gemini client: {e}")

    def is_ready(self) -> bool:
        """Check if service is ready to use."""
        return self.client is not None and self.api_key is not None

    def generate_response(self, prompt: str, max_tokens: int = 256) -> str:
        """
        Generate a response using Gemini 3 Flash.
        
        Args:
            prompt: Input text to generate response for
            max_tokens: Maximum tokens in response
        
        Returns:
            Generated text response
        """
        if not self.is_ready():
            logger.error("Gemini service not ready")
            return ""
        
        try:
            logger.debug(f"Generating response for: {prompt[:100]}...")
            
            # Add system prompt for call context
            system_message = """You are an AI assistant helping someone during a video call. 
Generate a concise, natural response that the user can quickly read and incorporate into their call.
Keep responses brief (1-2 sentences) and conversational."""
            
            full_prompt = f"{system_message}\n\nUser message: {prompt}"
            
            # Generate response with retries
            for attempt in range(self.max_retries):
                try:
                    response = self.client.generate_content(full_prompt)
                    
                    if response and response.text:
                        result = response.text.strip()
                        logger.info(f"Generated: {result[:100]}...")
                        return result
                    else:
                        logger.warning("Empty response from Gemini")
                        return ""
                        
                except Exception as e:
                    logger.warning(f"Attempt {attempt + 1}/{self.max_retries} failed: {e}")
                    if attempt < self.max_retries - 1:
                        time.sleep(1)  # Wait before retry
                    else:
                        raise
            
            return ""
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return ""

    def generate_response_multimodal(self, text: str, image_data: Optional[bytes] = None) -> str:
        """
        Generate response with optional image input (for future use).
        
        Args:
            text: Text prompt
            image_data: Optional image data
        
        Returns:
            Generated response
        """
        if not self.is_ready():
            logger.error("Gemini service not ready")
            return ""
        
        try:
            if image_data:
                # TODO: Implement image handling
                logger.warning("Image handling not yet implemented")
            
            return self.generate_response(text)
            
        except Exception as e:
            logger.error(f"Error in multimodal generation: {e}")
            return ""

    def create_conversation_context(self, conversation_history: list) -> str:
        """
        Create context from conversation history for coherent responses.
        
        Args:
            conversation_history: List of previous messages
        
        Returns:
            Contextualized prompt
        """
        context = "Previous context:\n"
        for msg in conversation_history[-5:]:  # Keep last 5 messages
            context += f"- {msg}\n"
        return context
