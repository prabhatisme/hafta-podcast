#!/usr/bin/env python3
"""
Hafta Podcast Scraper
A consolidated tool for scraping Newslaundry Hafta podcast episodes.
"""

import json
import re
import os
import argparse
import requests
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Optional

# Show configurations
SHOW_CONFIGS = {
    'hafta': {
        'show_id': '5ec3d9497cef7479d2ef4798',
        'data_file': 'hafta_data.json',
        'feed_file': 'hafta_feed.xml',
        'url': 'https://www.newslaundry.com/podcast/nl-hafta',
        'episode_pattern': r'hafta-(\d+)',
        'channel_title': 'Newslaundry Hafta',
        'channel_description': 'Freewheeling discussion on the news of the week from Newslaundry',
        'channel_link': 'https://www.newslaundry.com/podcast/nl-hafta',
        'channel_image': 'https://assets.pippa.io/shows/5ec3d9497cef7479d2ef4798/1751695551059-62a98700-bdf2-4588-911c-4f8f4d930ac3.jpeg',
        'language': 'en-us',
        'min_episode': 541
    },
    'hafta_hindi': {
        'show_id': '5ec247bf1ad9f849b1e3c640',
        'data_file': 'hafta_hindi.json',
        'feed_file': 'hafta_hindi_feed.xml',
        'url': 'https://hindi.newslaundry.com/podcast/nl-charcha',
        'episode_pattern': r'(?:charcha|nl-charcha)(?:-episode)?[-/](\d+)',  # Matches charcha-395, nl-charcha-395, or nl-charcha-episode-396
        'channel_title': 'NL Charcha',
        'channel_description': 'हिंदी पॉडकास्ट जहां हम हफ्तेभर के बवालों और सवालों पर चर्चा करते हैं',
        'channel_link': 'https://hindi.newslaundry.com/podcast/nl-charcha',
        'channel_image': None,  # Will use episode cover or default
        'language': 'hi-in',
        'min_episode': 1
    }
}

