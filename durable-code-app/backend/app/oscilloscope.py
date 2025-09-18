"""
Purpose: Real-time oscilloscope data streaming API endpoint for the durable code application.

Scope: WebSocket streaming of waveform data with configurable wave types and parameters
Overview: This module provides real-time streaming of oscilloscope data including sine waves,
    square waves, and white noise. It follows FastAPI best practices with WebSocket support
    for efficient real-time data streaming. Includes comprehensive error handling, proper
    validation, and performance optimizations for smooth visualization.
Dependencies: FastAPI, WebSocket, asyncio, numpy for waveform generation
Exports: WebSocket endpoint for oscilloscope data streaming
Interfaces: WebSocket API endpoint with JSON message protocol
Implementation: FastAPI WebSocket route with async streaming and waveform generation
"""

import asyncio
import contextlib
import json
import math
import random
import time
from datetime import datetime
from enum import Enum
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from loguru import logger
from pydantic import BaseModel, Field, validator

# Constants for waveform generation
SAMPLE_RATE = 1000  # Samples per second
BUFFER_SIZE = 100  # Number of samples per transmission
DEFAULT_FREQUENCY = 10.0  # Hz
DEFAULT_AMPLITUDE = 1.0
DEFAULT_OFFSET = 0.0
PI_TIMES_TWO = 2 * math.pi

# Validation constants
MIN_FREQUENCY = 0.1  # Minimum frequency in Hz
MAX_FREQUENCY = 100.0  # Maximum frequency in Hz
MIN_AMPLITUDE = 0.1  # Minimum amplitude
MAX_AMPLITUDE = 10.0  # Maximum amplitude
MIN_OFFSET = -10.0  # Minimum DC offset
MAX_OFFSET = 10.0  # Maximum DC offset

# Timing constants
COMMAND_TIMEOUT = 0.01  # Timeout for receiving commands in seconds
IDLE_SLEEP_DURATION = 0.1  # Sleep duration when not streaming in seconds

# API Router for oscilloscope endpoints
router = APIRouter(
    prefix="/api/oscilloscope",
    tags=["oscilloscope"],
)


class WaveType(str, Enum):
    """Supported waveform types."""

    SINE = "sine"
    SQUARE = "square"
    NOISE = "noise"


class OscilloscopeCommand(BaseModel):
    """Command model for oscilloscope control."""

    command: str = Field(..., description="Command type (start, stop, configure)")
    wave_type: WaveType | None = Field(WaveType.SINE, description="Type of waveform")
    frequency: float | None = Field(
        DEFAULT_FREQUENCY, ge=MIN_FREQUENCY, le=MAX_FREQUENCY, description="Frequency in Hz"
    )
    amplitude: float | None = Field(DEFAULT_AMPLITUDE, ge=MIN_AMPLITUDE, le=MAX_AMPLITUDE, description="Wave amplitude")
    offset: float | None = Field(DEFAULT_OFFSET, ge=MIN_OFFSET, le=MAX_OFFSET, description="DC offset")

    @validator("frequency")
    def validate_frequency(cls, value: float | None) -> float | None:  # noqa: N805  # pylint: disable=no-self-argument
        """Validate frequency is within reasonable range."""
        if value is not None and (value < MIN_FREQUENCY or value > MAX_FREQUENCY):
            raise ValueError(f"Frequency must be between {MIN_FREQUENCY} and {MAX_FREQUENCY} Hz")
        return value


class OscilloscopeData(BaseModel):
    """Data model for oscilloscope streaming."""

    timestamp: float = Field(..., description="Unix timestamp")
    samples: list[float] = Field(..., description="Waveform samples")
    sample_rate: int = Field(SAMPLE_RATE, description="Sample rate in Hz")
    wave_type: WaveType = Field(..., description="Current waveform type")
    parameters: dict[str, float] = Field(..., description="Current waveform parameters")


class WaveformGenerator:
    """Generate waveform samples for oscilloscope display."""

    def __init__(self) -> None:
        """Initialize the waveform generator."""
        self.phase = 0.0
        self.last_time = time.time()
        self.wave_type = WaveType.SINE
        self.frequency = DEFAULT_FREQUENCY
        self.amplitude = DEFAULT_AMPLITUDE
        self.offset = DEFAULT_OFFSET

    def configure(self, wave_type: WaveType, frequency: float, amplitude: float, offset: float) -> None:
        """Configure waveform parameters."""
        self.wave_type = wave_type
        self.frequency = frequency
        self.amplitude = amplitude
        self.offset = offset

    def _generate_sine_value(self, t: float) -> float:
        """Generate a single sine wave sample."""
        return self.amplitude * math.sin(PI_TIMES_TWO * self.frequency * t + self.phase)

    def _generate_square_value(self, t: float) -> float:
        """Generate a single square wave sample."""
        sine_value = math.sin(PI_TIMES_TWO * self.frequency * t + self.phase)
        return self.amplitude if sine_value >= 0 else -self.amplitude

    def _generate_noise_value(self) -> float:
        """Generate a single white noise sample."""
        return self.amplitude * (2 * random.random() - 1)  # noqa: S311  # nosec B311

    def _get_sample_value(self, t: float) -> float:
        """Get a single sample value based on wave type."""
        if self.wave_type == WaveType.SINE:
            return self._generate_sine_value(t)
        if self.wave_type == WaveType.SQUARE:
            return self._generate_square_value(t)
        if self.wave_type == WaveType.NOISE:
            return self._generate_noise_value()
        return 0.0

    def _update_phase_for_continuity(self, num_samples: int, dt: float) -> None:
        """Update phase to maintain waveform continuity."""
        if self.wave_type == WaveType.NOISE:
            return

        self.phase += PI_TIMES_TWO * self.frequency * num_samples * dt
        # Keep phase in reasonable range
        if self.phase > PI_TIMES_TWO:
            self.phase -= PI_TIMES_TWO

    def generate_samples(self, num_samples: int) -> list[float]:
        """Generate waveform samples based on current configuration."""
        dt = 1.0 / SAMPLE_RATE
        samples = []

        for i in range(num_samples):
            t = i * dt
            value = self._get_sample_value(t)
            samples.append(value + self.offset)

        self._update_phase_for_continuity(num_samples, dt)
        return samples


