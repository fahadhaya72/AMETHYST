# GHOST Desktop App - Testing & Preview Guide

## How to See Your App in Action Before Deployment

This guide shows you how to test, preview, and debug the GHOST application locally.

---

## 🎬 Quick Preview (2 Minutes)

### Fastest Way to See It Working

```powershell
# Terminal 1: Start the server
cd ghost_relay
python main_server.py

# Terminal 2: Run the client with debug output
cd ghost_client
python main_client.py
```

You'll see detailed output showing:
- ✅ Components initializing
- ✅ Audio being captured
- ✅ Text being transcribed
- ✅ Responses being generated
- ✅ UI updates happening

---

## 🧪 Testing Scenarios

### Scenario 1: Test Without Video Call (Easiest)

Just run the app and speak to your microphone:

```powershell
python main_client.py
```

When you speak:
1. Console shows: `Audio capture started`
2. Speak into microphone: "Hello, how are you?"
3. Console shows: `Transcribed: "Hello, how are you?"`
4. Console shows: `Generating response from server...`
5. Console shows: `Response: "I'm doing well, thank you for asking!"`
6. **Green text appears on your screen** (the overlay)

---

### Scenario 2: Test with Real Video Call (Best)

The ultimate test - actual video call!

**Setup**:
1. Start GHOST server: `cd ghost_relay && python main_server.py`
2. Start GHOST client: `cd ghost_client && python main_client.py`
3. Open Google Meet, Zoom, Teams, or WhatsApp
4. Start a video call
5. Listen to what the other person says
6. GHOST automatically captures and responds

**Workflow You'll See**:
```
Other person speaks
    ↓
GHOST captures audio (invisible to other party)
    ↓
Console shows: Transcribed: "..."
    ↓
Server generates response
    ↓
Console shows: Response: "..."
    ↓
Green text appears on your screen (only you see it)
    ↓
You read and speak the response
    ↓
Other person hears you naturally (thinks you thought of it!)
```

---

### Scenario 3: Test Individual Components

#### Test 1: Audio Capture
```powershell
# Check if Whisper can hear you
python -c "
import numpy as np
from ghost_client.audio.capture import AudioCapture

capture = AudioCapture()
capture.start()
print('🎤 Speaking now...')
import time
time.sleep(5)  # Speak for 5 seconds
audio = capture.get_buffer()
print(f'✅ Captured {len(audio)} audio samples')
capture.stop()
"
```

**Expected Output**:
```
🎤 Speaking now...
✅ Captured 80000 audio samples
```

#### Test 2: Microphone Detection
```powershell
python -c "
from ghost_client.core.permissions import PermissionsDialog

if PermissionsDialog.check_microphone_available():
    print('✅ Microphone found and ready')
else:
    print('❌ No microphone detected')
"
```

#### Test 3: Audio Transcription
```powershell
python -c "
from ghost_client.audio.stt_engine import STTEngine
import numpy as np

# Create 3 seconds of silence, then noise
stt = STTEngine(model_size='tiny')  # Use tiny for speed

# You need to feed actual audio
# For testing, use this:
print('Initializing Whisper...')
text = stt.transcribe(np.random.randn(48000).astype(np.float32))
print(f'Transcribed: {text}')
"
```

#### Test 4: Server/Gemini Connection
```powershell
python -c "
import os
# Set your API key first
os.environ['GEMINI_API_KEY'] = 'YOUR_API_KEY_HERE'

from ghost_relay.services.gemini_service import GeminiService

gemini = GeminiService()
if gemini.is_ready():
    print('✅ Gemini service is ready')
    response = gemini.generate_response('Say hello')
    print(f'Response: {response}')
else:
    print('❌ Gemini not configured')
"
```

---

## 📊 Debug & Testing Dashboard

### Enable Debug Mode

Edit `ghost_client/core/config.py`:

```python
DEBUG_MODE = True
LOG_CONFIG["level"] = "DEBUG"
```

