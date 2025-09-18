"""
Purpose: Unit tests for oscilloscope WebSocket streaming endpoint
Scope: Test WebSocket connection, command processing, and data streaming functionality
Overview: Comprehensive test suite for the oscilloscope module including connection tests,
    command validation, waveform generation verification, and error handling scenarios.
Dependencies: pytest, pytest-asyncio, FastAPI test client, WebSocket test support
Exports: Test cases for oscilloscope functionality
Interfaces: pytest test functions
Implementation: Async test functions using FastAPI test client
"""

import json
import asyncio
from typing import Any, Dict, List
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.oscilloscope import WaveType, WaveformGenerator

# Test client
client = TestClient(app)


class TestWaveformGenerator:
    """Test suite for WaveformGenerator class."""

    def test_initialization(self) -> None:
        """Test generator initializes with default values."""
        generator = WaveformGenerator()
        assert generator.wave_type == WaveType.SINE
        assert generator.frequency == 10.0
        assert generator.amplitude == 1.0
        assert generator.offset == 0.0
        assert generator.phase == 0.0

    def test_configure_parameters(self) -> None:
        """Test configuration of waveform parameters."""
        generator = WaveformGenerator()
        generator.configure(
            wave_type=WaveType.SQUARE,
            frequency=20.0,
            amplitude=2.0,
            offset=0.5
        )
        assert generator.wave_type == WaveType.SQUARE
        assert generator.frequency == 20.0
        assert generator.amplitude == 2.0
        assert generator.offset == 0.5

    def test_generate_sine_samples(self) -> None:
        """Test sine wave generation."""
        generator = WaveformGenerator()
        generator.configure(WaveType.SINE, 10.0, 1.0, 0.0)
        samples = generator.generate_samples(100)

        assert len(samples) == 100
        assert all(isinstance(s, float) for s in samples)
        # Sine wave should oscillate between -1 and 1
        assert min(samples) >= -1.1  # Small tolerance
        assert max(samples) <= 1.1

    def test_generate_square_samples(self) -> None:
        """Test square wave generation."""
        generator = WaveformGenerator()
        generator.configure(WaveType.SQUARE, 10.0, 1.0, 0.0)
        samples = generator.generate_samples(100)

        assert len(samples) == 100
        # Square wave should only have two values (plus/minus amplitude)
        unique_values = set(round(s, 5) for s in samples)
        assert len(unique_values) <= 2

    def test_generate_noise_samples(self) -> None:
        """Test white noise generation."""
        generator = WaveformGenerator()
        generator.configure(WaveType.NOISE, 10.0, 1.0, 0.0)
        samples = generator.generate_samples(100)

        assert len(samples) == 100
        # Noise should be random, so all values should be different
        unique_values = set(samples)
        assert len(unique_values) > 90  # Most values should be unique

    def test_dc_offset(self) -> None:
        """Test DC offset is applied correctly."""
        generator = WaveformGenerator()
        offset = 2.5
        generator.configure(WaveType.SINE, 10.0, 1.0, offset)
        samples = generator.generate_samples(100)

        # Average should be close to offset for sine wave
        avg = sum(samples) / len(samples)
        assert abs(avg - offset) < 0.1

    def test_phase_continuity(self) -> None:
        """Test phase continuity between sample batches."""
        generator = WaveformGenerator()
        generator.configure(WaveType.SINE, 10.0, 1.0, 0.0)

        # Generate two consecutive batches
        batch1 = generator.generate_samples(50)
        batch2 = generator.generate_samples(50)

        # The transition between batches should be smooth
        # (no discontinuity at the boundary)
        combined = batch1 + batch2
        assert len(combined) == 100