async def _handle_command(
    command: OscilloscopeCommand, generator: WaveformGenerator, streaming: bool
) -> tuple[bool, str]:
    """Handle incoming WebSocket commands."""
    handlers = {
        "start": _handle_start_command,
        "stop": _handle_stop_command,
        "configure": _handle_configure_command,
    }

    handler = handlers.get(command.command)
    if handler:
        return handler(command, generator, streaming)
    return streaming, "Unknown command"


def _handle_start_command(
    command: OscilloscopeCommand, generator: WaveformGenerator, streaming: bool  # pylint: disable=unused-argument
) -> tuple[bool, str]:
    """Handle start command."""
    generator.configure(
        wave_type=command.wave_type or WaveType.SINE,
        frequency=command.frequency or DEFAULT_FREQUENCY,
        amplitude=command.amplitude or DEFAULT_AMPLITUDE,
        offset=command.offset or DEFAULT_OFFSET,
    )
    return True, f"Started streaming {command.wave_type} wave"


def _handle_stop_command(
    command: OscilloscopeCommand, generator: WaveformGenerator, streaming: bool  # pylint: disable=unused-argument
) -> tuple[bool, str]:
    """Handle stop command."""
    return False, "Stopped streaming"


def _handle_configure_command(
    command: OscilloscopeCommand, generator: WaveformGenerator, streaming: bool
) -> tuple[bool, str]:
    """Handle configure command."""
    generator.configure(
        wave_type=command.wave_type or generator.wave_type,
        frequency=command.frequency or generator.frequency,
        amplitude=command.amplitude or generator.amplitude,
        offset=command.offset or generator.offset,
    )
    return streaming, f"Configured to {command.wave_type} wave"


async def _process_command(websocket: WebSocket, generator: WaveformGenerator, streaming: bool) -> bool:
    """Process incoming WebSocket commands."""
    try:
        message = await asyncio.wait_for(websocket.receive_text(), timeout=COMMAND_TIMEOUT)
        try:
            data = json.loads(message)
            command = OscilloscopeCommand(**data)
            streaming, log_msg = await _handle_command(command, generator, streaming)
            logger.info(log_msg)
        except (json.JSONDecodeError, ValueError) as e:
            logger.error("Invalid command received", error=str(e), exc_info=True)
            await websocket.send_json({"error": str(e)})
    except TimeoutError:  # design-lint: ignore[logging.exception-logging]
        # Timeout is expected when no commands received - no logging needed
        pass
    return streaming


async def _send_data(websocket: WebSocket, generator: WaveformGenerator) -> None:
    """Send oscilloscope data over WebSocket."""
    samples = generator.generate_samples(BUFFER_SIZE)
    response_data = OscilloscopeData(
        timestamp=time.time(),
        samples=samples,
        sample_rate=SAMPLE_RATE,
        wave_type=generator.wave_type,
        parameters={
            "frequency": generator.frequency,
            "amplitude": generator.amplitude,
            "offset": generator.offset,
        },
    )
    await websocket.send_json(response_data.dict())


@router.websocket("/stream")
async def oscilloscope_stream(websocket: WebSocket) -> None:  # noqa: C901
    """Provide WebSocket endpoint for real-time oscilloscope data streaming.

    Accepts commands to start/stop streaming and configure waveform parameters.
    Streams waveform data at configured sample rate.

    Protocol:
        Client -> Server: JSON command (OscilloscopeCommand)
        Server -> Client: JSON data (OscilloscopeData)
    """
    await websocket.accept()
    logger.info("Oscilloscope WebSocket connection established")

    generator = WaveformGenerator()
    streaming = False

    try:
        while True:
            streaming = await _process_command(websocket, generator, streaming)

            if streaming:
                await _send_data(websocket, generator)
                await asyncio.sleep(BUFFER_SIZE / SAMPLE_RATE)
            else:
                await asyncio.sleep(IDLE_SLEEP_DURATION)

    except WebSocketDisconnect:
        logger.debug("Oscilloscope WebSocket connection closed", connection_type="websocket")
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.exception("Error in oscilloscope stream", error=str(e))
        with contextlib.suppress(Exception):
            await websocket.send_json({"error": "Internal server error"})


# Health check for oscilloscope module
@router.get("/health", include_in_schema=False)
async def oscilloscope_health_check() -> dict[str, Any]:
    """Health check endpoint for oscilloscope module."""
    return {
        "status": "healthy",
        "module": "oscilloscope",
        "timestamp": datetime.now().isoformat(),
        "sample_rate": SAMPLE_RATE,
        "supported_waves": [wave.value for wave in WaveType],
    }
