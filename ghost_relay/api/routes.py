"""
API Routes for GHOST Relay Server.
Handles text-to-response conversion using Gemini 3 Flash API.
"""

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
import logging
from datetime import datetime
import os

from ..services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

# Initialize Gemini service
gemini_service = GeminiService()

# Create FastAPI app
app = FastAPI(
    title="GHOST Relay Server",
    description="Secure relay for AI-powered call assistance",
    version="1.0.0"
)


async def verify_api_key(request: Request) -> str:
    """Verify API key from request."""
    # Get API key from request body or headers
    try:
        body = await request.json()
        api_key = body.get("api_key")
    except:
        api_key = request.headers.get("X-API-Key")
    
    if not api_key:
        raise HTTPException(status_code=401, detail="Missing API key")
    
    # For now, accept any API key (implement proper validation later)
    return api_key


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.post("/api/generate")
async def generate_response(request: Request):
    """
    Generate AI response for given text.
    
    Request JSON:
    {
        "text": "User provided text",
        "api_key": "optional_api_key"
    }
    
    Response JSON:
    {
        "response": "AI generated response",
        "timestamp": "ISO timestamp",
        "tokens_used": 123
    }
    """
    try:
        # Parse request
        try:
            body = await request.json()
        except:
            raise HTTPException(status_code=400, detail="Invalid JSON")
        
        text = body.get("text", "").strip()
        
        if not text:
            raise HTTPException(status_code=400, detail="Empty text provided")
        
        logger.info(f"Generating response for: {text[:100]}...")
        
        # Generate response using Gemini
        response_text = gemini_service.generate_response(text)
        
        if not response_text:
            raise HTTPException(status_code=500, detail="Failed to generate response")
        
        return {
            "response": response_text,
            "timestamp": datetime.utcnow().isoformat(),
            "tokens_used": 0,  # Could implement token counting
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/transcribe")
async def transcribe_audio(request: Request):
    """
    Transcribe audio using cloud STT service.
    This is for optional cloud-based transcription.
    
    Request: multipart form data with audio file
    Response: {"text": "transcribed text"}
    """
    try:
        logger.info("Transcribe endpoint called")
        # TODO: Implement audio transcription
        return {"text": "", "status": "not_implemented"}
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        raise HTTPException(status_code=500, detail="Transcription failed")


@app.post("/api/logs")
async def send_logs(request: Request):
    """
    Receive debug logs from client for analytics.
    """
    try:
        body = await request.json()
        logger.debug(f"Client log: {body}")
        return {"status": "logged"}
    except Exception as e:
        logger.error(f"Error processing logs: {e}")
        return {"status": "error"}


@app.get("/api/status")
async def get_status():
    """Get server status and statistics."""
    return {
        "status": "online",
        "gemini_ready": gemini_service.is_ready(),
        "timestamp": datetime.utcnow().isoformat()
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
