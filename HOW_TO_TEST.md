# GHOST - Start Here: How to See Your App Working

## Like Testing a Website Before Deployment ✅

**Your Question**: How can I see how the desktop app looks and works (like previewing a website)?

**Answer**: You can test it locally just like a website! Here's how:

---

## 🚀 5-Minute Quick View

### Step 1: Open 2 PowerShell Windows
```powershell
# Window 1: Start Backend Server
cd c:\Users\Fahad\OneDrive\Desktop\AIMEET\ghost_relay
python main_server.py

# Window 2: Start Frontend App  
cd c:\Users\Fahad\OneDrive\Desktop\AIMEET\ghost_client
python main_client.py
```

### Step 2: What You'll See

**Window 1 Console** (Server):
```
INFO:     Application startup complete
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Window 2 Console** (Client):
```
[INFO] Audio capture started
[INFO] GHOST started successfully
```

### Step 3: You're Ready to Test!
- **Speak into your microphone**: Say "Hello"
- **Watch console show**: 
  ```
  [INFO] Transcribed: "Hello"
  [INFO] Response: "Hi there! How can I help?"
  ```
- **See on your screen**: Green text overlay appears

**That's it!** You've now seen the app working.

---

## 📚 Documentation for Different Testing Levels

| Level | What You Want | Documentation |
|-------|---------------|----------------|
| **🟢 Beginner** | See the app working right now | **← You're reading it!** |
| **🟡 Intermediate** | Understand the workflow and test different scenarios | [TESTING_PREVIEW.md](TESTING_PREVIEW.md) |
| **🔴 Advanced** | See real console output, trace every step | [VISUAL_DEMO.md](VISUAL_DEMO.md) |

---

## 🎬 The Three Ways to Test

### Way 1: Console Output Test (Easiest)
```
What you see: Text messages in PowerShell showing what's happening
Best for: Understanding the workflow
Time: 2 minutes
```

**Try this:**
```powershell
cd ghost_client
python main_client.py
# Speak into mic
# Watch console show: Transcribed: "..." → Response: "..."
```

### Way 2: Real Video Call Test (Best)
```
What you see: Green text appears on your screen during actual video call
Best for: Real-world testing
Time: 5-10 minutes
```

**Try this:**
```powershell
# Start server and client (from Way 1)
# Open Google Meet/Zoom/Teams
# Talk with someone
# Green responses appear on YOUR screen ONLY!
```

### Way 3: Component Testing (Technical)
```
What you see: Individual parts being tested in isolation
Best for: Debugging specific issues
Time: 5 minutes
```

**Try this:**
```powershell
# Test just the audio buffer
python tests/test_audio_buffer.py

# Test just the Gemini connection
python tests/test_relay_auth.py
```

---

## 👀 What You'll Actually See

### On Your Screen (Completely Normal)
```
Google Meet / Zoom / Teams / WhatsApp
├─ Video call running normally
├─ You see other person
├─ Chat visible
└─ NO VISIBLE APP (this is intentional!)
```

### On Your Screen After You Speak
```
Google Meet / Zoom / Teams
├─ Video call continues normally
├─ Then SUDDENLY →

    ╔════════════════════════════════════╗
    ║ I would approach this by first...  ║
    ║ analyzing the requirements...      ║
    ╚════════════════════════════════════╝

    (Green text, only you see it)
```

### In PowerShell Console
```
[INFO] Transcribed: "What do you think?"
[INFO] Response: "I would approach this by..."
[DEBUG] Displaying on overlay
```

---

## ✅ Complete Testing Workflow

```
START HERE
    ↓
[Step 1] Run: python setup.py
    ↓
[Step 2] Run: cd ghost_relay & python main_server.py (Terminal 1)
    ↓
[Step 3] Run: cd ghost_client & python main_client.py (Terminal 2)
    ↓
[Step 4] Speak into microphone OR
         Open video call and talk
    ↓
[Step 5] See console output showing:
         - Transcribed: [your words]
         - Response: [AI answer]
    ↓
[Step 6] See green overlay on screen ✓
    ↓
