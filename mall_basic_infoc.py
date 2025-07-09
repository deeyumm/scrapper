from playwright.sync_api import sync_playwright
import csv

input_csv = "Mall_Links_From_SCAI.csv"
output_csv = "Mall_Descriptions_From_SCAI.csv"

def scrape_mall_details(page, url):
    print(f"\nVisiting: {url}")
    try:
        page.goto(url, timeout=60000)
        page.wait_for_selector("div.portfolio-info", timeout=15000)
    except Exception as e:
        print(f"  Skipping due to error: {e}")
        return {}

    data = {
        "Mall URL": url  # Always include the source URL
    }

    #  PART 1: Mall Description Box
    blocks = page.query_selector_all("div.portfolio-info")
    for block in blocks:
        label_elem = block.query_selector("span.info-head.gdlr-title")
        if label_elem:
            label = label_elem.inner_text().strip().rstrip(":")
            full_text = block.inner_text().strip()
            value = full_text.replace(label_elem.inner_text(), "").strip(" :-\n")
            data[label] = value

    #  PART 2: Bold bullet points
    list_items = page.query_selector_all("ul li")
    for item in list_items:
        strong_tag = item.query_selector("strong")
        if strong_tag:
            key = strong_tag.inner_text().strip().rstrip(":")
            full_text = item.inner_text().strip()
            value = full_text.replace(strong_tag.inner_text(), "").strip(" :-\n")
            data[key] = value

    return data

def main():
    with open(input_csv, "r", encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        urls = [row[0] for row in reader]

    all_data = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for url in urls:
            data = scrape_mall_details(page, url)
            if data:
                all_data.append(data)

        browser.close()

    # Write CSV with dynamic headers
    if all_data:
        all_keys = set(k for row in all_data for k in row.keys())
        with open(output_csv, "w", newline='', encoding='utf-8') as f_out:
            writer = csv.DictWriter(f_out, fieldnames=sorted(all_keys))
            writer.writeheader()
            writer.writerows(all_data)

        print(f"\n Done! Scraped {len(all_data)} malls and saved to '{output_csv}'")
    else:
        print("\nNo data scraped.")

if __name__ == "__main__":
    main()