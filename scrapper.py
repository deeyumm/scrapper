from playwright.sync_api import sync_playwright
import time
import csv

all_mall_links = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # You can change to True if you don't want to see the browser
    page = browser.new_page()
    page.set_default_timeout(60000)  # set default timeout to 60 seconds

    for pg in range(1, 5):
        url = f"https://www.scai.in/member-malls/page/{pg}/"
        print(f"\n Visiting page {pg}...")
        page.goto(url)

        # Scroll slowly to load content (especially images & links)
        for _ in range(10):
            page.mouse.wheel(0, 1000)
            time.sleep(0.5)

        try:
            page.wait_for_selector("h3.portfolio-title a", timeout=15000)
            title_links = page.query_selector_all("h3.portfolio-title a")
            print(f" Found {len(title_links)} malls on this page.")

            for link in title_links:
                href = link.get_attribute("href")
                if href:
                    all_mall_links.append(href)

        except Exception as e:
            print(f" Skipping page {pg} due to error: {e}")

    browser.close()

# Save to CSV
csv_file = "Mall_Links_From_SCAI.csv"
with open(csv_file, "w", newline='', encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Mall_Link"])
    for mall_link in all_mall_links:
        writer.writerow([mall_link])

print(f"\n Done! Extracted {len(all_mall_links)} mall links and saved to '{csv_file}'.")