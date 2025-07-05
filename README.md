# Hafta Podcast Scraper

A Python tool for scraping NL Hafta podcast episodes, extracting metadata, and managing episode data.

## Features

- **Link Scraping**: Extract Hafta article links from HTML files
- **Episode ID Extraction**: Use Playwright to extract episode IDs from article pages
- **Episode Data Fetching**: Fetch complete episode metadata from Newslaundry API
- **Audio Metadata Extraction**: Extract audio URLs and metadata for podcast players
- **RSS Feed Generation**: Generate podcast RSS feeds compatible with iTunes and other podcast apps
- **Incremental Updates**: Only fetch new episodes, skip already processed ones
- **Flexible Browser Support**: Works with Brave Browser or default Playwright browsers

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd newslaundry
   ```

2. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright browsers**:
   ```bash
   playwright install
   ```

## Usage

### Main Script

The main script `hafta_scraper.py` provides a unified interface for all operations:

```bash
# Run complete pipeline (recommended)
python hafta_scraper.py

# Run specific actions
python hafta_scraper.py --action scrape-links
python hafta_scraper.py --action extract-ids
python hafta_scraper.py --action fetch-episodes
python hafta_scraper.py --action generate-rss

# Use default browser instead of Brave
python hafta_scraper.py --no-brave

# Scrape links from HTML file
python hafta_scraper.py --action scrape-links --html-file my_html_file.html
```

### Command Line Options

- `--action`: Choose operation (`scrape-links`, `extract-ids`, `fetch-episodes`, `generate-rss`, `full`)
- `--html-file`: Specify HTML file for link scraping (required for `scrape-links` action)
- `--no-brave`: Use default Playwright browser instead of Brave

## File Structure

### Core Files

- `hafta_scraper.py` - Main consolidated script with all functionality
- `requirements.txt` - Python dependencies

### Generated Files

- `hafta_data.json` - **Main consolidated data file** containing all episode data, links, and metadata
- `hafta_feed.xml` - RSS feed for podcast applications



### Removed Files

The following files have been removed and functionality consolidated into `hafta_scraper.py`:
- `scrape_hafta_links.py` - Old link scraping script
- `extract_episode_ids_playwright.py` - Old episode ID extraction
- `fetch_all_hafta_json.py` - Old episode fetching
- `extract_audio_metadata.py` - Old metadata extraction
- `fetch_hafta_json.py` - Old single episode fetching
- `json_to_rss.py` - Old RSS generation (now integrated)

## Workflow

1. **Run Pipeline**: Execute `python hafta_scraper.py` to run the complete pipeline
2. **Use Data**: Access the generated `hafta_data.json` file for your applications

**Note**: If you need to scrape new links from HTML, use:
```bash
python hafta_scraper.py --action scrape-links --html-file your_html_file.html
```

## Data Structure

### hafta_data.json (Main File)
The consolidated data file contains all information in a single, efficient structure:

```json
{
  "episodes": {
    "544": {
      "episode_id": "6868c1f43b5dc9fc2237ce73",
      "title": "Hafta 544: Episode Title",
      "publish_date": "2025-07-05T06:12:08.750Z",
      "summary": "Episode description...",
      "stream_url": "https://feeds.acast.com/.../episode.mp3",
      "duration": 6703.6,
      "cover": "https://assets.pippa.io/.../cover.jpeg",
      "raw_data": { /* Complete API response */ }
    }
  },
  "links": ["https://www.newslaundry.com/...", ...],
  "last_updated": "2025-07-05T23:48:00.000Z"
}
```

## Output Files

### hafta_feed.xml
RSS feed compatible with iTunes, Spotify, and other podcast applications. Contains:
- Episode titles and descriptions
- Audio file URLs
- Publication dates
- Duration information
- Cover images

## Configuration

Edit the configuration variables in `hafta_scraper.py`:

- `BRAVE_PATH`: Path to Brave Browser executable
- `SHOW_ID`: Newslaundry show ID (usually doesn't change)

## Troubleshooting

### Brave Browser Not Found
If Brave is not installed at the default path, either:
- Update `BRAVE_PATH` in the script
- Use `--no-brave` flag to use default browser

### Missing Dependencies
Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Network Issues
The script includes timeouts and retry logic, but network issues may cause some episodes to fail. Check the console output for failed episodes.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is for educational purposes. Please respect Newslaundry's terms of service and copyright. 