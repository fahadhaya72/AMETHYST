"""Test audio buffer management."""

import numpy as np
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ghost_client.audio.buffer import AudioBuffer


def test_buffer_creation():
    """Test buffer initialization."""
    buffer = AudioBuffer(duration_seconds=10, sample_rate=16000)
    
    assert buffer.max_samples == 160000
    assert buffer.get_duration() == 0.0
    assert not buffer.is_full()
    print("✓ Buffer creation test passed")


def test_buffer_add_audio():
    """Test adding audio to buffer."""
    buffer = AudioBuffer(duration_seconds=2, sample_rate=16000)
    
    # Create 1 second of audio
    audio_chunk = np.random.randn(16000).astype(np.float32)
    buffer.add_chunk(audio_chunk)
    
    duration = buffer.get_duration()
    assert 0.99 < duration < 1.01, f"Expected ~1.0s, got {duration}"
    print("✓ Buffer add audio test passed")


def test_buffer_get_audio():
    """Test retrieving audio from buffer."""
    buffer = AudioBuffer(duration_seconds=5, sample_rate=16000)
    
    # Add 2 seconds of audio
    audio_chunk = np.random.randn(32000).astype(np.float32)
    buffer.add_chunk(audio_chunk)
    
    # Get all audio
    retrieved = buffer.get_audio()
    assert len(retrieved) == 32000
    
    # Get 1 second
    retrieved_1s = buffer.get_audio(duration_seconds=1)
    assert len(retrieved_1s) == 16000
    
    print("✓ Buffer get audio test passed")


def test_buffer_overflow():
    """Test automatic overflow removal."""
    buffer = AudioBuffer(duration_seconds=1, sample_rate=16000)
    
    # Add 2 seconds (should overflow)
    audio_chunk = np.random.randn(32000).astype(np.float32)
    buffer.add_chunk(audio_chunk)
    
    # Should only have 1 second
    assert buffer.get_duration() < 1.01
    assert buffer.is_full()
    print("✓ Buffer overflow test passed")


def test_energy_level():
    """Test energy level calculation."""
    buffer = AudioBuffer(duration_seconds=1, sample_rate=16000)
    
    # Add silent audio (very small values)
    silent = np.ones(16000, dtype=np.float32) * 0.001
    buffer.add_chunk(silent)
    energy = buffer.get_energy_level()
    assert energy < 0.05  # Should be very low
    
    # Add louder audio
    buffer.clear()
    loud = np.ones(16000, dtype=np.float32) * 0.1
    buffer.add_chunk(loud)
    energy = buffer.get_energy_level()
    assert energy > 0.5  # Should be higher
    
    print("✓ Energy level test passed")


def run_all_tests():
    """Run all tests."""
    print("Running AudioBuffer tests...\n")
    
    try:
        test_buffer_creation()
        test_buffer_add_audio()
        test_buffer_get_audio()
        test_buffer_overflow()
        test_energy_level()
        
        print("\n✓ All tests passed!")
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
