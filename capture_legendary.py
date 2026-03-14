from playwright.sync_api import sync_playwright
import os
import time

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 1440, 'height': 1200}, color_scheme='dark')
    page = context.new_page()

    base_path = os.path.join(os.path.dirname(__file__), 'docs', 'screenshots')
    os.makedirs(base_path, exist_ok=True)

    print("Navigating to http://127.0.0.1:5173/legendary...")
    try:
        page.goto("http://127.0.0.1:5173/legendary", wait_until="networkidle", timeout=60000)
        time.sleep(10) # Wait for yfinance fetch and Recharts to render
        page.screenshot(path=os.path.join(base_path, "legendary_portfolios_dynamic.png"))
        print("Saved legendary_portfolios_dynamic.png")
    except Exception as e:
        print(f"Failed: {e}")

    browser.close()

with sync_playwright() as playwright:
    run(playwright)
