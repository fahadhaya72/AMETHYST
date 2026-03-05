# GHOST Troubleshooting Guide

## General Issues

### Issue: "ModuleNotFoundError: No module named 'X'"
**Cause**: Missing Python dependencies

**Solution**:
```powershell
pip install -r requirements_client.txt
pip install -r requirements_server.txt
```

---

### Issue: "Python not found" or "python is not recognized"
**Cause**: Python not in system PATH

**Solution**:
1. Verify Python is installed: Visit https://www.python.org/downloads/
2. During installation, **CHECK** "Add Python to PATH"
3. Restart PowerShell/Command Prompt
4. Test: `python --version`

---

## Audio & Capture Issues

### Issue: "No loopback device found"
**Cause**: Stereo Mix not enabled on your audio device

**Solution**:
1. **Right-click** the speaker icon (bottom-right)
2. Click **"Sound settings"** or **"Open Sound settings"**
3. Scroll down → **"Volume mixer"** or **"App volume and device preferences"**
4. In the **"Recording"** section, look for:
   - "Stereo Mix"
   - "What U Hear"
   - "WASAPI Loopback"
   - "Realtek Stereo Mix"
5. If you see a disabled/grayed-out device:
   - Right-click it
   - Select **"Enable"**
   - Click **"Set as default"**
6. **Restart** GHOST
7. If still not working, update your audio driver:
   - Go to manufacturer's website (Realtek, Intel, NVIDIA, etc.)
   - Download latest audio driver
   - Install and restart

---

### Issue: "PyAudio error: 'portaudio.h' not found"
**Cause**: PyAudio needs system libraries

**Windows Solution**:
```powershell
# Uninstall and reinstall PyAudio
pip uninstall pyaudio -y
pip install pipwin
pipwin install pyaudio
```

Or download pre-built wheel from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio

---

### Issue: Audio capture is working but transcription is empty
**Cause**: 
- Audio too quiet
- Background noise too loud
- Whisper not hearing speech correctly

**Solution**:
1. **Increase audio input**: Check your microphone volume is high enough
2. **Reduce background noise**: Turn off fans, close windows, etc.
3. **Use larger model**: Change in `config.py`:
   ```python
   STT_CONFIG = {
       "model_size": "small",  # Instead of "base"
   }
   ```
4. **Test audio directly**:
   ```powershell
   # Check if audio is being captured
   # Open Sound Recorder app (built-in Windows)
   # Record from "Stereo Mix" and verify you hear audio
   ```

---

### Issue: Transcription is very slow
**Cause**: Whisper model too large for your computer

**Solution - Use smaller model**:
```python
# In ghost_client/core/config.py
STT_CONFIG = {
    "model_size": "tiny",  # Fastest: small, fast, but less accurate
    # "model_size": "base",  # Balanced (default)
    # "model_size": "small",  # Better accuracy, slower
}
```

**Model Comparison**:
| Model | Speed | Accuracy | RAM | First Run |
|-------|-------|----------|-----|-----------|
| tiny | ⚡ 2-3s | ⭐⭐ | 1GB | Fast |
| base | ⚡⚡ 3-5s | ⭐⭐⭐ | 1GB | 1 min |
| small | ⚡⚡⚡ 5-10s | ⭐⭐⭐⭐ | 2GB | 10 min |
| medium | 🐌 10-15s | ⭐⭐⭐⭐⭐ | 5GB | 20 min |
| large | 🐢 15-30s | ⭐⭐⭐⭐⭐ | 10GB | 30 min |

---

## Network & Server Issues

### Issue: "ConnectionRefusedError: [WinError 10061]"
**Cause**: Relay server not running

**Solution**:
1. Open **separate PowerShell window**
2. Navigate to `ghost_relay` folder
3. Run: `python main_server.py`
4. You should see:
   ```
   INFO:     Application startup complete
   INFO:     Uvicorn running on http://0.0.0.0:8000
   ```
5. Keep this window open while using the client

---

### Issue: "GEMINI_API_KEY not found" or similar error
**Cause**: API key not configured

**Solution**:
1. Get your API key from https://ai.google.dev/
2. Edit `ghost_relay/.env`:
   ```
   GEMINI_API_KEY=YOUR_ACTUAL_API_KEY_HERE
   ```
3. **Save the file** (Ctrl+S)
4. **Restart the server**:
   - Close existing server window (Ctrl+C)
   - Run `python main_server.py` again

---

### Issue: "Request timeout" or slow responses
**Cause**: 
- Internet connection slow
- Gemini API overloaded
- Processing taking too long

**Solution**:
1. **Check internet**: Open browser, check you can access websites
2. **Reduce timeout**: Edit `ghost_client/core/config.py`:
   ```python
   RELAY_CONFIG = {
       "timeout": 60,  # Increase from 30 to 60 seconds
   }
   ```
3. **Wait for response**: Some requests take 5-10 seconds
4. **Check server logs**: Look for error messages in server terminal

---

