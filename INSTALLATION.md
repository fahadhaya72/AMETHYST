# GHOST - Windows Installation Guide

Complete step-by-step installation guide for Windows users.

## Prerequisites Check

Before installing, verify you have:
- ✅ Windows 10 or Windows 11
- ✅ Administrator access (for audio driver access)
- ✅ Internet connection (for downloading dependencies)
- ✅ ~5 GB free disk space
- ✅ Google account (for getting API key)

---

## Step 1: Install Python 3.11+

### Download Python
1. Visit https://www.python.org/downloads/
2. Click **"Download Python 3.12.x"** (or latest 3.11+)
3. Wait for download to complete

### Install Python
1. Run the downloaded `.exe` file
2. **IMPORTANT**: Check the box: **"Add Python to PATH"** ✓
3. Click **"Customize installation"**
4. **IMPORTANT**: Make sure these are checked:
   - ✅ tcl/tk and IDLE (for GUI)
   - ✅ pip
5. Click **"Install"**
6. Wait for installation to complete
7. Click **"Close"**

### Verify Installation
1. Open **PowerShell** (Windows key → type "powershell" → Enter)
2. Type this command:
   ```powershell
   python --version
   ```
3. You should see: `Python 3.12.x` (or your version)
4. Type:
   ```powershell
   python -m pip --version
   ```
5. You should see: `pip X.X.X from...`

✅ If both commands work, Python is installed correctly!

---

## Step 2: Get Google Gemini API Key

### Create Google Account (if needed)
1. Visit https://accounts.google.com
2. Click **"Create account"**
3. Fill in your details
4. Complete verification

### Get Your API Key
1. Visit https://ai.google.dev/
2. Click **"Get API Key"** button
3. Select your project (or create one)
4. Click **"Create API key"**
5. **COPY** the generated API key (looks like: `AIzaSy...`)
6. **SAVE IT SOMEWHERE SAFE** - you'll need it next!

⚠️ **NEVER share this key publicly or on GitHub!**

---

## Step 3: Download GHOST Project

### Option A: Download ZIP (Easiest)
1. Visit the GHOST repository
2. Click **"Code"** → **"Download ZIP"**
3. Right-click the ZIP file → **"Extract All..."**
4. Choose a location (e.g., `C:\Users\YourName\Documents\AIMEET`)
5. Click **"Extract"**

### Option B: Use Git (If installed)
```powershell
git clone <repository-url>
cd AIMEET
```

---

## Step 4: Install Dependencies

### Open PowerShell in AIMEET Folder
1. Open File Explorer
2. Navigate to the AIMEET folder
3. Right-click in empty space
4. Click **"Open PowerShell window here"**

### Run Setup Script
```powershell
python setup.py
```

This will:
- ✅ Install all Python packages
- ✅ Create necessary directories
- ✅ Generate `.env` file
- ✅ Run automated tests

The script will pause if there are issues and show you how to fix them.

---

## Step 5: Configure Your API Key

