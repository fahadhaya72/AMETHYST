"""
GHOST Project Architecture and Implementation Guide
"""

# GHOST: Real-Time AI-Powered Call Assistant

## Overview
GHOST is a Windows desktop application that captures audio during video calls (Google Meet, Zoom, WhatsApp) and uses Google's Gemini 3 Flash API to generate real-time responses that are displayed to the user but invisible to other call participants.

## Architecture

### Phase 1: Stealth Overlay UI
- **Component**: `ghost_client/ui/overlay.py`
- **Features**:
  - Transparent, click-through tkinter window
  - Neon green text on black background (stealth aesthetic)
  - Automatically shows/hides when responses are generated
  - Always on top, never focused to avoid detection
  - Positioned at top-right corner of screen

### Phase 2: Audio Capture
- **Component**: `ghost_client/audio/capture.py`
- **Features**:
  - WASAPI loopback device detection on Windows
  - Captures system audio from video calls
  - Real-time audio streaming
  - Automatic device fallback

### Phase 3: Speech-to-Text Processing
- **Component**: `ghost_client/audio/stt_engine.py`
- **Features**:
  - OpenAI Whisper for local STT (no API calls)
  - Support for multiple languages
  - Real-time transcription
  - Fallback options for other STT providers

### Phase 4: Network Communication
- **Component**: `ghost_client/network/relay_client.py`
- **Features**:
  - HTTP/WebSocket communication with relay server
  - Sends transcribed text to backend
  - Receives AI-generated responses
  - Handles failures gracefully

### Phase 5: Response Generation
- **Server**: `ghost_relay/main_server.py`
- **Service**: `ghost_relay/services/gemini_service.py`
- **Features**:
  - FastAPI backend
  - Google Gemini 3 Flash integration
  - Secure API key storage in `.env` file
  - Response caching for common phrases

## Setup Instructions

### 1. Install Dependencies

```bash
# Client setup
pip install -r requirements_client.txt

# Server setup
pip install -r requirements_server.txt
```

### 2. Configure Environment

1. Create/edit `ghost_relay/.env`:
   ```
   GEMINI_API_KEY=your_api_key_here
   RELAY_HOST=0.0.0.0
   RELAY_PORT=8000
   ```

2. Get your Gemini API key from: https://ai.google.dev/

### 3. Enable Stereo Mix (Windows)

1. Right-click speaker icon → Sound settings
2. Advanced → Volume mixer
3. App volume and device preferences
4. Find and enable "Stereo Mix" or "WASAPI Loopback"

### 4. Run the Application

**Terminal 1 - Start server:**
```bash
cd ghost_relay
python main_server.py
```

**Terminal 2 - Start client:**
```bash
cd ghost_client
python main_client.py
```

## File Structure

```
AIMEET/
├── ghost_client/
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py           # Configuration and settings
│   ├── audio/
│   │   ├── __init__.py
│   │   ├── capture.py          # WASAPI audio capture
│   │   ├── buffer.py           # Rolling audio buffer
│   │   └── stt_engine.py       # Whisper STT
│   ├── network/
│   │   ├── __init__.py
│   │   └── relay_client.py     # Server communication
│   ├── ui/
│   │   ├── __init__.py
│   │   └── overlay.py          # Transparent overlay UI
│   └── main_client.py          # Entry point
├── ghost_relay/
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py           # API endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   └── gemini_service.py   # Gemini integration
│   ├── main_server.py          # Server entry point
│   └── .env                    # API keys (NEVER commit!)
├── tests/
│   ├── test_audio_buffer.py
│   └── test_relay_auth.py
├── requirements_client.txt     # Client dependencies
├── requirements_server.txt     # Server dependencies
└── .gitignore                  # Git ignore rules
```

## Key Technologies

- **Python 3.11+**
- **FastAPI** - Web framework
- **tkinter** - GUI (built-in)
- **PyAudio** - Audio capture
- **Whisper** - Speech-to-Text
- **Google Generative AI** - Gemini 3 Flash
- **Uvicorn** - ASGI server

## Security Considerations

1. **API Key Management**:
   - Store Gemini API key in `.env` file
   - Never commit `.env` to version control
   - Use environment variables in production

2. **Network Security**:
   - Use HTTPS in production
   - Implement rate limiting on server
   - Add authentication tokens if needed

3. **Audio Privacy**:
   - Audio is captured locally, not stored
   - Only text (transcription) is sent to server
   - Server processes and doesn't retain conversations

## Future Enhancements

1. **Multi-language Support**: Support for 50+ languages
2. **Context Memory**: Remember conversation history for better responses
3. **Custom Prompts**: User-configurable AI system prompts
4. **Advanced VAD**: Silence detection to avoid processing noise
5. **Response Templates**: Quick-access canned responses
6. **Analytics Dashboard**: Server-side call statistics
7. **Mobile Version**: iOS/Android companion app

## Troubleshooting

**Issue**: "Stereo Mix" device not found
- Solution: Enable in Windows Sound settings, update audio drivers

**Issue**: "GEMINI_API_KEY not found"
- Solution: Create `.env` file with your API key

**Issue**: Audio transcription slow
- Solution: Use Whisper "tiny" model, or switch to cloud STT

**Issue**: Server connection timeout
- Solution: Check firewall, ensure relay server is running

## License
Private Open Source - Use Responsibly

## Support
For issues, check logs in `ghost_client.log` and server console output.
