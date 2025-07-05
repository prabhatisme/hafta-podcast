import json
import requests

# Load the hafta links
with open('hafta_links.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Take the first link as an example
hafta_link = data['hafta_links'][0]

# For demo: Use the known episode_id for Hafta 544
# In a real scenario, you would extract this dynamically from the article page
# or have a mapping from the article link to the episode_id
# For Hafta 544:
episode_id = "6868c1f43b5dc9fc2237ce73"

api_url = f"https://www.newslaundry.com/acast-rest/shows/5ec3d9497cef7479d2ef4798/episodes/{episode_id}"

# Fetch the JSON data
response = requests.get(api_url)
if response.status_code == 200:
    episode_json = response.json()
    # Save the JSON
    with open('hafta_episode.json', 'w', encoding='utf-8') as f:
        json.dump(episode_json, f, indent=2)
    print("Episode JSON saved to hafta_episode.json")
else:
    print(f"Failed to fetch JSON: {response.status_code}") 