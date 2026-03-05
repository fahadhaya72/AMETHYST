"""
Speech-to-Text (STT) Engine Integration.
Supports Whisper, Azure Speech, and Google Cloud Speech.
"""

import numpy as np
import logging
from typing import Optional
import asyncio

logger = logging.getLogger(__name__)


class STTEngine:
    """
    Speech-to-Text engine for transcribing audio to text.
    Supports multiple STT providers.
    """

    def __init__(self, engine: str = "whisper", model_size: str = "base", language: str = "en"):
        """
        Initialize STT Engine.
        
        Args:
            engine: STT engine to use ('whisper', 'azure', 'google')
            model_size: Model size for Whisper ('tiny', 'base', 'small', 'medium', 'large')
            language: Language code (e.g., 'en', 'es', 'fr')
        """
        self.engine = engine.lower()
        self.model_size = model_size
        self.language = language
        self.model = None
        
        self._initialize_engine()

    def _initialize_engine(self):
        """Initialize the selected STT engine."""
        try:
            if self.engine == "whisper":
                self._init_whisper()
            elif self.engine == "azure":
                self._init_azure()
            elif self.engine == "google":
                self._init_google()
            else:
                logger.error(f"Unknown STT engine: {self.engine}")
                
        except Exception as e:
            logger.error(f"Error initializing STT engine: {e}")

    def _init_whisper(self):
        """Initialize OpenAI Whisper."""
        try:
            import whisper
            logger.info(f"Loading Whisper model: {self.model_size}")
            self.model = whisper.load_model(self.model_size)
            logger.info("Whisper model loaded successfully")
        except ImportError:
            logger.error("Whisper not installed. Run: pip install openai-whisper")
        except Exception as e:
            logger.error(f"Error loading Whisper: {e}")

    def _init_azure(self):
        """Initialize Azure Speech Services."""
        try:
            import azure.cognitiveservices.speech as speechsdk
            self.azure_sdk = speechsdk
            logger.info("Azure Speech SDK loaded")
        except ImportError:
            logger.error("Azure Speech SDK not installed. Run: pip install azure-cognitiveservices-speech")

    def _init_google(self):
        """Initialize Google Cloud Speech."""
        try:
            from google.cloud import speech_v1
            self.google_client = speech_v1.SpeechClient()
            logger.info("Google Cloud Speech client initialized")
        except ImportError:
            logger.error("Google Cloud Speech not installed. Run: pip install google-cloud-speech")

    def transcribe(self, audio_data: np.ndarray, sample_rate: int = 16000) -> str:
        """
        Transcribe audio to text.
        
        Args:
            audio_data: Audio data as numpy array
            sample_rate: Sample rate in Hz
        
        Returns:
            Transcribed text
        """
        try:
            if self.engine == "whisper":
                return self._transcribe_whisper(audio_data, sample_rate)
            elif self.engine == "azure":
                return self._transcribe_azure(audio_data, sample_rate)
            elif self.engine == "google":
                return self._transcribe_google(audio_data, sample_rate)
            else:
                logger.error(f"Unknown STT engine: {self.engine}")
                return ""
                
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return ""

    def _transcribe_whisper(self, audio_data: np.ndarray, sample_rate: int) -> str:
        """Transcribe using OpenAI Whisper."""
        try:
            if self.model is None:
                logger.error("Whisper model not initialized")
                return ""
            
            # Ensure audio is float32 and normalized
            if audio_data.dtype != np.float32:
                audio_data = audio_data.astype(np.float32)
            
            # Normalize if values are too large
            max_val = np.abs(audio_data).max()
            if max_val > 1.0:
                audio_data = audio_data / (max_val + 1e-7)
            
            # Perform transcription
            logger.debug("Starting Whisper transcription...")
            result = self.model.transcribe(
                audio_data,
                language=self.language,
                fp16=False,  # Use float32
            )
            
            text = result.get("text", "").strip()
            logger.info(f"Transcribed: {text[:100]}...")
            return text
            
        except Exception as e:
            logger.error(f"Whisper transcription error: {e}")
            return ""

    def _transcribe_azure(self, audio_data: np.ndarray, sample_rate: int) -> str:
        """Transcribe using Azure Speech Services."""
        logger.warning("Azure transcription not yet implemented")
        return ""

    def _transcribe_google(self, audio_data: np.ndarray, sample_rate: int) -> str:
        """Transcribe using Google Cloud Speech."""
        logger.warning("Google Cloud transcription not yet implemented")
        return ""

    async def transcribe_async(self, audio_data: np.ndarray, sample_rate: int = 16000) -> str:
        """Asynchronous transcription (non-blocking)."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.transcribe, audio_data, sample_rate)
