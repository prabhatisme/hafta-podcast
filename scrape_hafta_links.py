import json
import re
from bs4 import BeautifulSoup

# Load the HTML file
with open('element.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'lxml')

# Regex pattern for aria-label
pattern = re.compile(r'^click to read Hafta \d+:')

hafta_links = []

# Find all <a> tags with matching aria-label
for a in soup.find_all('a', attrs={'aria-label': pattern}):
    href = a.get('href')
    if href:
        hafta_links.append(href)

# Store in object
result = {"hafta_links": hafta_links}

# Write to JSON file
with open('hafta_links.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=2)

print(f"Extracted {len(hafta_links)} links.") 