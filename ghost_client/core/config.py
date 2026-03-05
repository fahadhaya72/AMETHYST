"""
Local client configuration and settings for GHOST application.
Includes UI colors, VAD thresholds, audio parameters, and relay server settings.
"""

import os
from pathlib import Path

# ============ APPLICATION SETTINGS ============
APP_NAME = "GHOST"
VERSION = "1.0.0"
DEBUG_MODE = False

# ============ UI SETTINGS ============
UI_CONFIG = {
    "overlay_opacity": 0.9,  # Window transparency (0-1)
    "text_color": "#00FF00",  # Neon green for stealth feel
    "background_color": "#000000",  # Black background
    "font_size": 12,
    "font_family": "Courier New",
    "window_width": 600,
    "window_height": 400,
    "position_x": 100,
    "position_y": 100,
}

# ============ AUDIO SETTINGS ============
AUDIO_CONFIG = {
    "sample_rate": 16000,  # Hz (Whisper standard)
    "chunk_size": 1024,  # Samples per chunk
    "channels": 1,  # Mono
    "format": "float32",  # PyAudio format
    "buffer_duration": 30,  # seconds - rolling buffer
    "device_index": None,  # Auto-detect loopback device
}

# ============ VAD (VOICE ACTIVITY DETECTION) SETTINGS ============
VAD_CONFIG = {
    "enabled": True,
    "threshold": 0.5,  # Energy threshold (0-1)
    "min_duration": 0.5,  # Minimum speech duration (seconds)
    "silence_duration": 1.0,  # Silence before considering speech ended (seconds)
}

# ============ STT (SPEECH-TO-TEXT) SETTINGS ============
STT_CONFIG = {
    "engine": "whisper",  # Options: "whisper", "azure", "google"
    "model_size": "base",  # Whisper model: tiny, base, small, medium, large
    "language": "en",
    "temperature": 0.0,  # For consistent transcription
}

# ============ RELAY SERVER SETTINGS ============
RELAY_CONFIG = {
    "host": "localhost",  # Change to your server IP/domain in production
    "port": 8000,
    "protocol": "http",  # Change to https in production
    "endpoint_transcribe": "/api/transcribe",
    "endpoint_generate": "/api/generate",
    "timeout": 30,  # seconds
    "retry_attempts": 3,
    "retry_delay": 2,  # seconds
}

# ============ SECURITY & PERMISSIONS ============
PERMISSIONS = {
    "microphone": False,
    "system_audio_capture": False,
    "overlay_access": False,
}

# ============ LOGGING ============
LOG_CONFIG = {
    "level": "DEBUG" if DEBUG_MODE else "INFO",
    "file": "ghost_client.log",
    "max_size": 10 * 1024 * 1024,  # 10MB
    "backup_count": 5,
}

# ============ PATHS ============
BASE_DIR = Path(__file__).parent.parent.parent
LOGS_DIR = BASE_DIR / "logs"
CACHE_DIR = BASE_DIR / ".cache"

# Create necessary directories
LOGS_DIR.mkdir(exist_ok=True)
CACHE_DIR.mkdir(exist_ok=True)


def get_relay_url(endpoint: str) -> str:
    """Construct full relay server URL."""
    protocol = RELAY_CONFIG["protocol"]
    host = RELAY_CONFIG["host"]
    port = RELAY_CONFIG["port"]
    return f"{protocol}://{host}:{port}{endpoint}"


def request_permissions() -> bool:
    """
    Request system permissions from user.
    Shows a custom dialog asking for microphone and audio permissions.
    
    Returns:
        True if user grants permissions, False otherwise
    """
    try:
        from .permissions import PermissionsDialog
        dialog = PermissionsDialog()
        # Check if microphone is available first
        if PermissionsDialog.check_microphone_available():
            return dialog.request_permissions()
        else:
            return False
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Error requesting permissions: {e}")
        return False
