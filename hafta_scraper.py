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

# Configuration
BRAVE_PATH = "/Applications/Brave Browser Beta.app/Contents/MacOS/Brave Browser Beta"
SHOW_ID = "5ec3d9497cef7479d2ef4798"
API_BASE = f"https://www.newslaundry.com/acast-rest/shows/{SHOW_ID}/episodes"

class HaftaScraper:
    def __init__(self):
        self.data_file = 'hafta_data.json'
        self.links_file = 'hafta_links.json'
        
        # Initialize data structure
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
        
    def scrape_links_from_html(self, html_file=None):
        """Extract Hafta article links from HTML file."""
        if not html_file:
            print("No HTML file specified. Please provide a file path.")
            return []
            
        print(f"Scraping Hafta links from {html_file}...")
        
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                html = f.read()
        except FileNotFoundError:
            print(f"HTML file '{html_file}' not found.")
            return []
        
        soup = BeautifulSoup(html, 'lxml')
        pattern = re.compile(r'^click to read Hafta \d+:')
        hafta_links = []
        
        for a in soup.find_all('a', attrs={'aria-label': pattern}):
            href = a.get('href')
            if href:
                hafta_links.append(href)
        
        # Update data structure
        self.data['links'] = hafta_links
        self.save_data()
        
        print(f"Extracted {len(hafta_links)} links")
        return hafta_links
    
    def extract_episode_ids(self, use_brave=True):
        """Extract episode IDs using Playwright."""
        print("Extracting episode IDs using Playwright...")
        
        hafta_links = self.data.get('links', [])
        if not hafta_links:
            print("No links found. Run scrape-links first.")
            return {}
        
        hafta_num_re = re.compile(r'hafta-(\d+)')
        api_re = re.compile(r'/acast-rest/shows/5ec3d9497cef7479d2ef4798/episodes/([a-z0-9]+)')
        
        new_episode_ids = {}
        failures = []
        
        with sync_playwright() as p:
            if use_brave and os.path.exists(BRAVE_PATH):
                browser = p.chromium.launch(executable_path=BRAVE_PATH, headless=True)
            else:
                browser = p.chromium.launch(headless=True)
            
            context = browser.new_context()
            
            for link in hafta_links:
                match = hafta_num_re.search(link)
                if not match:
                    print(f"Could not extract Hafta number from: {link}")
                    failures.append(link)
                    continue
                
                hafta_num = match.group(1)
                
                # Skip if already processed
                if hafta_num in self.data['episodes']:
                    print(f"Hafta {hafta_num} already processed. Skipping.")
                    continue
                
                episode_id_found = [None]
                page = context.new_page()
                
                try:
                    def handle_request(request):
                        url = request.url
                        api_match = api_re.search(url)
                        if api_match:
                            episode_id_found[0] = api_match.group(1)
                    
                    page.on('request', handle_request)
                    page.goto(link, timeout=60000)
                    page.wait_for_timeout(5000)
                except Exception as e:
                    print(f"Error loading {link}: {e}")
                    failures.append(link)
                
                page.close()
                
                if episode_id_found[0]:
                    new_episode_ids[hafta_num] = episode_id_found[0]
                    print(f"Hafta {hafta_num}: {episode_id_found[0]}")
                else:
                    print(f"No episode_id found for Hafta {hafta_num}")
                    failures.append(link)
            
            browser.close()
        
        print(f"Found {len(new_episode_ids)} new episode IDs")
        if failures:
            print(f"Failed to process {len(failures)} links")
        
        return new_episode_ids
    
    def fetch_episodes(self):
        """Fetch episode data for new episode IDs."""
        print("Fetching episode data...")
        
        # Get episode IDs that need fetching
        episode_ids = {}
        for hafta_num, episode_data in self.data['episodes'].items():
            if 'raw_data' not in episode_data:
                episode_ids[hafta_num] = episode_data.get('episode_id')
        
        if not episode_ids:
            print("No new episodes to fetch.")
            return
        
        new_episodes = 0
        failures = []
        
        for hafta_num, episode_id in episode_ids.items():
            if not episode_id:
                print(f"No episode_id for Hafta {hafta_num}")
                failures.append(hafta_num)
                continue
            
            api_url = f"{API_BASE}/{episode_id}"
            try:
                response = requests.get(api_url)
                if response.status_code == 200:
                    episode_json = response.json()
                    
                    # Update episode data
                    if hafta_num not in self.data['episodes']:
                        self.data['episodes'][hafta_num] = {}
                    
                    self.data['episodes'][hafta_num].update({
                        'episode_id': episode_id,
                        'raw_data': episode_json,
                        'title': episode_json.get('shows', {}).get('title'),
                        'publish_date': episode_json.get('shows', {}).get('publishDate'),
                        'summary': episode_json.get('shows', {}).get('summary'),
                        'stream_url': episode_json.get('shows', {}).get('streamUrl'),
                        'duration': episode_json.get('shows', {}).get('duration'),
                        'cover': episode_json.get('shows', {}).get('cover'),
                    })
                    
                    print(f"Fetched and added Hafta {hafta_num}")
                    new_episodes += 1
                else:
                    print(f"Failed to fetch JSON for Hafta {hafta_num}: {response.status_code}")
                    failures.append(hafta_num)
            except Exception as e:
                print(f"Error fetching {api_url}: {e}")
                failures.append(hafta_num)
        
        self.save_data()
        print(f"\nSummary: {new_episodes} new episodes fetched, {len(failures)} failed")
    
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
        
        # Get episodes with data
        episodes = [ep for ep in self.data['episodes'].values() if 'title' in ep]
        
        if not episodes:
            print("No episodes with data found. Run fetch-episodes first.")
            return
        
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
        
        # Add episodes
        for episode in episodes:
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
            
            if episode.get('cover'):
                itunes_image = ET.SubElement(item, 'itunes:image')
                itunes_image.set('href', episode['cover'])
            
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
    
    def run_full_pipeline(self):
        """Run the complete scraping pipeline."""
        print("Running full Hafta scraping pipeline...")
        
        # Step 1: Extract episode IDs (if links exist)
        new_ids = self.extract_episode_ids()
        
        # Step 2: Fetch episodes
        if new_ids:
            self.fetch_episodes()
        
        # Step 3: Generate RSS feed
        self.generate_rss_feed()
        
        print("Pipeline completed successfully!")
    


def main():
    parser = argparse.ArgumentParser(description='Hafta Podcast Scraper')
    parser.add_argument('--action', choices=['scrape-links', 'extract-ids', 'fetch-episodes', 'generate-rss', 'full'], 
                       default='full', help='Action to perform')
    parser.add_argument('--html-file', help='HTML file to scrape links from (required for scrape-links action)')
    parser.add_argument('--no-brave', action='store_true', help='Use default browser instead of Brave')
    
    args = parser.parse_args()
    
    scraper = HaftaScraper()
    
    if args.action == 'scrape-links':
        if not args.html_file:
            print("Error: --html-file is required for scrape-links action")
            return
        scraper.scrape_links_from_html(args.html_file)
    elif args.action == 'extract-ids':
        scraper.extract_episode_ids(use_brave=not args.no_brave)
    elif args.action == 'fetch-episodes':
        scraper.fetch_episodes()
    elif args.action == 'generate-rss':
        scraper.generate_rss_feed()
    elif args.action == 'full':
        scraper.run_full_pipeline()

if __name__ == "__main__":
    main() 