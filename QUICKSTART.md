# GHOST Project - Quick Start Guide

## 🚀 Quick Start (5 minutes)

### Step 1: Install Python (if not already installed)
- Download Python 3.11+ from https://www.python.org/downloads/
- **Important**: Check "Add Python to PATH" during installation

### Step 2: Get Google Gemini API Key
1. Go to https://ai.google.dev/
2. Click "Get API Key"
3. Create a new API key or use existing
4. Copy the API key

### Step 3: Set Up Environment
Open PowerShell/Command Prompt in the AIMEET folder:

```powershell
# Install dependencies
pip install -r requirements_client.txt
pip install -r requirements_server.txt

# Create .env file for server
# Edit ghost_relay/.env and replace with your API key:
# GEMINI_API_KEY=paste_your_key_here
```

### Step 4: Enable Stereo Mix on Windows
1. Right-click the **speaker icon** in system tray
2. Select **"Sound settings"** or **"Open Sound settings"**
3. Scroll down, click **"Volume mixer"** or **"App volume and device preferences"**
4. Look for **"Stereo Mix"** in the list
   - If not found: Right-click any disabled device → Enable it
5. Restart the application

### Step 5: Run the Application

**Terminal 1 - Start the backend server:**
```powershell
cd ghost_relay
python main_server.py
```
You should see: `Application startup complete`

**Terminal 2 - Start the application:**
```powershell
cd ghost_client
python main_client.py
```

### Step 6: Test It
1. Open a video call (Google Meet, Zoom, Teams)
2. Say something to the other person
3. GHOST will transcribe and generate a response
4. A green text overlay should appear on your screen
5. Press `Ctrl+C` in either terminal to stop

---

## 🔧 Configuration

Edit `ghost_client/core/config.py` to customize:

```python
UI_CONFIG = {
    "overlay_opacity": 0.9,          # 0-1 (more transparent = lower)
    "text_color": "#00FF00",         # Neon green
    "font_size": 12,                 # Text size in pixels
    "window_width": 600,             # Width in pixels
    "window_height": 400,            # Height in pixels
}

AUDIO_CONFIG = {
    "sample_rate": 16000,            # Hz
    "buffer_duration": 30,           # seconds
}

STT_CONFIG = {
    "model_size": "base",            # tiny, base, small, medium, large
                                      # (smaller = faster, larger = more accurate)
}
```

---

## 🎯 How It Works

```
Video Call
    ↓
[WASAPI Audio Loopback] ← Captures system audio
    ↓
[Whisper STT] ← Transcribes to text (local)
    ↓
[Relay Server] → Sends to Gemini API
    ↓
[Gemini 3 Flash] ← Generates response
    ↓
[Server Response] → Sends back to client
    ↓
[Overlay Display] ← Shows response on screen
```

---

## ❓ Troubleshooting

### Problem: "pyaudio not found"
```powershell
pip install pyaudio
```

### Problem: "Stereo Mix device not found"
1. Update your audio driver
2. Check if "What U Hear" device exists instead
3. Some audio devices don't support loopback

### Problem: "GEMINI_API_KEY not found"
1. Check `.env` file exists in `ghost_relay/` folder
2. Verify API key is correctly pasted (no spaces before/after)
3. Restart server after editing `.env`

### Problem: Server won't start
```powershell
pip install fastapi uvicorn google-generativeai
```

### Problem: Transcription taking too long
- Change `model_size` from "base" to "tiny" in config.py (faster, less accurate)
- Or from "base" to "medium" (slower, more accurate)

---

## 📝 Example Dialog Flow

**Video Call Situation:**
```
Other person: "What's your email address?"

GHOST transcribes: "What's your email address?"

GHOST Gemini generates: "I'll send you my email after the call."

Your screen shows:
┌────────────────────────────┐
│ I'll send you my email     │
│ after the call.            │
└────────────────────────────┘

You can read and say this while other person doesn't see it!
```

---

## 🔐 Security Notes

- ✅ Your API key is stored locally in `.env` (never uploaded)
- ✅ Audio is only transcribed to text - not stored
- ✅ Text is sent to Gemini, processed, then forgotten
- ✅ Server doesn't log conversations
- ❌ Don't commit `.env` file to Git/GitHub

---

## 📚 Further Reading

- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - Detailed technical overview
- [Google Generative AI Docs](https://ai.google.dev/docs)
- [Whisper STT Documentation](https://github.com/openai/whisper)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

## 💪 Next Steps

After getting basic setup working:

1. **Customize Prompts** - Edit `gemini_service.py` system message
2. **Add Quick Responses** - Create custom response templates
3. **Improve Accuracy** - Increase STT model size for better transcription
4. **Deploy Server** - Host on cloud (AWS, Google Cloud, Azure)
5. **Add Logging** - Record statistics about your usage

---

**Need Help?**
Check `ghost_client.log` file in the AIMEET folder for detailed error logs.

Good luck with GHOST! 👻
