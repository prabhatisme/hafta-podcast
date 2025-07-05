import json

# Load all episode data
with open('hafta_episodes.json', 'r', encoding='utf-8') as f:
    episodes = json.load(f)

output = []

for hafta_num, data in episodes.items():
    show = data.get('shows', {})
    output.append({
        'hafta_num': hafta_num,
        'title': show.get('title'),
        'publishDate': show.get('publishDate'),
        'summary': show.get('summary'),
        'streamUrl': show.get('streamUrl'),
        'duration': show.get('duration'),
        'cover': show.get('cover'),
    })

with open('hafta_audio_urls.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print(f"Extracted metadata for {len(output)} episodes to hafta_audio_urls.json") 