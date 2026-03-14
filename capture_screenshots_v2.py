import asyncio
from playwright.async_api import async_playwright
import os

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1440, 'height': 1200}, color_scheme='dark')
        page = await context.new_page()

        base_path = os.path.join(os.path.dirname(__file__), 'docs', 'screenshots')
        os.makedirs(base_path, exist_ok=True)
        
        url_base = "http://127.0.0.1:5174"

        try:
            # 1. Sector Heatmap
            print("Navigating to Sector Heatmap...")
            await page.goto(f"{url_base}/sectors", wait_until="networkidle", timeout=60000)
            await page.wait_for_timeout(15000) # Wait for APIs to return and charts to render
            await page.screenshot(path=os.path.join(base_path, "sector_heatmap.png"))
            print("Saved sector_heatmap.png")
            
            # 2. Sector Indices
            print("Navigating to Sector Indices...")
            await page.goto(f"{url_base}/indices", wait_until="networkidle", timeout=60000)
            await page.wait_for_timeout(15000)
            await page.screenshot(path=os.path.join(base_path, "sector_indices.png"))
            print("Saved sector_indices.png")

            # 3. Legendary Portfolios
            print("Navigating to Legendary Portfolios...")
            await page.goto(f"{url_base}/legendary", wait_until="networkidle", timeout=60000)
            await page.wait_for_timeout(20000) # This page might take longer due to 5y history
            await page.screenshot(path=os.path.join(base_path, "legendary_portfolios.png"))
            # Overwrite the old _dynamic one too for consistency if needed, but we'll use legendary_portfolios.png
            await page.screenshot(path=os.path.join(base_path, "legendary_portfolios_dynamic.png"))
            print("Saved legendary_portfolios.png")

        except Exception as e:
            print(f"Error occurred: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
