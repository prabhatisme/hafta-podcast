# Hafta Podcast Scraper

A Python tool for scraping NL Hafta podcast episodes, extracting metadata, and generating an RSS feed.

## Features

- **Automated Scraping**: Uses Playwright to visit the live Hafta podcast page and detect new episodes automatically
- **Episode Data Extraction**: Fetches complete episode metadata from Newslaundry's API
- **RSS Feed Generation**: Generates a podcast RSS feed compatible with iTunes and other podcast apps
- **Incremental Updates**: Only fetches and processes new episodes (>= 541), skipping already processed ones
- **Fully Automated**: No manual HTML downloads or intermediate steps required

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd hafta-podcast
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

4. **Install Playwright browser**:
   ```bash
   python -m playwright install chromium --only-shell
   ```

## Usage

### Main Script

The main script `hafta_scraper.py` provides a unified interface for all operations:

```bash
# Run complete pipeline (scrape new episodes and generate RSS)
python hafta_scraper.py
# or
python hafta_scraper.py --action full

# Only regenerate RSS feed from existing data
python hafta_scraper.py --action generate-rss
```

### Command Line Options

- `--action`: Choose operation (`generate-rss`, `full`)

## File Structure

- `hafta_scraper.py` - Main script
- `requirements.txt` - Python dependencies
- `hafta_data.json` - Main data file (auto-generated)
- `hafta_feed.xml` - RSS feed (auto-generated)

## GitHub Actions Automation

This project includes a GitHub Actions workflow (`.github/workflows/hafta_scraper.yml`) that runs the scraper weekly, updates the data and RSS feed, and commits changes automatically.

## Data Structure

### hafta_data.json

```json
{
  "episodes": {
    "545": { ... },
    "544": { ... },
    ...
  },
  "links": [
    "https://www.newslaundry.com/2025/07/12/hafta-545-bihar-electoral-revision-dalai-lama-and-the-future-of-tibetan-movement",
    ...
  ],
  "last_updated": "2025-07-12T18:38:36.322467"
}
```

### hafta_feed.xml

- Standard RSS 2.0 feed with all episode metadata, sorted newest first.

## Troubleshooting

- Ensure all dependencies are installed:
  ```bash
  pip install -r requirements.txt
  ```
- Ensure Playwright browser is installed:
  ```bash
  python -m playwright install chromium --only-shell
  ```
- If you encounter issues, try deleting `hafta_data.json` and re-running the full pipeline.

### RSS Feed Links

- [NL Hafta English](https://raw.githubusercontent.com/prabhatisme/hafta-podcast/refs/heads/main/hafta_feed.xml)

- [NL Hafta Hindi](https://www.newslaundry.com/podcast-rss/getFeed/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJtZW1iZXJJZCI6InlvZ2VzaHdhckBvdXRsb29rLmNvbSIsInN1YnNjcmlwdGlvbk5hbWUiOiJHYW1lIENoYW5nZXIiLCJleHBpcnlEYXRlIjoiNjU3LjY1MDQwNTU3ODcwMzdkIiwic2hvd0lkIjoiNWVjMjQ3YmYxYWQ5Zjg0OWIxZTNjNjQwIiwiaWF0IjoxNzA0NzAyMjA0LCJleHAiOjE3NjE1MjMxOTl9.xaAhKGIvz099K7u3KGR0lzeMdrATFAAlo-jrj2dfFck)

## License

This project is for educational purposes. Please respect Newslaundry's terms of service and copyright. 