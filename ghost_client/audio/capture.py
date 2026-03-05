"""
WASAPI Loopback Audio Capture for Windows.
Captures system audio (voice from video calls) in real-time.
"""

import numpy as np
import threading
import logging
from collections import deque
from typing import Optional, Callable
import pyaudio

logger = logging.getLogger(__name__)


class AudioCapture:
    """
    Captures system audio using WASAPI loopback on Windows.
    This captures the voice of the remote person during video calls.
    """

    def __init__(self, sample_rate: int = 16000, chunk_size: int = 1024):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.is_recording = False
        
        self.p = None
        self.stream = None
        self.capture_thread = None
        
        self.audio_queue = deque(maxlen=1000)  # Store recent audio chunks
        self.callback = None  # Optional callback for each chunk
        
        self._find_loopback_device()

    def _find_loopback_device(self):
        """Find the WASAPI loopback device on Windows."""
        try:
            self.p = pyaudio.PyAudio()
            
            # Look for "Stereo Mix" or "WASAPI Loopback" device
            loopback_index = None
            for i in range(self.p.get_device_count()):
                info = self.p.get_device_info_by_index(i)
                device_name = info['name'].lower()
                
                if any(keyword in device_name for keyword in ['stereo mix', 'loopback', 'what u hear']):
                    loopback_index = i
                    logger.info(f"Found loopback device: {info['name']} (index: {i})")
                    break
            
            if loopback_index is None:
                logger.warning("Stereo Mix/Loopback device not found. Capturing from default input.")
                loopback_index = None  # Fall back to default
                
            self.loopback_index = loopback_index
            
        except Exception as e:
            logger.error(f"Error finding loopback device: {e}")
            self.loopback_index = None

    def start(self, callback: Optional[Callable] = None):
        """Start capturing audio."""
        if self.is_recording:
            logger.warning("Audio capture already running")
            return
        
        self.callback = callback
        self.is_recording = True
        
        try:
            # Open audio stream
            self.stream = self.p.open(
                format=pyaudio.paFloat32,
                channels=1,
                rate=self.sample_rate,
                input=True,
                input_device_index=self.loopback_index,
                frames_per_buffer=self.chunk_size,
                stream_callback=None,  # Non-blocking mode
            )
            
            # Start capture thread
            self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
            self.capture_thread.start()
            
            logger.info("Audio capture started")
            
        except Exception as e:
            logger.error(f"Error starting audio capture: {e}")
            self.is_recording = False

    def _capture_loop(self):
        """Main audio capture loop."""
        while self.is_recording:
            try:
                # Read audio chunk
                audio_data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                
                # Convert byte string to numpy array
                audio_chunk = np.frombuffer(audio_data, dtype=np.float32)
                
                # Add to queue
                self.audio_queue.append(audio_chunk)
                
                # Trigger callback if provided
                if self.callback:
                    self.callback(audio_chunk)
                    
            except Exception as e:
                logger.error(f"Error in capture loop: {e}")
                break

    def stop(self):
        """Stop capturing audio."""
        if not self.is_recording:
            return
        
        self.is_recording = False
        
        if self.capture_thread:
            self.capture_thread.join(timeout=2)
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        
        if self.p:
            self.p.terminate()
        
        logger.info("Audio capture stopped")

    def get_buffer(self) -> np.ndarray:
        """Get all buffered audio as a single array."""
        if not self.audio_queue:
            return np.array([], dtype=np.float32)
        
        return np.concatenate(list(self.audio_queue))

    def clear_buffer(self):
        """Clear the audio buffer."""
        self.audio_queue.clear()

    def __del__(self):
        """Cleanup on destruction."""
        if self.is_recording:
            self.stop()
