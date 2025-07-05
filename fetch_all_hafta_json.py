import json
import requests
import os

# Load the mapping from Hafta number to episode_id
with open('hafta_to_episode_id.json', 'r', encoding='utf-8') as f:
    hafta_to_episode_id = json.load(f)

# Load existing episodes if the file exists
episodes_file = 'hafta_episodes.json'
if os.path.exists(episodes_file):
    with open(episodes_file, 'r', encoding='utf-8') as f:
        hafta_episodes = json.load(f)
else:
    hafta_episodes = {}

new_episodes = 0
skipped = 0
failures = []

for hafta_num, episode_id in hafta_to_episode_id.items():
    if hafta_num in hafta_episodes:
        print(f"Hafta {hafta_num} already fetched. Skipping.")
        skipped += 1
        continue
    api_url = f"https://www.newslaundry.com/acast-rest/shows/5ec3d9497cef7479d2ef4798/episodes/{episode_id}"
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            episode_json = response.json()
            hafta_episodes[hafta_num] = episode_json
            print(f"Fetched and added Hafta {hafta_num}")
            new_episodes += 1
        else:
            print(f"Failed to fetch JSON for Hafta {hafta_num}: {response.status_code}")
            failures.append(hafta_num)
    except Exception as e:
        print(f"Error fetching {api_url}: {e}")
        failures.append(hafta_num)

# Save all episodes to one file
with open(episodes_file, 'w', encoding='utf-8') as f:
    json.dump(hafta_episodes, f, indent=2)

print(f"\nSummary:")
print(f"New episodes fetched: {new_episodes}")
print(f"Episodes skipped (already present): {skipped}")
if failures:
    print(f"Failures: {len(failures)} -> {failures}")
else:
    print("No failures.") 