SUCCESS! App is working!
```

---

## 🎯 Different Testing Scenarios

### Scenario A: Desktop Intercom (No Video Call)
```
You: "Hello"
Console: [INFO] Transcribed: "Hello"
Screen: [Green text] "Hello! How can I help?"
Time: 10 seconds
Perfect for: Quick testing
```

### Scenario B: Real Video Call
```
Other person: "What time is the meeting?"
You: (GHOST captures this)
Console: [INFO] Transcribed: "What time is the meeting?"
Screen: [Green overlay] "The meeting is at 2 PM"
You: Speak the response naturally
Other person: Thinks you're smart!
Time: 10-15 seconds
Perfect for: Real-world use
```

### Scenario C: Technical Deep-Dive
```
python main_client.py
# But also check logs:
Get-Content ghost_client.log -Wait

# And check server:
Invoke-WebRequest http://localhost:8000/health

# And test Gemini:
python -c "
from ghost_relay.services.gemini_service import GeminiService
g = GeminiService()
print(g.generate_response('test'))
"
```

---

## 📊 Console Output Examples

You'll see messages like this:

```
✅ INITIALIZATION
[INFO] Initializing GHOST v1.0.0
[INFO] Audio capture initialized
[INFO] Whisper model loaded
[INFO] Server connection established

✅ LISTENING
[DEBUG] Audio chunk received: 1024 samples
[DEBUG] Buffer updated to: 48000 samples

✅ PROCESSING
[INFO] Transcribed: "Hello world"
[DEBUG] Sending to server...

✅ RESPONSE
[INFO] Response: "Hello! Nice talking to you!"
[DEBUG] Displaying on overlay

✅ COMPLETE
[Your screen shows the green text]
```

---

## 🔍 How to Know It's Working

### Signs of Success ✅

- [x] Console shows no ERROR messages
- [x] "Application startup complete" appears
- [x] "GHOST started successfully" appears
- [x] You speak and see "Transcribed: ..." in console
- [x] You see "Response: ..." in console
- [x] Green text appears on screen
- [x] No error dialogs appear

### Signs of Problems ❌

- [ ] "ModuleNotFoundError" - Missing dependencies
- [ ] "Connection refused" - Server not running
- [ ] "GEMINI_API_KEY not found" - API key not set
- [ ] "No loopback device" - Enable Stereo Mix
- [ ] Overlay doesn't appear - Check logs

**Solution**: See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## 🎮 Try These Test Commands Now

```powershell
# Check Python installed
python --version

# Navigate to project
cd "c:\Users\Fahad\OneDrive\Desktop\AIMEET"

# Install dependencies
python -m pip install -r requirements_client.txt
python -m pip install -r requirements_server.txt

# Start server (in one PowerShell)
cd ghost_relay
python main_server.py

# Start client (in another PowerShell)
cd ghost_client
python main_client.py

# Watch it work!
# Speak → Console shows what happened → Green text appears
```

---

## 📖 Read Next

After this, read:

1. **Want to understand testing better?** → [TESTING_PREVIEW.md](TESTING_PREVIEW.md)
2. **Want to see real console output?** → [VISUAL_DEMO.md](VISUAL_DEMO.md)
3. **Want full setup guide?** → [QUICKSTART.md](QUICKSTART.md)
4. **Want to fix problems?** → [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
5. **Want technical details?** → [ARCHITECTURE.md](docs/ARCHITECTURE.md)

---

## 🎬 Summary: How It Works

```
Like a website preview:
┌──────────────────────────────────────────┐
│ WEBSITE: Run localhost:3000              │
│ See: Browser shows website               │
│ Test: Click buttons, fill forms, etc.    │
└──────────────────────────────────────────┘

                    SAME CONCEPT
                    
┌──────────────────────────────────────────┐
│ GHOST: Run 2 terminals                   │
│ See: Console output + overlay on screen  │
│ Test: Speak words, see responses         │
└──────────────────────────────────────────┘
```

---

## ✨ That's It!

You now understand how to **see and test** your GHOST desktop app before deployment!

- 🟢 **Level 1**: Run it and speak (2 min) ← Do this now!
- 🟡 **Level 2**: Test with video call (10 min)
- 🔴 **Level 3**: Debug individual components (advanced)

---

## 🚀 Ready? Let's Go!

```powershell
# Open PowerShell and try this RIGHT NOW:

cd c:\Users\Fahad\OneDrive\Desktop\AIMEET\ghost_relay
python main_server.py

# (In another PowerShell window)
cd c:\Users\Fahad\OneDrive\Desktop\AIMEET\ghost_client
python main_client.py

# Then speak into your microphone and watch the magic! ✨
```

**Questions?** See [TESTING_PREVIEW.md](TESTING_PREVIEW.md) for more details!

---

Happy testing! 👻

