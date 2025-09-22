#!/usr/bin/env python3
"""
Integration tests for the oscilloscope functionality using Playwright.

Purpose:
    Validate that the oscilloscope WebSocket connection, data streaming,
    and UI interactions work correctly end-to-end.

Scope:
    - WebSocket connection establishment
    - Real-time data streaming
    - UI control interactions
    - Waveform visualization
    - Error handling

Overview: End-to-end integration tests using Playwright to validate oscilloscope functionality including
WebSocket connections, real-time data streaming, user interface interactions, waveform visualization,
control panel operations, and error handling scenarios across the complete technology stack from frontend
to backend.

Dependencies:
    - playwright
    - pytest
    - asyncio

Exports: Playwright-based integration test classes and browser automation fixtures for oscilloscope testing

Interfaces: Async pytest fixtures and test methods using Playwright browser automation API

Implementation:
    Uses Playwright to automate browser interactions and validate
    the oscilloscope functionality across the full stack.
"""

import asyncio
import json
from typing import Any, AsyncGenerator

import pytest
import pytest_asyncio

try:
    from playwright.async_api import Page, WebSocket, async_playwright  # type: ignore[import-not-found]
except ImportError:
    # For type checking when playwright is not installed
    Page = Any
    WebSocket = Any
    async_playwright = None

# Enable auto mode for async fixtures
pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture(scope="function")
async def browser() -> AsyncGenerator[Any, None]:
    """Create a browser instance for testing."""
    if async_playwright is None:
        pytest.skip("Playwright not installed")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        yield browser
        await browser.close()


@pytest_asyncio.fixture(scope="function")
async def page(browser: Any) -> Any:
    """Create a page instance for testing."""
    context = await browser.new_context()
    page = await context.new_page()
    yield page
    await context.close()


