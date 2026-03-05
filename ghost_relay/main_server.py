"""
GHOST Relay Server - Main Entry Point.
Starts the FastAPI backend server with Gemini integration.
"""

import uvicorn
import logging
import os
from pathlib import Path
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import API routes
from api.routes import app


def main():
    """Start the GHOST relay server."""
    
    # Load environment variables from .env file
    try:
        from dotenv import load_dotenv
        env_file = Path(__file__).parent / ".env"
        if env_file.exists():
            load_dotenv(env_file)
            logger.info(f"Loaded environment from {env_file}")
        else:
            logger.warning(f".env file not found at {env_file}")
    except ImportError:
        logger.warning("python-dotenv not installed")
    
    # Verify required environment variables
    if not os.getenv("GEMINI_API_KEY"):
        logger.error("GEMINI_API_KEY environment variable not set!")
        logger.error("Please set GEMINI_API_KEY in .env file or environment")
        sys.exit(1)
    
    logger.info("Starting GHOST Relay Server...")
    logger.info(f"API Key loaded: {os.getenv('GEMINI_API_KEY')[:10]}...")
    
    # Get host and port from environment or use defaults
    host = os.getenv("RELAY_HOST", "0.0.0.0")
    port = int(os.getenv("RELAY_PORT", "8000"))
    
    logger.info(f"Server will listen on {host}:{port}")
    
    # Start the server
    try:
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info",
            access_log=True,
            reload=False,  # Set to True for development
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
