"""
In-memory rolling audio buffer management.
Stores recent audio data for processing and analysis.
"""

import numpy as np
import threading
import logging
from collections import deque
from typing import Optional

logger = logging.getLogger(__name__)


class AudioBuffer:
    """
    Manages a rolling circular buffer for audio data.
    Automatically removes old data as new audio arrives.
    """

    def __init__(self, duration_seconds: float, sample_rate: int = 16000):
        """
        Initialize audio buffer.
        
        Args:
            duration_seconds: Duration of rolling buffer in seconds
            sample_rate: Sample rate in Hz
        """
        self.sample_rate = sample_rate
        self.duration_seconds = duration_seconds
        self.max_samples = int(sample_rate * duration_seconds)
        
        # Use deque for automatic overflow removal
        self.buffer = deque(maxlen=self.max_samples)
        self.lock = threading.RLock()
        
        logger.info(f"AudioBuffer initialized: {duration_seconds}s @ {sample_rate}Hz")

    def add_chunk(self, audio_chunk: np.ndarray):
        """Add audio chunk to buffer."""
        with self.lock:
            # Convert to float32 if needed
            if audio_chunk.dtype != np.float32:
                audio_chunk = audio_chunk.astype(np.float32)
            
            # Add samples one by one to deque
            for sample in audio_chunk:
                self.buffer.append(sample)

    def get_audio(self, duration_seconds: Optional[float] = None) -> np.ndarray:
        """
        Get audio from buffer.
        
        Args:
            duration_seconds: Duration to retrieve. If None, returns entire buffer.
        
        Returns:
            Audio data as numpy array.
        """
        with self.lock:
            if not self.buffer:
                return np.array([], dtype=np.float32)
            
            if duration_seconds is None:
                return np.array(list(self.buffer), dtype=np.float32)
            
            # Calculate samples to retrieve
            samples_to_get = int(self.sample_rate * duration_seconds)
            if samples_to_get > len(self.buffer):
                samples_to_get = len(self.buffer)
            
            # Get the most recent samples
            return np.array(list(self.buffer)[-samples_to_get:], dtype=np.float32)

    def clear(self):
        """Clear the entire buffer."""
        with self.lock:
            self.buffer.clear()

    def get_duration(self) -> float:
        """Get current duration of audio in buffer."""
        with self.lock:
            return len(self.buffer) / self.sample_rate

    def is_full(self) -> bool:
        """Check if buffer is at maximum capacity."""
        with self.lock:
            return len(self.buffer) >= self.max_samples

    def get_energy_level(self) -> float:
        """
        Calculate RMS energy level of buffer (0-1 scale).
        Useful for VAD and voice detection.
        """
        with self.lock:
            if not self.buffer:
                return 0.0
            
            audio_array = np.array(list(self.buffer), dtype=np.float32)
            rms = np.sqrt(np.mean(audio_array ** 2))
            
            # Normalize to 0-1 range using typical speech levels
            energy_level = min(rms / 0.1, 1.0)
            return energy_level