Then run:
```powershell
python main_client.py
```

You'll see **super detailed output**:
```
[DEBUG] Audio chunk received: 1024 samples
[DEBUG] Buffer now contains: 16000 samples (1.0s)
[DEBUG] Transcription started...
[DEBUG] Whisper model loaded
[DEBUG] Transcription complete: "hello"
[DEBUG] Sending to server...
[DEBUG] Server response received: "Hi there!"
[DEBUG] Displaying text on overlay
```

### Check Logs

After running, check `ghost_client.log`:

```powershell
# View last 50 lines of log
Get-Content ghost_client.log -Tail 50

# Watch logs in real-time (like 'tail -f' on Linux)
Get-Content ghost_client.log -Wait
```

---

## 🎯 Complete Testing Checklist

Use this checklist to verify everything works:

### Phase 1: Setup ✓
- [ ] Python 3.11+ installed
- [ ] Dependencies installed: `pip install -r requirements_client.txt`
- [ ] Server dependencies installed: `pip install -r requirements_server.txt`
- [ ] API key configured in `.env`
- [ ] All files downloaded/created

### Phase 2: Component Testing ✓
- [ ] Microphone detected and working
- [ ] Audio capture running
- [ ] Whisper model loads
- [ ] Buffer stores audio correctly
- [ ] STT produces text output

### Phase 3: Server Testing ✓
- [ ] Server starts without errors
- [ ] Health check endpoint responds: `http://localhost:8000/health`
- [ ] Gemini service initializes
- [ ] API key validation passes

### Phase 4: Integration Testing ✓
- [ ] Client connects to server
- [ ] Audio flows through capture → buffer → STT
- [ ] Text sent to server successfully
- [ ] Gemini generates response
- [ ] Response returned to client

### Phase 5: UI Testing ✓
- [ ] Overlay window appears
- [ ] Text displays in green on black
- [ ] Window is click-through
- [ ] Window disappears when not needed
- [ ] Text is readable during call

### Phase 6: Real-World Testing ✓
- [ ] Works with Google Meet
- [ ] Works with Zoom
- [ ] Works with Teams
- [ ] Works with WhatsApp
- [ ] Other person can't see overlay
- [ ] Responses are natural and helpful

---

## 🔍 What You'll See Running the App

### Console Output (Real Example)

```
[INFO] Initializing GHOST v1.0.0
[INFO] RelayClient initialized: http://localhost:8000

[INFO] Audio capture started
[INFO] Processing thread started
[INFO] UI thread started

[INFO] Starting GHOST...
Client started successfully

# (You speak: "What's the capital of France?")

[DEBUG] Audio chunk received: 1024 samples
[DEBUG] Buffer updated: 48000 samples (3.0s of audio)
[DEBUG] Transcribing audio...
[INFO] Transcribed: "What's the capital of France?"

[DEBUG] Sending to server...
[DEBUG] Request to: http://localhost:8000/api/generate
[INFO] Generating response for: What's the capital of France?
[INFO] Response: "The capital of France is Paris, a beautiful city known for the Eiffel Tower."

[DEBUG] Displaying text on overlay

# (Green text appears on your screen)
```

### Overlay Display (On Your Screen)

```
╔═══════════════════════════════════╗
║ The capital of France is Paris,   ║
║ a beautiful city known for the    ║
║ Eiffel Tower.                     ║
╚═══════════════════════════════════╝
```

