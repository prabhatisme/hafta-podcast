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
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from datetime import datetime
from bs4.element import Tag

# Configuration
SHOW_ID = "5ec3d9497cef7479d2ef4798"
API_BASE = f"https://www.newslaundry.com/acast-rest/shows/{SHOW_ID}/episodes"

class HaftaScraper:
    def __init__(self):
        self.data_file = 'hafta_data.json'
        # self.links_file = 'hafta_links.json'  # Remove unused attribute
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
        import re
        
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
        
        # Reference image URL from reference.xml
        reference_image_url = "https://assets.pippa.io/shows/5ec3d9497cef7479d2ef4798/1751695551059-62a98700-bdf2-4588-911c-4f8f4d930ac3.jpeg"
        
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
        title.text = 'Newslaundry Hafta'
        
        description = ET.SubElement(channel, 'description')
        description.text = 'Freewheeling discussion on the news of the week from Newslaundry'
        
        link = ET.SubElement(channel, 'link')
        link.text = 'https://www.newslaundry.com/podcast/nl-hafta'
        
        # Channel image (reference)
        image = ET.SubElement(channel, 'image')
        image_url = ET.SubElement(image, 'url')
        image_url.text = reference_image_url
        image_title = ET.SubElement(image, 'title')
        image_title.text = 'Hafta Podcast'
        image_link = ET.SubElement(image, 'link')
        image_link.text = 'https://www.newslaundry.com/podcast/nl-hafta'
        
        language = ET.SubElement(channel, 'language')
        language.text = 'en-us'
        
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
            item_link.text = f"https://www.newslaundry.com/podcast/nl-hafta"
            
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
        with open('hafta_feed.xml', 'w', encoding='utf-8') as f:
            f.write(pretty_xml)
        
        print(f"RSS feed created with {len(episodes)} episodes: hafta_feed.xml")
    
    def run_full_pipeline(self, min_hafta=541):
        print("Running full Hafta scraping pipeline...")
        hafta_url = "https://www.newslaundry.com/podcast/nl-hafta"
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            page.goto(hafta_url, timeout=60000)
            # Wait for at least one article to appear
            try:
                page.wait_for_selector('article', timeout=15000)
            except Exception:
                print("No <article> elements found after waiting.")
                browser.close()
                return
            html = page.content()
            soup = BeautifulSoup(html, 'lxml')
            from bs4.element import Tag
            new_links = []
            hafta_num_re = re.compile(r"hafta-(\d+)")
            for article in soup.find_all('article'):
                if not isinstance(article, Tag):
                    continue
                a = None
                for child in article.descendants:
                    if isinstance(child, Tag) and child.name == 'a' and child.has_attr('href'):
                        a = child
                        break
                if not a or not isinstance(a, Tag):
                    continue
                href = a['href']
                if not isinstance(href, str):
                    continue
                match = hafta_num_re.search(href)
                if match:
                    hafta_num = int(match.group(1))
                    if hafta_num >= min_hafta:
                        full_url = href
                        if not full_url.startswith('http'):
                            full_url = 'https://www.newslaundry.com' + full_url
                        new_links.append((hafta_num, full_url))
            # Sort by hafta number descending (latest first)
            new_links = sorted(set(new_links), key=lambda x: -x[0])
            # Compare with existing links
            last_links = self.data.get('links', [])
            if not new_links:
                print("No Hafta links found on page.")
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
            hafta_num_re = re.compile(r'hafta-(\d+)')
            api_re = re.compile(r'/acast-rest/shows/5ec3d9497cef7479d2ef4798/episodes/([a-z0-9]+)')
            for hafta_num, link in new_episode_links:
                print(f"Processing Hafta {hafta_num} at {link}")
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
                    self.data['episodes'][str(hafta_num)] = episode_data  # type: ignore[assignment]
                    print(f"Fetched and added Hafta {hafta_num}")
                else:
                    print(f"Failed to fetch episode data for Hafta {hafta_num}")
            browser.close()
            self.save_data()
            self.generate_rss_feed()
            print("Pipeline completed!")
    


def main():
    parser = argparse.ArgumentParser(description='Hafta Podcast Scraper')
    parser.add_argument('--action', choices=['generate-rss', 'full'], 
                       default='full', help='Action to perform')
    args = parser.parse_args()
    
    scraper = HaftaScraper()
    
    if args.action == 'generate-rss':
        scraper.generate_rss_feed()
    elif args.action == 'full':
        scraper.run_full_pipeline()

if __name__ == "__main__":
    main() 