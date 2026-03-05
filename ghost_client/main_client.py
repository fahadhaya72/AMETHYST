"""
GHOST Main Client - Entry point orchestrating all components.
Manages threads for UI, Audio capture, STT, and Network communication.
"""

import logging
import threading
import time
import sys
import queue
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from core.config import (
    APP_NAME, VERSION, UI_CONFIG, AUDIO_CONFIG, VAD_CONFIG, STT_CONFIG,
    RELAY_CONFIG, LOG_CONFIG, request_permissions, get_relay_url
)
from audio.capture import AudioCapture
from audio.buffer import AudioBuffer
from audio.stt_engine import STTEngine
from network.relay_client import RelayClient
from ui.overlay import StealthOverlay

# Configure logging
logging.basicConfig(
    level=LOG_CONFIG["level"],
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_CONFIG["file"]),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class GHOSTClient:
    """Main GHOST client orchestrator."""

    def __init__(self):
        """Initialize GHOST client."""
        logger.info(f"Initializing {APP_NAME} v{VERSION}")
        
        self.is_running = False
        
        # Initialize components
        self.overlay = StealthOverlay(
            width=UI_CONFIG["window_width"],
            height=UI_CONFIG["window_height"],
        )
        
        self.audio_capture = AudioCapture(
            sample_rate=AUDIO_CONFIG["sample_rate"],
            chunk_size=AUDIO_CONFIG["chunk_size"]
        )
        
        self.audio_buffer = AudioBuffer(
            duration_seconds=AUDIO_CONFIG["buffer_duration"],
            sample_rate=AUDIO_CONFIG["sample_rate"]
        )
        
        self.stt_engine = STTEngine(
            engine=STT_CONFIG["engine"],
            model_size=STT_CONFIG["model_size"],
            language=STT_CONFIG["language"]
        )
        
        self.relay_client = RelayClient(
            host=RELAY_CONFIG["host"],
            port=RELAY_CONFIG["port"],
            protocol=RELAY_CONFIG["protocol"],
            timeout=RELAY_CONFIG["timeout"]
        )
        
        # Thread queues for communication
        self.audio_queue = queue.Queue()
        self.response_queue = queue.Queue()
        
        # Threads
        self.audio_thread = None
        self.processing_thread = None
        self.ui_thread = None

    def request_system_permissions(self):
        """Request microphone and system audio permissions."""
        logger.info("Requesting system permissions...")
        try:
            # Request permissions using the permission dialog
            permissions_granted = request_permissions()
            if permissions_granted:
                logger.info("Permissions granted")
                return True
            else:
                logger.warning("Permissions denied")
                return False
        except Exception as e:
            logger.error(f"Error requesting permissions: {e}")
            return False

    def start(self):
        """Start GHOST client."""
        if self.is_running:
            logger.warning("Client already running")
            return
        
        logger.info(f"Starting {APP_NAME}...")
        self.is_running = True
        
        try:
            # Request permissions first
            if not self.request_system_permissions():
                logger.error("Failed to obtain permissions")
                self.is_running = False
                return
            
            # Start audio capture
            self.audio_capture.start(callback=self._on_audio_chunk)
            
            # Start processing thread
            self.processing_thread = threading.Thread(
                target=self._processing_loop,
                daemon=True,
                name="ProcessingThread"
            )
            self.processing_thread.start()
            
            # Start UI thread
            self.ui_thread = threading.Thread(
                target=self._ui_loop,
                daemon=True,
                name="UIThread"
            )
            self.ui_thread.start()
            
            logger.info(f"{APP_NAME} started successfully")
            
        except Exception as e:
            logger.error(f"Error starting client: {e}")
            self.is_running = False

    def stop(self):
        """Stop GHOST client."""
        if not self.is_running:
            return
        
        logger.info("Stopping GHOST client...")
        self.is_running = False
        
        try:
            self.audio_capture.stop()
            self.overlay.close()
            logger.info("Client stopped")
        except Exception as e:
            logger.error(f"Error stopping client: {e}")

    def _on_audio_chunk(self, chunk):
        """Callback when audio chunk is received."""
        self.audio_buffer.add_chunk(chunk)
        self.audio_queue.put(chunk)

    def _processing_loop(self):
        """Main processing loop for STT and response generation."""
        logger.info("Processing thread started")
        
        while self.is_running:
            try:
                # Check if there's enough audio to process
                duration = self.audio_buffer.get_duration()
                
                if duration >= 2.0:  # Process every 2 seconds
                    audio_data = self.audio_buffer.get_audio()
                    
                    if len(audio_data) > 0:
                        # Transcribe audio
                        logger.debug("Transcribing audio...")
                        text = self.stt_engine.transcribe(audio_data)
                        
                        if text.strip():
                            logger.info(f"Transcribed: {text}")
                            
                            # Send to relay server for response generation
                            logger.debug("Requesting response from server...")
                            response = self.relay_client.generate_response(text)
                            
                            if response:
                                logger.info(f"Response: {response}")
                                self.response_queue.put(response)
                        
                        # Clear buffer after processing
                        self.audio_buffer.clear()
                
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error in processing loop: {e}")
                time.sleep(1)

    def _ui_loop(self):
        """Main UI loop."""
        logger.info("UI thread started")
        
        while self.is_running:
            try:
                # Get responses from queue
                try:
                    response = self.response_queue.get(timeout=0.5)
                    if response:
                        self.overlay.display_text(response)
                except queue.Empty:
                    pass
                
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error in UI loop: {e}")
                time.sleep(1)

    def run_forever(self):
        """Run the client indefinitely."""
        self.start()
        
        try:
            while self.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
            self.stop()


def main():
    """Main entry point."""
    try:
        client = GHOSTClient()
        client.run_forever()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