### Edit the .env File
1. Navigate to `ghost_relay` folder
2. Right-click `‍‍‍‍.env` file
3. Click **"Open with"** → **"Notepad"**
4. Replace:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```
   with your actual key:
   ```
   GEMINI_API_KEY=AIzaSy...YOUR_KEY_HERE...
   ```
5. **Save** (Ctrl+S)
6. Close Notepad

⚠️ **IMPORTANT**: 
- Don't use quotes around the key
- No spaces before/after the key
- Only one API key per line

---

## Step 6: Enable Stereo Mix in Windows

### For Windows 10 / 11

1. **Right-click** the speaker icon in system tray (bottom-right)
2. Click **"Sound settings"** or **"Open Sound settings"**

3. **Scroll down** to find:
   - **"Volume mixer"**, or
   - **"App volume and device preferences"**, or
   - **"Advanced"**

4. Look for **Recording devices** section

5. Find one of these:
   - "Stereo Mix"
   - "What U Hear"
   - "WASAPI Loopback"
   - "Realtek Stereo Mix"
   - "(Audio Device) - Loopback"

6. If the device appears **grayed out/disabled**:
   - Right-click it
   - Select **"Enable"**
   - Right-click again
   - Select **"Set as default device"**

7. Close Sound settings

### If Stereo Mix Doesn't Appear

**Update Audio Driver**:
1. Right-click speaker icon → **"Device manager"**
2. Expand **"Sound, video and game controllers"**
3. Right-click your audio device
4. Click **"Update driver"**
5. **"Search automatically for drivers"**
6. Wait for update to complete
7. **Restart Windows**
8. Check Sound settings again

**Alternative**: Install Virtual Audio Cable
- Download VB-Audio Cable: https://vb-audio.com/Cable/
- Install and follow instructions
- Use as audio source in GHOST

---

## Step 7: Test Installation

### Start the Server
1. Open **PowerShell** (or reuse existing)
2. Navigate to `ghost_relay` folder:
   ```powershell
   cd ghost_relay
   ```
3. Start server:
   ```powershell
   python main_server.py
   ```
4. You should see:
   ```
   INFO:     Application startup complete
   INFO:     Uvicorn running on http://0.0.0.0:8000
   ```
5. **Keep this window open!**

### Start the Client
1. Open **new PowerShell window** (don't close the server!)
2. Navigate to `ghost_client` folder:
   ```powershell
   cd ghost_client
   ```
3. Start client:
   ```powershell
   python main_client.py
   ```
4. You should see:
   ```
   Starting GHOST...
   Audio capture started
   Processing thread started
   ```

### Test with Video Call
1. Open Google Meet, Zoom, Teams, or WhatsApp
2. Start a video call (or call with someone)
3. Say something like: "Hello, how are you?"
4. GHOST should:
   - Capture your voice
   - Transcribe it
   - Generate a response
   - **Display it on your screen** in bright green text

5. If you see the response display, it's working! ✅

---

## Step 8: Stop the Application

### To Stop GHOST
- In either PowerShell window, press **Ctrl+C**
- Type `Y` if asked to confirm
- Both windows will shut down

---

## Optional: Create Shortcuts

### Desktop Shortcut to Start Server
1. Right-click Desktop
2. Click **"New"** → **"Shortcut"**
3. Location:
   ```
   powershell.exe -NoExit -Command "cd 'C:\path\to\AIMEET\ghost_relay'; python main_server.py"
   ```
4. Name: "GHOST - Start Server"
5. Click **"Finish"**
6. Right-click shortcut → **"Properties"**
7. Change icon if desired
8. Click **"OK"**

### Desktop Shortcut to Start Client
1. Right-click Desktop
2. Click **"New"** → **"Shortcut"**
3. Location:
   ```
   powershell.exe -NoExit -Command "cd 'C:\path\to\AIMEET\ghost_client'; python main_client.py"
   ```
4. Name: "GHOST - Start Client"
5. Click **"Finish"**

---

## Troubleshooting Installation

### "Python not found"
- **Solution**: Reinstall Python, make sure to check "Add Python to PATH"
- Test: Open new PowerShell, type `python --version`

### "pip: command not found"
- **Solution**: Reinstall Python with pip option checked
- Or: `python -m pip install --upgrade pip`

### "Stereo Mix not appearing"
- See [Step 6](#step-6-enable-stereo-mix-in-windows)
- Update audio drivers
- Try VB-Audio Cable alternative

### "GEMINI_API_KEY not found"
- **Solution**: Check `.env` file in `ghost_relay` folder
- Verify API key is correctly pasted (no spaces, no quotes)
- Restart the server

### "ModuleNotFoundError"
- **Solution**: 
  ```powershell
  pip install -r requirements_client.txt
  pip install -r requirements_server.txt
  ```

### Setup script fails
- Make sure you're in the AIMEET folder
- Run: `python setup.py` (not `python setup`)
- Check internet connection
- Try: `pip install --upgrade pip setuptools`

---

## System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **OS** | Windows 10 | Windows 11 |
| **CPU** | Intel i5 / Ryzen 5 | Intel i7 / Ryzen 7+ |
| **RAM** | 4 GB | 8 GB+ |
| **Disk** | 5 GB | 10 GB |
| **Internet** | 5 Mbps | 10 Mbps+ |
| **Python** | 3.11+ | 3.12+ |

---

## Next Steps

After successful installation:

1. **Read the Quick Start Guide**: [QUICKSTART.md](QUICKSTART.md)
2. **Understand the architecture**: [ARCHITECTURE.md](docs/ARCHITECTURE.md)
3. **Customize settings**: Edit `ghost_client/core/config.py`
4. **Run tests**: `python tests/test_audio_buffer.py`

---

## Getting Help

If you have issues:

1. **Check logs**:
   - Client: [ghost_client.log](ghost_client.log)
   - Server: Console window output

2. **Read documentation**:
   - [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Solutions to common problems
   - [QUICKSTART.md](QUICKSTART.md) - Quick reference
   - [README.md](README.md) - Full documentation

3. **Enable debug mode**:
   ```python
   # In ghost_client/core/config.py
   DEBUG_MODE = True
   ```
   Then check `ghost_client.log` for detailed messages

---

## Security Notes

✅ **What's Secure:**
- API key stored locally (`.env`)
- Audio only transcribed to text
- Text sent to Gemini, then forgotten
- No conversation logging

❌ **What's NOT Secure:**
- If someone gets your `.env` file, they get your API key
- Gemini (Google) processes your transcriptions
- Never share your API key!

**Best Practices:**
- Keep API key private
- Update dependencies regularly: `pip install --upgrade -r requirements_*.txt`
- Don't commit `.env` to GitHub/Git

---

## Congratulations! 🎉

You've successfully installed GHOST!

Next, read [QUICKSTART.md](QUICKSTART.md) for usage instructions.

Happy using! 👻