class HaftaScraper:
    def __init__(self, show_name: str = 'hafta'):
        """Initialize scraper for a specific show."""
        if show_name not in SHOW_CONFIGS:
            raise ValueError(f"Unknown show: {show_name}. Available: {list(SHOW_CONFIGS.keys())}")
        
        self.config = SHOW_CONFIGS[show_name]
        self.show_name = show_name
        self.data_file = self.config['data_file']
        self.data = self.load_data()
        
    def load_data(self):
        """Load existing data or create new structure."""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {
                'episodes': {},  # hafta_num -> full episode data
                'links': [],     # article links
                'last_updated': None
            }
    
    def save_data(self):
        """Save data to file."""
        self.data['last_updated'] = datetime.now().isoformat()
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2)
        
    def generate_rss_feed(self):
        """Generate RSS feed from episode data."""
        print("Generating RSS feed...")
        
        # Import here to avoid dependency issues
        import xml.etree.ElementTree as ET
        from xml.dom import minidom
        
        def clean_html_tags(text):
            if not text:
                return ""
            clean = re.compile('<.*?>')
            return re.sub(clean, '', text)
        
        def format_duration(seconds):
            if not seconds:
                return "00:00:00"
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        
        # Get episodes with data, sorted by episode number descending
        episodes = [
            (int(num), ep) for num, ep in self.data['episodes'].items() if 'title' in ep
        ]
        episodes = sorted(episodes, key=lambda x: -x[0])
        
        if not episodes:
            print("No episodes with data found. Skipping RSS feed generation.")
            return
        
        # Get reference image URL - use config or first episode cover
        reference_image_url = self.config['channel_image']
        if not reference_image_url and episodes:
            # Try to get from first episode
            first_episode = episodes[0][1]
            reference_image_url = first_episode.get('cover') or ''
        
        # Create RSS root element
        rss = ET.Element('rss')
        rss.set('version', '2.0')
        rss.set('xmlns:itunes', 'http://www.itunes.com/dtds/podcast-1.0.dtd')
        rss.set('xmlns:content', 'http://purl.org/rss/1.0/modules/content/')
        rss.set('xmlns:atom', 'http://www.w3.org/2005/Atom')
        
        # Create channel element
        channel = ET.SubElement(rss, 'channel')
        
        # Channel metadata
        title = ET.SubElement(channel, 'title')
        title.text = self.config['channel_title']
        
        description = ET.SubElement(channel, 'description')
        description.text = self.config['channel_description']
        
        link = ET.SubElement(channel, 'link')
        link.text = self.config['channel_link']
        
        # Channel image (if available)
        if reference_image_url:
            image = ET.SubElement(channel, 'image')
            image_url = ET.SubElement(image, 'url')
            image_url.text = reference_image_url
            image_title = ET.SubElement(image, 'title')
            image_title.text = self.config['channel_title']
            image_link = ET.SubElement(image, 'link')
            image_link.text = self.config['channel_link']
        
        language = ET.SubElement(channel, 'language')
        language.text = self.config['language']
        
        # iTunes specific channel tags
        itunes_author = ET.SubElement(channel, 'itunes:author')
        itunes_author.text = 'Newslaundry'
        
        itunes_category = ET.SubElement(channel, 'itunes:category')
        itunes_category.set('text', 'News')
        
        itunes_explicit = ET.SubElement(channel, 'itunes:explicit')
        itunes_explicit.text = 'false'
        
        itunes_type = ET.SubElement(channel, 'itunes:type')
        itunes_type.text = 'episodic'
        
        # iTunes channel image
        if reference_image_url:
            itunes_image = ET.SubElement(channel, 'itunes:image')
            itunes_image.set('href', reference_image_url)
        
        # Add episodes
        for _, episode in episodes:
            item = ET.SubElement(channel, 'item')
            
            # Episode title
            item_title = ET.SubElement(item, 'title')
            item_title.text = episode.get('title', 'Unknown Episode')
            
            # Episode description
            item_description = ET.SubElement(item, 'description')
            summary = clean_html_tags(episode.get('summary', ''))
            item_description.text = summary
            
            # Link
            item_link = ET.SubElement(item, 'link')
            item_link.text = self.config['channel_link']
            
            # Publication date
            if episode.get('publish_date'):
                try:
                    pub_date = datetime.fromisoformat(episode['publish_date'].replace('Z', '+00:00'))
                    item_pub_date = ET.SubElement(item, 'pubDate')
                    item_pub_date.text = pub_date.strftime('%a, %d %b %Y %H:%M:%S %z')
                except:
                    pass
            
            # Enclosure (audio file)
            if episode.get('stream_url'):
                enclosure = ET.SubElement(item, 'enclosure')
                enclosure.set('url', episode['stream_url'])
                enclosure.set('type', 'audio/mpeg')
                if episode.get('duration'):
                    enclosure.set('length', str(int(episode['duration'] * 1024)))
            
            # iTunes specific episode tags
            itunes_episode_type = ET.SubElement(item, 'itunes:episodeType')
            itunes_episode_type.text = 'full'
            
            if episode.get('duration'):
                itunes_duration = ET.SubElement(item, 'itunes:duration')
                itunes_duration.text = format_duration(episode['duration'])
            
            # Episode image: use episode cover if present, else reference image
            episode_image_url = episode.get('cover') or reference_image_url
            itunes_image = ET.SubElement(item, 'itunes:image')
            itunes_image.set('href', episode_image_url)
            
            # Content encoded (full description with HTML)
            if episode.get('summary'):
                content_encoded = ET.SubElement(item, 'content:encoded')
                content_encoded.text = episode['summary']
        
        # Create pretty XML
        rough_string = ET.tostring(rss, 'unicode')
        reparsed = minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="  ")
        
        # Write to file
        feed_file = self.config['feed_file']
        with open(feed_file, 'w', encoding='utf-8') as f:
            f.write(pretty_xml)
        
        print(f"RSS feed created with {len(episodes)} episodes: {feed_file}")
    
    def run_full_pipeline(self, min_episode: Optional[int] = None):
        """Run full scraping pipeline for the configured show."""
        if min_episode is None:
            min_episode = self.config['min_episode']
        
        show_name_display = self.config['channel_title']
        print(f"Running full {show_name_display} scraping pipeline...")
        podcast_url = self.config['url']
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            page.goto(podcast_url, timeout=60000)
            # Wait for at least one article to appear
            try:
                page.wait_for_selector('article', timeout=15000)
            except Exception:
                print("No <article> elements found after waiting.")
                browser.close()
                return
            html = page.content()
            soup = BeautifulSoup(html, 'lxml')
            new_links = []
            episode_num_re = re.compile(self.config['episode_pattern'])
            for article in soup.find_all('article'):
                if not hasattr(article, 'descendants'):
                    continue
                a = None
                for child in article.descendants:
                    if hasattr(child, 'name') and hasattr(child, 'has_attr'):
                        if child.name == 'a' and child.has_attr('href'):
                            a = child
                            break
                if not a or not hasattr(a, 'has_attr'):
                    continue
                href = a['href']
                if not isinstance(href, str):
                    continue
                match = episode_num_re.search(href)
                if match:
                    episode_num = int(match.group(1))
                    if episode_num >= min_episode:
                        full_url = href
                        if not full_url.startswith('http'):
                            # Extract base URL from config (handles both www and hindi subdomains)
                            base_url = urlparse(self.config['url']).scheme + '://' + urlparse(self.config['url']).netloc
                            full_url = base_url + full_url
                        new_links.append((episode_num, full_url))
            # Sort by episode number descending (latest first)
            new_links = sorted(set(new_links), key=lambda x: -x[0])
            # Compare with existing links
            last_links = self.data.get('links', [])
            if not new_links:
                print(f"No {show_name_display} links found on page.")
                browser.close()
                return
            latest_scraped = last_links[0] if last_links else None
            # Find the first new link (if any)
            new_episode_links = []
            for num, url in new_links:
                if url == latest_scraped:
                    break
                new_episode_links.append((num, url))
            if not new_episode_links:
                print("No new episodes found. Exiting.")
                browser.close()
                return
            print(f"Found {len(new_episode_links)} new episode(s): {[num for num, _ in new_episode_links]}")
            # Prepend new links to links list
            self.data['links'] = [url for _, url in new_episode_links] + last_links
            # For each new episode, visit the link and listen for the API request
            episode_num_re = re.compile(self.config['episode_pattern'])
            show_id = self.config['show_id']
            api_re = re.compile(rf'/acast-rest/shows/{re.escape(show_id)}/episodes/([a-z0-9]+)')
            for episode_num, link in new_episode_links:
                print(f"Processing Episode {episode_num} at {link}")
                episode_id_found = [None]
                api_json = [None]
                episode_page = context.new_page()
                def handle_request(request):
                    url = request.url
                    api_match = api_re.search(url)
                    if api_match and not episode_id_found[0]:
                        episode_id_found[0] = api_match.group(1)
                        # Fetch the API response directly
                        try:
                            resp = requests.get(url)
                            if resp.status_code == 200:
                                api_json[0] = resp.json()
                        except Exception as e:
                            print(f"Error fetching API JSON: {e}")
                episode_page.on('request', handle_request)
                try:
                    episode_page.goto(link, timeout=60000)
                    episode_page.wait_for_timeout(5000)
                except Exception as e:
                    print(f"Error loading {link}: {e}")
                episode_page.close()
                if episode_id_found[0] and api_json[0]:
                    # Ensure episodes dict exists
                    if 'episodes' not in self.data or not isinstance(self.data['episodes'], dict):
                        self.data['episodes'] = {}
                    episode_data = {
                        'episode_id': str(episode_id_found[0]) if episode_id_found[0] is not None else '',
                        'raw_data': api_json[0],
                        'title': api_json[0].get('shows', {}).get('title', ''),
                        'publish_date': api_json[0].get('shows', {}).get('publishDate', ''),
                        'summary': api_json[0].get('shows', {}).get('summary', ''),
                        'stream_url': api_json[0].get('shows', {}).get('streamUrl', ''),
                        'duration': api_json[0].get('shows', {}).get('duration', 0),
                        'cover': api_json[0].get('shows', {}).get('cover', ''),
                    }
                    self.data['episodes'][str(episode_num)] = episode_data  # type: ignore[assignment]
                    print(f"Fetched and added Episode {episode_num}")
                else:
                    print(f"Failed to fetch episode data for Episode {episode_num}")
            browser.close()
            self.save_data()
            self.generate_rss_feed()
            print("Pipeline completed!")
    


def main():
    parser = argparse.ArgumentParser(description='Hafta Podcast Scraper')
    parser.add_argument('--action', choices=['generate-rss', 'full'], 
                       default='full', help='Action to perform')
    parser.add_argument('--show', choices=list(SHOW_CONFIGS.keys()),
                       default='hafta', help='Show to scrape (default: hafta)')
    parser.add_argument('--min-episode', type=int, default=None,
                       help='Minimum episode number to scrape (overrides config default)')
    args = parser.parse_args()
    
    scraper = HaftaScraper(show_name=args.show)
    
    if args.action == 'generate-rss':
        scraper.generate_rss_feed()
    elif args.action == 'full':
        scraper.run_full_pipeline(min_episode=args.min_episode)

if __name__ == "__main__":
    main() 