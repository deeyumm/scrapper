import csv
import requests
from bs4 import BeautifulSoup

input_csv = "Mall_Links_From_SCAI.csv"
output_csv = "Mall_Details_Extracted.csv"

all_data = []

with open(input_csv, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        url = row["Mall_Link"]
        print(f"Scraping: {url}")
        try:
            response = requests.get(url, timeout=30)
            soup = BeautifulSoup(response.text, "html.parser")

            section_data = {"Mall_Link": url}  # Initialize row with the link

            # Find the <h3> that contains "DETAILS OF MALL"
            details_header = soup.find("h3", string=lambda t: t and "DETAILS OF MALL" in t.upper())
            if details_header:
                # Get next <ul> element after this header
                ul = details_header.find_next("ul")
                if ul:
                    for li in ul.find_all("li"):
                        # Extract all <strong> tags in the <li>
                        strong_tags = li.find_all("strong")
                        for strong in strong_tags:
                            key = strong.text.strip().replace(":", "")
                            value = ""
                            
                            # Get the text immediately after the <strong> tag
                            next_part = strong.next_sibling
                            if next_part and isinstance(next_part, str):
                                value = next_part.strip()
                            else:
                                # fallback method
                                li_text = li.get_text(separator=" ").strip()
                                strong_text = strong.text.strip()
                                after_strong = li_text.split(strong_text, 1)[-1].strip()
                                value = after_strong.split("  ")[0].strip()
                            
                            section_data[key] = value

            all_data.append(section_data)

        except Exception as e:
            print(f"Failed to process {url}: {e}")

# Determine all unique column names
all_columns = set()
for row in all_data:
    all_columns.update(row.keys())
all_columns = sorted(all_columns)

# Save to output CSV
with open(output_csv, "w", newline='', encoding="utf-8") as f_out:
    writer = csv.DictWriter(f_out, fieldnames=all_columns)
    writer.writeheader()
    for row in all_data:
        writer.writerow(row)

print(f"\n Done! Extracted details for {len(all_data)} malls and saved to '{output_csv}'")
