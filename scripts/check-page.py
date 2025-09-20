#!/usr/bin/env python3
from playwright.sync_api import sync_playwright
import time

def check_page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Navigate to the page
        page.goto("http://localhost:5173")

        # Wait for content to load
        time.sleep(3)

        # Get the root div content
        root_content = page.query_selector("#root")
        if root_content:
            html = root_content.inner_html()
            text = root_content.inner_text()

            print("=== ROOT DIV HTML (first 500 chars) ===")
            print(html[:500] if html else "EMPTY")
            print("\n=== ROOT DIV TEXT (first 300 chars) ===")
            print(text[:300] if text else "EMPTY")

            if html and len(html) > 10:
                print("\n✅ SUCCESS: Page has content!")
                print(f"Total HTML length: {len(html)} characters")
            else:
                print("\n❌ FAILURE: Page is blank!")
        else:
            print("❌ FAILURE: No root div found!")

        # Check for console errors
        page.on("console", lambda msg: print(f"Console {msg.type}: {msg.text}") if msg.type in ["error", "warning"] else None)

        browser.close()

if __name__ == "__main__":
    check_page()
