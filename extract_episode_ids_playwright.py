import json
import re
from playwright.sync_api import sync_playwright

# Path to Brave browser on macOS
BRAVE_PATH = "/Applications/Brave Browser Beta.app/Contents/MacOS/Brave Browser Beta"

# Load the hafta links
with open('hafta_links.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
hafta_links = data['hafta_links']

# Regex to extract Hafta number from the URL (e.g., hafta-544)
hafta_num_re = re.compile(r'hafta-(\d+)')
# Regex to match the API call and extract episode_id
api_re = re.compile(r'/acast-rest/shows/5ec3d9497cef7479d2ef4798/episodes/([a-z0-9]+)')

hafta_to_episode_id = {}
failures = []

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=BRAVE_PATH, headless=True)
    context = browser.new_context()
    for link in hafta_links:
        match = hafta_num_re.search(link)
        if not match:
            print(f"Could not extract Hafta number from: {link}")
            failures.append(link)
            continue
        hafta_num = match.group(1)
        episode_id_found = [None]  # Use a list for mutability
        page = context.new_page()
        try:
            def handle_request(request):
                url = request.url
                api_match = api_re.search(url)
                if api_match:
                    episode_id_found[0] = api_match.group(1)
            page.on('request', handle_request)
            page.goto(link, timeout=60000)
            page.wait_for_timeout(5000)  # Wait for network requests
        except Exception as e:
            print(f"Error loading {link}: {e}")
            failures.append(link)
        page.close()
        if episode_id_found[0]:
            hafta_to_episode_id[hafta_num] = episode_id_found[0]
            print(f"Hafta {hafta_num}: {episode_id_found[0]}")
        else:
            print(f"No episode_id found for Hafta {hafta_num} ({link})")
            failures.append(link)
    browser.close()

# Save the mapping
with open('hafta_to_episode_id.json', 'w', encoding='utf-8') as f:
    json.dump(hafta_to_episode_id, f, indent=2)

if failures:
    print("Some links could not be processed:")
    for fail in failures:
        print(fail)
else:
    print("All episode IDs extracted successfully.") 