import json
from datetime import datetime
import requests

# Helper to get file size for enclosure
def get_file_size(url):
    try:
        response = requests.head(url, allow_redirects=True, timeout=10)
        size = response.headers.get('Content-Length')
        if size and size.isdigit():
            return int(size)
    except Exception:
        pass
    return 1  # fallback to 1 if unknown

# Load the JSON data
with open('hafta_audio_urls.json', 'r', encoding='utf-8') as f:
    episodes = json.load(f)

# RSS feed header with namespaces and channel metadata
rss = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<rss xmlns:dc="http://purl.org/dc/elements/1.1/"',
    '    xmlns:content="http://purl.org/rss/1.0/modules/content/"',
    '    xmlns:atom="http://www.w3.org/2005/Atom" version="2.0"',
    '    xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">',
    '  <channel>',
    '    <title><![CDATA[Hafta Podcast]]></title>',
    '    <description><![CDATA[All Hafta episodes]]></description>',
    '    <link>https://www.newslaundry.com/hafta</link>',
    '    <image>',
    '      <url>https://assets.pippa.io/shows/5ec3d9497cef7479d2ef4798/1751695551059-62a98700-bdf2-4588-911c-4f8f4d930ac3.jpeg</url>',
    '      <title>Hafta Podcast</title>',
    '      <link>https://www.newslaundry.com/hafta</link>',
    '    </image>',
    '    <generator>Python Script</generator>',
    '    <lastBuildDate>{}</lastBuildDate>'.format(datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')),
    '    <atom:link href="https://www.newslaundry.com/hafta" rel="self" type="application/rss+xml" />',
    '    <pubDate>Mon, 18 May 2020 08:30:55 GMT</pubDate>',
    '    <copyright><![CDATA[All rights reserved]]></copyright>',
    '    <language><![CDATA[en]]></language>',
    '    <managingEditor>subscription@newslaundry.com (Newslaundry)</managingEditor>',
    '    <webMaster>subscription@newslaundry.com (Newslaundry)</webMaster>',
    '    <category><![CDATA[News]]></category>',
    '    <itunes:author>Newslaundry.com</itunes:author>',
    '    <itunes:summary><![CDATA[All Hafta episodes]]></itunes:summary>',
    '    <itunes:owner>',
    '      <itunes:name>Newslaundry</itunes:name>',
    '      <itunes:email>subscription@newslaundry.com</itunes:email>',
    '    </itunes:owner>',
    '    <itunes:explicit>false</itunes:explicit>',
    '    <itunes:image href="https://assets.pippa.io/shows/5ec3d9497cef7479d2ef4798/1751695551059-62a98700-bdf2-4588-911c-4f8f4d930ac3.jpeg" />',
    '    <itunes:category text="News" />'
]

# Add each episode as an item
for ep in episodes:
    title = ep.get('title', '').replace(']]>', ']]]]><![CDATA[>')
    pub_date = ep.get('publishDate', '')
    # Convert ISO date to RFC 2822 for RSS
    try:
        dt = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
        pub_date_rss = dt.strftime('%a, %d %b %Y %H:%M:%S GMT')
    except Exception:
        pub_date_rss = pub_date
    summary = ep.get('summary', '').replace(']]>', ']]]]><![CDATA[>')
    url = ep.get('streamUrl', '')
    # Remove HTML from summary for itunes:summary
    import re
    summary_text = re.sub('<[^<]+?>', '', summary)
    duration = ep.get('duration', '')
    cover = ep.get('cover', '')
    # Get file size for enclosure
    enclosure_length = get_file_size(url)
    # Format duration as HH:MM:SS if possible
    try:
        dur = float(duration)
        hours = int(dur // 3600)
        minutes = int((dur % 3600) // 60)
        seconds = int(dur % 60)
        duration_str = f"{hours:02}:{minutes:02}:{seconds:02}"
    except Exception:
        duration_str = str(duration)
    rss.append('    <item>')
    rss.append(f'      <title><![CDATA[{title}]]></title>')
    rss.append(f'      <description><![CDATA[{summary}]]></description>')
    rss.append(f'      <guid isPermaLink="false">{url.split("/")[-1].split(".")[0]}</guid>')
    rss.append('      <dc:creator><![CDATA[Newslaundry]]></dc:creator>')
    rss.append(f'      <pubDate>{pub_date_rss}</pubDate>')
    rss.append(f'      <enclosure url="{url}" type="audio/mpeg" length="{enclosure_length}"/>')
    rss.append('      <itunes:author>Newslaundry</itunes:author>')
    rss.append(f'      <itunes:summary><![CDATA[{summary_text}]]></itunes:summary>')
    rss.append('      <itunes:explicit>false</itunes:explicit>')
    rss.append(f'      <itunes:duration>{duration_str}</itunes:duration>')
    if cover:
        rss.append(f'      <itunes:image href="{cover}" />')
    rss.append('    </item>')

# Close the RSS feed
rss.extend([
    '  </channel>',
    '</rss>'
])

# Write to an RSS file
with open('hafta_feed.xml', 'w', encoding='utf-8') as f:
    f.write('\n'.join(rss))

print("RSS feed created: hafta_feed.xml") 