"""
WebSocket/HTTP Client for communicating with the secure relay server.
Handles transcription submission and response retrieval.
"""

import requests
import json
import logging
import asyncio
import aiohttp
from typing import Optional, Dict, Any
import numpy as np

logger = logging.getLogger(__name__)


class RelayClient:
    """
    Client for communicating with the GHOST relay server.
    Sends transcribed text and receives AI-generated responses.
    """

    def __init__(self, host: str = "localhost", port: int = 8000, 
                 protocol: str = "http", timeout: int = 30):
        """
        Initialize relay client.
        
        Args:
            host: Relay server hostname/IP
            port: Relay server port
            protocol: Protocol ('http' or 'https')
            timeout: Request timeout in seconds
        """
        self.base_url = f"{protocol}://{host}:{port}"
        self.timeout = timeout
        self.api_key = None  # Will be set later if needed
        
        logger.info(f"RelayClient initialized: {self.base_url}")

    def set_api_key(self, api_key: str):
        """Set API key for authentication."""
        self.api_key = api_key
        logger.debug("API key set")

    def transcribe(self, audio_data: np.ndarray, sample_rate: int = 16000) -> str:
        """
        Send audio to server for transcription.
        
        Args:
            audio_data: Audio samples as numpy array
            sample_rate: Sample rate in Hz
        
        Returns:
            Transcribed text from server
        """
        try:
            # For now, return empty (client will do local STT)
            # This is for future cloud-based STT support
            return ""
        except Exception as e:
            logger.error(f"Transcription request failed: {e}")
            return ""

    def generate_response(self, text: str) -> str:
        """
        Send text to server and get AI-generated response.
        
        Args:
            text: Text to send to Gemini
        
        Returns:
            Generated response from Gemini API
        """
        try:
            endpoint = f"{self.base_url}/api/generate"
            
            payload = {
                "text": text,
            }
            
            if self.api_key:
                payload["api_key"] = self.api_key
            
            response = requests.post(
                endpoint,
                json=payload,
                timeout=self.timeout,
            )
            
            response.raise_for_status()
            
            data = response.json()
            generated_text = data.get("response", "")
            
            logger.info(f"Generated response: {generated_text[:100]}...")
            return generated_text
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request to relay server failed: {e}")
            return ""
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response from server: {e}")
            return ""
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return ""

    def health_check(self) -> bool:
        """Check if relay server is reachable."""
        try:
            endpoint = f"{self.base_url}/health"
            response = requests.get(endpoint, timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Health check failed: {e}")
            return False

    async def generate_response_async(self, text: str) -> str:
        """
        Asynchronously generate response (non-blocking).
        
        Args:
            text: Text to send to Gemini
        
        Returns:
            Generated response
        """
        try:
            endpoint = f"{self.base_url}/api/generate"
            
            payload = {
                "text": text,
            }
            
            if self.api_key:
                payload["api_key"] = self.api_key
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    endpoint,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    data = await response.json()
                    return data.get("response", "")
                    
        except Exception as e:
            logger.error(f"Async generation error: {e}")
            return ""

    def send_log(self, log_data: Dict[str, Any]) -> bool:
        """Send debug logs to server (for analytics)."""
        try:
            endpoint = f"{self.base_url}/api/logs"
            response = requests.post(
                endpoint,
                json=log_data,
                timeout=self.timeout,
            )
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Failed to send logs: {e}")
            return False