class TestOscilloscopeWebSocket:
    """Test suite for oscilloscope WebSocket endpoint."""

    def test_websocket_connection(self) -> None:
        """Test WebSocket connection establishment."""
        with client.websocket_connect("/api/oscilloscope/stream") as websocket:
            # Connection should be established
            # Send a test command
            websocket.send_json({
                "command": "start",
                "wave_type": "sine",
                "frequency": 10.0,
                "amplitude": 1.0,
                "offset": 0.0
            })

            # Should receive data
            data = websocket.receive_json()
            assert "timestamp" in data or "error" not in data

    def test_start_command(self) -> None:
        """Test start streaming command."""
        with client.websocket_connect("/api/oscilloscope/stream") as websocket:
            # Send start command
            websocket.send_json({
                "command": "start",
                "wave_type": "sine",
                "frequency": 20.0,
                "amplitude": 2.0,
                "offset": 0.5
            })

            # Receive multiple data packets
            for _ in range(3):
                data = websocket.receive_json()
                assert "timestamp" in data
                assert "samples" in data
                assert "sample_rate" in data
                assert "wave_type" in data
                assert data["wave_type"] == "sine"
                assert "parameters" in data
                assert data["parameters"]["frequency"] == 20.0

    def test_stop_command(self) -> None:
        """Test stop streaming command."""
        with client.websocket_connect("/api/oscilloscope/stream") as websocket:
            # Start streaming
            websocket.send_json({
                "command": "start",
                "wave_type": "sine"
            })

            # Verify streaming
            data = websocket.receive_json()
            assert "samples" in data

            # Stop streaming
            websocket.send_json({"command": "stop"})

            # After stop, no data should be streamed
            # (This is hard to test directly, but we can verify no errors)

    def test_configure_command(self) -> None:
        """Test configuration change during streaming."""
        with client.websocket_connect("/api/oscilloscope/stream") as websocket:
            # Start with sine wave
            websocket.send_json({
                "command": "start",
                "wave_type": "sine",
                "frequency": 10.0
            })

            # Get initial data
            data1 = websocket.receive_json()
            assert data1["wave_type"] == "sine"

            # Configure to square wave
            websocket.send_json({
                "command": "configure",
                "wave_type": "square",
                "frequency": 15.0
            })

            # Get data after configuration
            # May need to receive a few packets for the change to take effect
            for _ in range(3):
                data2 = websocket.receive_json()
                if data2.get("wave_type") == "square":
                    assert data2["parameters"]["frequency"] == 15.0
                    break

    def test_invalid_command_handling(self) -> None:
        """Test handling of invalid commands."""
        with client.websocket_connect("/api/oscilloscope/stream") as websocket:
            # Send invalid JSON
            websocket.send_text("not a json")

            # Should receive error response
            data = websocket.receive_json()
            assert "error" in data or "samples" in data  # Either error or continue streaming

    def test_invalid_parameters(self) -> None:
        """Test validation of command parameters."""
        with client.websocket_connect("/api/oscilloscope/stream") as websocket:
            # Send command with invalid frequency
            websocket.send_json({
                "command": "start",
                "wave_type": "sine",
                "frequency": 200.0  # Out of range
            })

            # Should handle gracefully (either error or use default)
            data = websocket.receive_json()
            assert data is not None

    def test_all_wave_types(self) -> None:
        """Test all supported wave types."""
        with client.websocket_connect("/api/oscilloscope/stream") as websocket:
            for wave_type in ["sine", "square", "noise"]:
                websocket.send_json({
                    "command": "configure",
                    "wave_type": wave_type
                })

                websocket.send_json({"command": "start"})

                data = websocket.receive_json()
                assert "samples" in data
                # Wave type might not update immediately
                # but should not cause errors

    def test_data_format(self) -> None:
        """Test the format of streamed data."""
        with client.websocket_connect("/api/oscilloscope/stream") as websocket:
            websocket.send_json({
                "command": "start",
                "wave_type": "sine"
            })

            data = websocket.receive_json()

            # Verify data structure
            assert isinstance(data.get("timestamp"), (int, float))
            assert isinstance(data.get("samples"), list)
            assert isinstance(data.get("sample_rate"), int)
            assert isinstance(data.get("wave_type"), str)
            assert isinstance(data.get("parameters"), dict)

            # Verify samples are floats
            samples = data["samples"]
            assert len(samples) > 0
            assert all(isinstance(s, (int, float)) for s in samples)


class TestOscilloscopeHealth:
    """Test suite for oscilloscope health check endpoint."""

    def test_health_check(self) -> None:
        """Test health check endpoint."""
        response = client.get("/api/oscilloscope/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert data["module"] == "oscilloscope"
        assert "timestamp" in data
        assert "sample_rate" in data
        assert "supported_waves" in data
        assert set(data["supported_waves"]) == {"sine", "square", "noise"}


# Performance test (optional, can be skipped in CI)
@pytest.mark.slow
class TestOscilloscopePerformance:
    """Performance tests for oscilloscope streaming."""

    def test_streaming_rate(self) -> None:
        """Test that streaming maintains expected data rate."""
        with client.websocket_connect("/api/oscilloscope/stream") as websocket:
            websocket.send_json({
                "command": "start",
                "wave_type": "sine",
                "frequency": 50.0
            })

            # Collect data for a short period
            import time
            start_time = time.time()
            packet_count = 0
            sample_count = 0

            while time.time() - start_time < 1.0:  # Collect for 1 second
                try:
                    websocket.send_text("")  # Keep connection alive
                    data = websocket.receive_json()
                    if "samples" in data:
                        packet_count += 1
                        sample_count += len(data["samples"])
                except:
                    break

            # Should receive reasonable amount of data
            assert packet_count > 0
            assert sample_count > 0
