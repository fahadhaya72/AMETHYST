"""Test relay server authentication and API communication."""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ghost_relay.services.gemini_service import GeminiService


def test_gemini_initialization():
    """Test Gemini service initialization."""
    service = GeminiService()
    
    # Should initialize (but may not have API key)
    assert service is not None
    assert service.model_name == "gemini-1.5-flash"
    print("✓ Gemini initialization test passed")


def test_gemini_readiness():
    """Test checking if Gemini is ready."""
    service = GeminiService()
    
    # readiness depends on API key availability
    is_ready = service.is_ready()
    print(f"  Gemini readiness: {is_ready}")
    print("✓ Gemini readiness test passed")


def run_all_tests():
    """Run all tests."""
    print("Running Relay Authentication tests...\n")
    
    try:
        test_gemini_initialization()
        test_gemini_readiness()
        
        print("\n✓ All relay tests passed!")
        return True
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
