import json

# Load the JSON data
with open('hafta_audio_urls.json', 'r', encoding='utf-8') as f:
    episodes = json.load(f)

# Start the OPML content
opml = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<opml version="2.0">',
    '  <head>',
    '    <title>Hafta Episodes</title>',
    '  </head>',
    '  <body>'
]

# Add each episode as an outline
for ep in episodes:
    title = ep.get('title', '').replace('"', '&quot;')
    url = ep.get('streamUrl', '')
    opml.append(f'    <outline text="{title}" type="audio" xmlUrl="{url}"/>')

# Close the OPML tags
opml.extend([
    '  </body>',
    '</opml>'
])

# Write to an OPML file
with open('hafta_episodes.opml', 'w', encoding='utf-8') as f:
    f.write('\n'.join(opml))

print("OPML file created: hafta_episodes.opml") 