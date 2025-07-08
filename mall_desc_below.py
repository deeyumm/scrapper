from bs4 import BeautifulSoup
import csv
from playwright.sync_api import sync_playwright
import time

# Input/output
input_csv = "Mall_Links_From_SCAII.csv"
output_csv = "Mall_Details_Only.csv"

# Read all URLs
with open(input_csv, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    urls = [row["Mall_Link"] for row in reader]

data = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    for idx, url in enumerate(urls):
        print(f"\n Scraping ({idx+1}/{len(urls)}): {url}")
        try:
            page.goto(url, timeout=60000)
            page.wait_for_timeout(3000)
            html = page.content()
            soup = BeautifulSoup(html, "html.parser")

            section_data = {}

            # Find the <h3> that contains "DETAILS OF MALL"
            details_header = soup.find("h3", string=lambda t: t and "DETAILS OF MALL" in t.upper())
            if details_header:
                # Get next <ul> element after this header
                ul = details_header.find_next("ul")
                if ul:
                    for li in ul.find_all("li"):
                        strong = li.find("strong")
                        if strong:
                            key = strong.text.strip().replace(":", "")
                            value = li.get_text().replace(strong.text, "").strip()
                            section_data[key] = value
            
            # Add URL for reference
            section_data["Source URL"] = url
            data.append(section_data)

        except Exception as e:
            print(f" Error scraping {url}: {e}")
            continue

    browser.close()

# Get all unique keys
all_keys = sorted({key for row in data for key in row})

# Save to CSV
with open(output_csv, "w", newline='', encoding='utf-8') as f_out:
    writer = csv.DictWriter(f_out, fieldnames=all_keys)
    writer.writeheader()
    writer.writerows(data)

print(f"\n Done! Saved mall detail section to '{output_csv}'")