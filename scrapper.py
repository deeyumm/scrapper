from playwright.sync_api import sync_playwright
import pandas as pd
import time

mall_urls = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    for pg in range(1, 5):  # There are 4 pages
        print(f"\n Visiting page {pg}...")
        page.goto(f"https://www.scai.in/member-malls/page/{pg}/")
        time.sleep(3)  # Wait for page content to load

        page.mouse.wheel(0, 1000)  # Scroll just a little to trigger lazy loading
        time.sleep(2)

        cards = page.locator(".elementor-post")  # Each mall card
        total = cards.count()
        print(f" Found {total} cards on this page.")

        for i in range(total):
            card = cards.nth(i)

            # Check if this card has an image to hover
            image = card.locator("img")
            if image.count() == 0:
                print(f" Skipping card {i+1} (no image)")
                continue

            print(f"➡ Hovering over card {i+1} on page {pg}...")
            card.hover()
            time.sleep(0.5)

            # Try to get the link after hovering
            link = card.locator("a.elementor-post__thumbnail__link")
            if link.count() > 0:
                href = link.get_attribute("href")
                if href:
                    print(f"Found link: {href}")
                    mall_urls.append(href)
            else:
                print(f" No clickable icon on card {i+1}")

    browser.close()

# Save all found mall URLs
df = pd.DataFrame({"mall_url": mall_urls})
df.to_csv("Mall_Links_From_SCAI.csv", index=False)
print(f"\n Done! Extracted {len(mall_urls)} mall links across all pages.")