### Issue: Server returns "Internal server error"
**Solution**:
1. Check the server console for detailed error message
2. Common causes:
   - **API Key wrong**: Check `.env` file
   - **Gemini SDK missing**: `pip install google-generativeai`
   - **Request malformed**: Check JSON format in logs
3. Restart server and try again

---

## Client Application Issues

### Issue: App starts but no UI appears
**Expected Behavior**: 
- App is intentionally invisible
- No window in taskbar
- No visible interface

**Solution**:
- This is **correct**! 
- App is running in background mode
- During video calls, responses will appear
- Press `Ctrl+C` in terminal to stop

### Issue: "ModuleNotFoundError: No module named 'tkinter'"
**Cause**: tkinter not installed (unusual)

**Solution**:
```powershell
# Reinstall Python with tkinter
# Windows: Download Python installer again, select "tcl/tk and IDLE"
# Or: Use package manager
pip install tk
```

---

### Issue: Overlay text not showing during calls
**Cause**:
- Application may not be running
- Video call detection failed
- STT not processing audio

**Solution**:
1. **Check client is running**:
   - Should see messages like "Processing thread started"
   - Look for "Transcribed: ..." messages
2. **Check audio is being captured**:
   - Open Windows Sound Recorder
   - Record from "Stereo Mix"
   - If no sound, your audio device doesn't support loopback
3. **Enable debug logging**:
   ```python
   # In config.py
   DEBUG_MODE = True
   LOG_CONFIG["level"] = "DEBUG"
   ```
   - Check `ghost_client.log` file for details

---

### Issue: Permission dialog won't appear
**Cause**: tkinter display issue

**Solution**:
```powershell
# Run the client with output to see if permissions are being requested
python main_client.py
# You should see "Requesting system permissions..."
```

---

## Performance Issues

### Issue: High CPU/RAM usage
**Cause**: Whisper processing, or buffer filling up

**Solution**:
1. **Close other apps**: Free up RAM
2. **Reduce buffer size**:
   ```python
   AUDIO_CONFIG = {
       "buffer_duration": 15,  # Instead of 30 (seconds)
   }
   ```
3. **Use smaller STT model**: (see Audio issues section)
4. **Check for memory leaks**:
   - Restart the client every hour
   - Monitor Task Manager (Ctrl+Shift+Esc)

---

### Issue: Lag between speech and response
**Cause**: Normal operation - several steps take time

**Typical latency breakdown**:
- Audio capture: Real-time
- **Transcription: 2-5 seconds** ← Here
- **Network: 1-2 seconds** ← Here  
- **Gemini generation: 2-5 seconds** ← Here
- Display: <100ms

**Total: 5-12 seconds from speech to response**

**To reduce**:
1. Use smaller STT model (faster)
2. Internet closer to Gemini server
3. Reduce response length in prompt

---

## Installation Problems

### Issue: "pip install fails" or "No module named pip"
**Cause**: pip not properly configured

**Solution**:
```powershell
# Reinstall pip
python -m ensurepip --upgrade
pip --version  # Test it works
```

---

### Issue: Can't run `setup.py`
**Cause**: Permissions or Python path issue

**Solution**:
```powershell
# Run with explicit Python path
python setup.py
# Or use python3 if python is aliased
python3 setup.py
```

---

## Debug Mode

### Enable detailed logging:
```python
# In ghost_client/core/config.py
DEBUG_MODE = True
LOG_CONFIG["level"] = "DEBUG"
```

Then check `ghost_client.log` for detailed information.

### Get server debug info:
```powershell
# In ghost_relay/.env
DEBUG_MODE=True
LOG_LEVEL=DEBUG
```

Then check server console for detailed error messages.

---

## Getting Help

1. **Check logs first**:
   - Client: `ghost_client.log`
   - Server: Console output

2. **Read documentation**:
   - [QUICKSTART.md](QUICKSTART.md) - Setup guide
   - [ARCHITECTURE.md](docs/ARCHITECTURE.md) - Technical details

3. **Search common issues** (above)

4. **Try these steps**:
   - Restart app
   - Restart server
   - Restart Windows
   - Reinstall dependencies: `pip install --upgrade -r requirements_*.txt`

---

## Advanced: Windows Audio Settings

If your audio device isn't showing Stereo Mix:

### For Realtek Audio:
1. Right-click speaker → Sound settings
2. → Recording devices
3. Right-click empty area → **"Show disabled devices"**
4. Right-click "Stereo Mix" → Enable

### For NVIDIA/AMD HDMI Audio:
- HDMI devices sometimes don't support loopback
- Try USB audio interface instead

### For Virtual Audio:
- Install VB-Audio Cable (free): https://vb-audio.com/Cable/
- Set as system source

---

## Still Having Issues?

1. Read through this guide
2. Check `ghost_client.log` and server output
3. Review [ARCHITECTURE.md](docs/ARCHITECTURE.md) for how components work
4. Double-check API key in `ghost_relay/.env`
5. Verify Stereo Mix is enabled in Windows Audio settings
6. Ensure server is running before starting client

Good luck! 👻
