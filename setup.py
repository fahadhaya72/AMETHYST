"""
Setup script for GHOST application.
Automates dependency installation and configuration.
"""

import os
import subprocess
import sys
from pathlib import Path

# Color codes for terminal output
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'
BOLD = '\033[1m'


def print_status(message: str, status: str = "INFO"):
    """Print colored status message."""
    colors = {
        "INFO": '\033[94m',  # Blue
        "SUCCESS": GREEN,
        "WARNING": YELLOW,
        "ERROR": RED,
    }
    color = colors.get(status, RESET)
    print(f"{color}[{status}]{RESET} {message}")


def check_python_version():
    """Check if Python version is 3.11 or higher."""
    print_status("Checking Python version...", "INFO")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print_status(f"Python {version.major}.{version.minor} detected. Requires 3.11+", "ERROR")
        return False
    
    print_status(f"Python {version.major}.{version.minor}.{version.micro} ✓", "SUCCESS")
    return True


def install_dependencies():
    """Install Python dependencies."""
    print_status("Installing dependencies...", "INFO")
    
    base_dir = Path(__file__).parent
    
    # Install client dependencies
    print_status("Installing client dependencies...", "INFO")
    client_reqs = base_dir / "requirements_client.txt"
    if client_reqs.exists():
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(client_reqs)])
            print_status("Client dependencies installed ✓", "SUCCESS")
        except subprocess.CalledProcessError as e:
            print_status(f"Failed to install client dependencies: {e}", "ERROR")
            return False
    
    # Install server dependencies
    print_status("Installing server dependencies...", "INFO")
    server_reqs = base_dir / "requirements_server.txt"
    if server_reqs.exists():
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(server_reqs)])
            print_status("Server dependencies installed ✓", "SUCCESS")
        except subprocess.CalledProcessError as e:
            print_status(f"Failed to install server dependencies: {e}", "ERROR")
            return False
    
    return True


def setup_environment():
    """Set up environment files and directories."""
    print_status("Setting up environment...", "INFO")
    
    base_dir = Path(__file__).parent
    
    # Create .env file if it doesn't exist
    env_file = base_dir / "ghost_relay" / ".env"
    if not env_file.exists():
        print_status(f"Creating {env_file}...", "INFO")
        env_content = """# GHOST Relay Server - Environment Variables
# IMPORTANT: Keep this file SECURE - never commit to version control!

GEMINI_API_KEY=your_api_key_here
RELAY_HOST=0.0.0.0
RELAY_PORT=8000
RELAY_PROTOCOL=http
LOG_LEVEL=INFO
DEBUG_MODE=False
"""
        env_file.write_text(env_content)
        print_status(f"Created {env_file} (UPDATE WITH YOUR API KEY)", "WARNING")
    else:
        print_status(f"{env_file} already exists ✓", "SUCCESS")
    
    # Create logs directory
    logs_dir = base_dir / "logs"
    logs_dir.mkdir(exist_ok=True)
    print_status(f"Logs directory ready: {logs_dir} ✓", "SUCCESS")
    
    # Create cache directory
    cache_dir = base_dir / "ghost_client" / ".cache"
    cache_dir.mkdir(exist_ok=True)
    print_status(f"Cache directory ready: {cache_dir} ✓", "SUCCESS")
    
    return True


def check_gemini_api_key():
    """Check if Gemini API key is configured."""
    print_status("Checking Gemini API key...", "INFO")
    
    base_dir = Path(__file__).parent
    env_file = base_dir / "ghost_relay" / ".env"
    
    if not env_file.exists():
        print_status("No .env file found", "WARNING")
        return False
    
    content = env_file.read_text()
    if "your_api_key_here" in content or "GEMINI_API_KEY=" not in content:
        print_status("⚠️  Gemini API key not configured!", "WARNING")
        print("   To set up your API key:")
        print("   1. Go to https://ai.google.dev/")
        print("   2. Click 'Get API Key'")
        print("   3. Copy your API key")
        print(f"   4. Edit {env_file}")
        print("   5. Replace 'your_api_key_here' with your actual key")
        return False
    
    print_status("Gemini API key configured ✓", "SUCCESS")
    return True


def run_tests():
    """Run automated tests."""
    print_status("Running automated tests...", "INFO")
    
    base_dir = Path(__file__).parent
    test_dir = base_dir / "tests"
    
    if not test_dir.exists():
        print_status("Tests directory not found", "WARNING")
        return True  # Don't fail if tests don't exist
    
    # Run audio buffer tests
    test_buffer = test_dir / "test_audio_buffer.py"
    if test_buffer.exists():
        print_status("Running audio buffer tests...", "INFO")
        try:
            result = subprocess.run([sys.executable, str(test_buffer)], capture_output=True, text=True)
            if result.returncode == 0:
                print_status("Audio buffer tests passed ✓", "SUCCESS")
            else:
                print_status(f"Audio buffer tests failed: {result.stderr}", "WARNING")
        except Exception as e:
            print_status(f"Error running tests: {e}", "WARNING")
    
    return True


def main():
    """Run the setup process."""
    print(f"\n{BOLD}{'='*60}")
    print(f"GHOST Setup Wizard")
    print(f"{'='*60}{RESET}\n")
    
    # Step 1: Check Python version
    if not check_python_version():
        print_status("Setup failed: Python 3.11+ required", "ERROR")
        return False
    
    # Step 2: Install dependencies
    print()
    if not install_dependencies():
        print_status("Setup failed: Could not install dependencies", "ERROR")
        return False
    
    # Step 3: Set up environment
    print()
    if not setup_environment():
        print_status("Setup failed: Could not set up environment", "ERROR")
        return False
    
    # Step 4: Check API key
    print()
    api_key_configured = check_gemini_api_key()
    
    # Step 5: Run tests
    print()
    if not run_tests():
        print_status("Some tests failed (this is okay)", "WARNING")
    
    # Final summary
    print(f"\n{BOLD}{'='*60}")
    print(f"Setup Complete!{RESET}")
    print(f"{'='*60}\n")
    
    if not api_key_configured:
        print(f"{YELLOW}⚠️  API KEY REQUIRED{RESET}")
        print("   Edit ghost_relay/.env and add your Gemini API key\n")
    
    print("Next steps:")
    print("1. Edit ghost_relay/.env with your Gemini API key")
    print("2. Enable Stereo Mix in Windows Sound settings")
    print("3. Start the server: cd ghost_relay && python main_server.py")
    print("4. Start the client: cd ghost_client && python main_client.py")
    print("5. Open a video call and test!\n")
    print("For help, see:")
    print("   - QUICKSTART.md (quick start guide)")
    print("   - README.md (full documentation)")
    print("   - docs/ARCHITECTURE.md (technical details)\n")
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print_status("\nSetup cancelled by user", "WARNING")
        sys.exit(1)
    except Exception as e:
        print_status(f"Unexpected error: {e}", "ERROR")
        sys.exit(1)
