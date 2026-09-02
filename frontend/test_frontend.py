import pytest
from playwright.sync_api import sync_playwright

def test_frontend_renders_and_loads():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Load local static frontend file directly
        # Note: In a real test environment, we'd start a server.
        # Here we'll mock the server or just check the local file load if possible.
        # Since we are told to use "http://localhost:3000", we assume the server is running.
        try:
            page.goto("http://localhost:3000")
        except Exception as e:
            pytest.fail(f"Could not load page at http://localhost:3000: {e}")

        # Verify title and primary elements exist
        assert "Campus & Commute" in page.title() or page.locator("text=Campus & Commute").is_visible()
        assert page.locator("#card-attendance").is_visible()
        assert page.locator("#card-exams").is_visible()
        assert page.locator("#card-trains").is_visible()
        assert page.locator("#select-from-station").is_visible()
        assert page.locator("#select-to-station").is_visible()

        browser.close()