@pytest.mark.skip(reason="Playwright integration tests require special network setup")
class TestOscilloscopeIntegration:
    """Integration tests for oscilloscope functionality."""

    @pytest.mark.asyncio
    async def test_oscilloscope_page_loads(self, page: Any) -> None:
        """Test that the oscilloscope page loads successfully."""
        # Navigate to the app - use container name for Docker network
        await page.goto("http://durable-code-frontend-feat-no-skipped-tests-linter-dev:5173")

        # Wait for the app to load
        await page.wait_for_selector("#root", timeout=10000)

        # Check that the Demo tab exists
        demo_tab = await page.query_selector('button:has-text("Demo")')
        assert demo_tab is not None, "Demo tab not found"

        # Click the Demo tab
        await demo_tab.click()

        # Wait for oscilloscope components to load
        await page.wait_for_selector("canvas", timeout=5000)

        # Verify canvas is present
        canvas = await page.query_selector("canvas")
        assert canvas is not None, "Oscilloscope canvas not found"

    @pytest.mark.asyncio
    async def test_websocket_connection(self, page: Any) -> None:
        """Test that WebSocket connection is established."""
        ws_connected = False
        ws_messages = []

        # Set up WebSocket event handlers
        def on_websocket(ws: Any) -> None:
            nonlocal ws_connected
            ws_connected = True

            def on_message(message: str) -> None:
                try:
                    data = json.loads(message)
                    ws_messages.append(data)
                except json.JSONDecodeError:
                    pass

            ws.on("framereceived", lambda event: on_message(event.get("payload", "")))

        page.on("websocket", on_websocket)

        # Navigate to the app
        await page.goto("http://durable-code-frontend-feat-no-skipped-tests-linter-dev:5173")

        # Wait for the Demo tab and click it
        await page.wait_for_selector('button:has-text("Demo")', timeout=10000)
        await page.click('button:has-text("Demo")')

        # Wait for WebSocket connection
        await asyncio.sleep(2)

        assert ws_connected, "WebSocket connection was not established"
        assert len(ws_messages) > 0, "No WebSocket messages received"

    @pytest.mark.asyncio
    async def test_oscilloscope_controls(self, page: Any) -> None:
        """Test oscilloscope control interactions."""
        # Navigate to the Demo tab
        await page.goto("http://durable-code-frontend-feat-no-skipped-tests-linter-dev:5173")
        await page.wait_for_selector('button:has-text("Demo")', timeout=10000)
        await page.click('button:has-text("Demo")')

        # Wait for controls to load
        await page.wait_for_selector('button:has-text("Connect")', timeout=5000)

        # Click Connect button
        connect_button = await page.query_selector('button:has-text("Connect")')
        if connect_button:
            await connect_button.click()
            await asyncio.sleep(1)

        # Test waveform selector if present
        waveform_selector = await page.query_selector("select")
        if waveform_selector:
            # Change waveform type
            await waveform_selector.select_option("square")
            await asyncio.sleep(0.5)

            await waveform_selector.select_option("triangle")
            await asyncio.sleep(0.5)

            await waveform_selector.select_option("sine")
            await asyncio.sleep(0.5)

        # Test frequency control if present
        frequency_input = await page.query_selector('input[type="range"]')
        if frequency_input:
            # Adjust frequency
            await frequency_input.fill("5")
            await asyncio.sleep(0.5)

    @pytest.mark.asyncio
    async def test_oscilloscope_data_streaming(self, page: Any) -> None:
        """Test that oscilloscope receives and displays streaming data."""
        # Navigate to Demo tab
        await page.goto("http://durable-code-frontend-feat-no-skipped-tests-linter-dev:5173")
        await page.wait_for_selector('button:has-text("Demo")', timeout=10000)
        await page.click('button:has-text("Demo")')

        # Wait for canvas
        await page.wait_for_selector("canvas", timeout=5000)

        # Click Connect if button exists
        connect_button = await page.query_selector('button:has-text("Connect")')
        if connect_button:
            await connect_button.click()

        # Wait for data streaming
        await asyncio.sleep(3)

        # Check if canvas has been rendered (by checking its data URL changes)
        canvas = await page.query_selector("canvas")
        if canvas:
            # Take two snapshots of the canvas
            snapshot1 = await canvas.screenshot()
            await asyncio.sleep(1)
            snapshot2 = await canvas.screenshot()

            # If data is streaming, the snapshots should be different
            assert snapshot1 != snapshot2, "Canvas is not updating - no data streaming detected"

    @pytest.mark.asyncio
    async def test_oscilloscope_disconnect_reconnect(self, page: Any) -> None:
        """Test disconnect and reconnect functionality."""
        # Navigate to Demo tab
        await page.goto("http://durable-code-frontend-feat-no-skipped-tests-linter-dev:5173")
        await page.wait_for_selector('button:has-text("Demo")', timeout=10000)
        await page.click('button:has-text("Demo")')

        # Connect
        connect_button = await page.query_selector('button:has-text("Connect")')
        if connect_button:
            await connect_button.click()
            await asyncio.sleep(1)

            # Look for Disconnect button
            disconnect_button = await page.query_selector('button:has-text("Disconnect")')
            if disconnect_button:
                # Disconnect
                await disconnect_button.click()
                await asyncio.sleep(1)

                # Reconnect
                connect_button = await page.query_selector('button:has-text("Connect")')
                if connect_button:
                    await connect_button.click()
                    await asyncio.sleep(1)

                    # Verify connection is re-established
                    disconnect_button = await page.query_selector('button:has-text("Disconnect")')
                    assert disconnect_button is not None, "Reconnection failed"

    @pytest.mark.asyncio
    async def test_oscilloscope_error_handling(self, page: Any) -> None:
        """Test error handling when backend is unavailable."""
        # Stop the backend (simulate failure)
        # This would need to be coordinated with Docker commands

        # For now, test that the UI handles errors gracefully
        await page.goto("http://durable-code-frontend-feat-no-skipped-tests-linter-dev:5173")
        await page.wait_for_selector('button:has-text("Demo")', timeout=10000)
        await page.click('button:has-text("Demo")')

        # The app should still load even if WebSocket fails
        await page.wait_for_selector("canvas", timeout=5000)
        canvas = await page.query_selector("canvas")
        assert canvas is not None, "App failed to load canvas element"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