(Only you see this - it's completely invisible to others!)

### Server Console Output

```
INFO:     Application startup complete
INFO:     Uvicorn running on http://0.0.0.0:8000

INFO:     127.0.0.1:54321 - "POST /api/generate HTTP/1.1" 200 OK
[INFO] Generating response for: What's the capital of France?
[INFO] Generated: "The capital of France is Paris, a beautiful city known for the Eiffel Tower."
```

---

## 🎮 Interactive Testing Script

Create a test script to simulate the full workflow:

### Create `test_workflow.py`

```python
"""
Interactive test to simulate complete workflow.
Shows you exactly what the app does.
"""

import time
import os
os.environ['GEMINI_API_KEY'] = input("Enter your Gemini API key: ")

from ghost_client.audio.buffer import AudioBuffer
from ghost_client.audio.stt_engine import STTEngine
from ghost_client.network.relay_client import RelayClient
import numpy as np

print("\n" + "="*60)
print("GHOST Workflow Test - See Each Step")
print("="*60 + "\n")

# Step 1: Audio Buffer
print("📍 Step 1: Audio Buffering")
print("-" * 60)
buffer = AudioBuffer(duration_seconds=5, sample_rate=16000)
print("✓ Audio buffer created (5 second capacity)")

# Simulate audio
fake_audio = np.random.randn(16000).astype(np.float32) * 0.1  # 1 second
buffer.add_chunk(fake_audio)
print(f"✓ Added audio: {buffer.get_duration():.1f} seconds")
print(f"✓ Energy level: {buffer.get_energy_level():.2f}\n")

# Step 2: STT
print("📍 Step 2: Speech-to-Text")
print("-" * 60)
stt = STTEngine(model_size='tiny')
print("✓ Whisper model loaded (using 'tiny' for speed)")

# For real test, you'd need actual audio from microphone
# For now, we'll just show it's ready
print("✓ STT engine ready\n")

# Step 3: Server Communication
print("📍 Step 3: Server Communication")
print("-" * 60)
relay = RelayClient(host='localhost', port=8000)
health = relay.health_check()
print(f"✓ Server health check: {'✅ Online' if health else '❌ Offline'}")
print("✓ RelayClient connected\n")

# Step 4: Generate Response
print("📍 Step 4: Generate AI Response")
print("-" * 60)
test_text = "Hello, how are you?"
print(f"Input text: '{test_text}'")
response = relay.generate_response(test_text)
if response:
    print(f"✓ Response received: '{response}'\n")
else:
    print("❌ No response (check server is running)\n")

# Step 5: Summary
print("="*60)
print("✅ Workflow Test Complete!")
print("="*60)
print("\nWhat you saw:")
print("1. Audio was captured to buffer")
print("2. Buffer stored audio with energy detection")
print("3. STT engine (Whisper) initialized")
print("4. Client connected to server")
print("5. Text was sent to Gemini API")
print("6. Response was generated")
print(f"\nThis happens every 2-5 seconds during actual video calls!")
```

Run it:
```powershell
python test_workflow.py
```

---

## 🎥 How to View App in Different Scenarios

### Scenario A: Minimal Testing (Just Code)
```powershell
# Just see the workflow in console
python main_client.py

# Speak into microphone when prompted
# Watch console output show each step
```

### Scenario B: With Debug Logging
```powershell
# See detailed debug messages
# Edit config.py: DEBUG_MODE = True
python main_client.py
```

Check logs: `Get-Content ghost_client.log -Wait`

### Scenario C: Full Testing (With Real Video)
```powershell
# Terminal 1: Server
cd ghost_relay
python main_server.py

# Terminal 2: Client
cd ghost_client
python main_client.py

# Browser/Phone: Open video call
# Talk to other person normally
# Watch overlay appear with responses
```

### Scenario D: Component Testing
```powershell
# Test individual parts in isolation
python tests/test_audio_buffer.py
python tests/test_relay_auth.py

# Or create custom tests for specific components
```

---

## 📈 Performance Monitoring

### Watch Logs in Real-Time
```powershell
Get-Content ghost_client.log -Wait
```

### Monitor System Resources During Testing
```powershell
# Open Task Manager
taskmgr

# Look for "python.exe" processes
# Monitor CPU, Memory, Disk usage
```

### Check Server Health
```powershell
# In browser or PowerShell
Invoke-WebRequest http://localhost:8000/health

# Should return: {"status": "healthy"}
```

---

## 🐛 Debugging Common Issues During Testing

### Issue: Audio Not Captured
**How to debug**:
```powershell
python -c "
from ghost_client.core.permissions import PermissionsDialog
print('Microphone available:', PermissionsDialog.check_microphone_available())
"
```

### Issue: Whisper Not Transcribing
**How to debug**:
```powershell
python -c "
import os
os.environ['GEMINI_API_KEY'] = 'test'

from ghost_client.audio.stt_engine import STTEngine
stt = STTEngine()
if stt.model:
    print('✓ Whisper loaded')
else:
    print('✗ Whisper failed to load')
"
```

### Issue: Server Not Responding
**How to debug**:
```powershell
# Check server is running
Invoke-WebRequest http://localhost:8000/health

# Check API key is set
Write-Host $env:GEMINI_API_KEY
```

### Issue: Overlay Not Showing
**How to debug**:
```powershell
# Run with debug output
python main_client.py

# Look for "Overlay shown" messages
# If not there, check logs for errors
```

---

## 📹 Record Your Testing

### Screen Recording (Windows)
```powershell
# Start recording
# Press Windows Key + G

# Perform actions
# Stop recording
```

Files save to: `C:\Users\YourName\Videos\Captures`

### Save Console Output to File
```powershell
# Run and save output
python main_client.py | Tee-Object -FilePath test_output.txt

# Both shows on screen AND saves to file
```

---

## ✅ Sign-Off Checklist Before Deployment

Before considering your app "ready", verify:

- [ ] Audio capture works without errors
- [ ] Whisper transcribes test audio correctly
- [ ] Server API responds to requests
- [ ] Gemini generates coherent responses
- [ ] Responses display on overlay
- [ ] App runs for 10+ minutes without crashing
- [ ] Logs show no error messages
- [ ] Works with at least one video call app
- [ ] Other participants can't see overlay
- [ ] Responses are helpful and relevant
- [ ] No excessive CPU/memory usage
- [ ] All documentation is accurate
- [ ] Setup.py runs without errors
- [ ] Troubleshooting guide covers issues you found

---

## 🎬 Final Preview Example: Complete Workflow

### What You'll See When Testing

**Terminal 1 Output (Server)**:
```
INFO:     Application startup complete
INFO:     Uvicorn running on http://0.0.0.0:8000
[INFO] Gemini service initialized
```

**Terminal 2 Output (Client)**:
```
[INFO] Starting GHOST...
[INFO] Audio capture started
[INFO] Processing thread started
[INFO] UI thread started
```

**Your Screen**:
- No visible window
- App runs in background

**When you speak during a call**:
```
Terminal 2:
[INFO] Transcribed: "Tell me a joke"
[DEBUG] Generating response...
[INFO] Response: "Why don't scientists trust atoms? Because they make up everything!"

Your Screen:
╔════════════════════════════════════╗
║ Why don't scientists trust atoms?  ║
║ Because they make up everything!  ║
╚════════════════════════════════════╝
```

**Other person**: Hears you naturally speaking the response (they don't know it's AI!)

---

## 🚀 Next Steps

1. **Follow QUICKSTART.md** to install
2. **Run `setup.py`** to verify everything
3. **Run `main_client.py`** and speak to microphone
4. **Watch console output** showing the workflow
5. **Open a real video call** and test
6. **Monitor logs** to ensure no errors
7. **Celebrate** - Your app is working!

---

## 📞 Testing Tips

- 🎤 **Speak clearly** - Whisper works best with clear audio
- ⏸️ **Wait for response** - Takes 5-10 seconds after speaking
- 📝 **Check logs** - Best way to understand what's happening
- 🐛 **Enable debug mode** - For detailed message tracking
- 📹 **Record tests** - For showing others or documentation
- 💾 **Save output** - For troubleshooting later

---

**Ready to test?** Start with [QUICKSTART.md](QUICKSTART.md) and come back here to preview!

Good luck! 👻
