import asyncio
from playwright.async_api import async_playwright
import os
import time

async def capture_screenshots():
    # Ensure assets directory exists
    if not os.path.exists('report_assets'):
        os.makedirs('report_assets')

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context(viewport={'width': 1280, 'height': 800})
        page = await context.new_page()

        # Base URL
        base_url = 'http://127.0.0.1:5000'

        # 0. Switch to Agriculture Course
        print("Switching to agriculture course...")
        await page.goto(f'{base_url}/settings')
        await page.wait_for_timeout(2000)
        
        # Select agriculture course from dropdown
        try:
            await page.select_option('select#courseSelect', '农产量调查手册')
            await page.wait_for_timeout(1000)
            print("Switched to 农产量调查手册 course")
        except Exception as e:
            print(f"Warning: Could not switch course automatically: {e}")

        # 1. Home Page
        print(f"Navigating to {base_url}...")
        await page.goto(base_url)
        # Wait for potential animations or load
        await page.wait_for_timeout(2000)
        await page.screenshot(path='report_assets/screenshot_home.png')
        print("Captured screenshot_home.png")

        # 2. Learning Page
        print(f"Navigating to {base_url}/learning...")
        await page.goto(f'{base_url}/learning')
        await page.wait_for_timeout(3000)
        await page.screenshot(path='report_assets/screenshot_learning.png')
        print("Captured screenshot_learning.png")

        # 3. Exam Page
        print(f"Navigating to {base_url}/exam...")
        await page.goto(f'{base_url}/exam')
        await page.wait_for_timeout(3000)
        await page.screenshot(path='report_assets/screenshot_exam.png')
        print("Captured screenshot_exam.png")

        # 4. Review Page
        print(f"Navigating to {base_url}/review...")
        await page.goto(f'{base_url}/review')
        await page.wait_for_timeout(2000)
        await page.screenshot(path='report_assets/screenshot_review.png')
        print("Captured screenshot_review.png")

        await browser.close()

if __name__ == '__main__':
    asyncio.run(capture_screenshots())
