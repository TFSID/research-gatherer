# Research Gatherer

A powerful deep research tool that combines multiple search engines with AI-powered content parsing for comprehensive source gathering and organization.

## Features

### 🔍 Multi-Engine Search
- **14 Search Engines**: Google, Bing, Yahoo, Yandex, DuckDuckGo, and more
- **Parallel Processing**: Simultaneous searches across all engines
- **Deduplication**: Automatic removal of duplicate links
- **Keyword Lists**: Support for batch keyword processing

### 📄 AI-Powered Parsing
- **Jina AI Integration**: Converts web pages to clean markdown
- **Smart Titles**: Automatic title extraction and filename generation
- **Metadata**: Adds source URL, parse date, and domain information
- **Rate Limiting**: Built-in delays to respect API limits

### 📁 Intelligent Organization
- **Auto-Categorization**: Organizes content by domain
- **Duplicate Handling**: Automatic filename conflict resolution
- **Summary Reports**: Generates research statistics and structure
- **Failed Link Tracking**: Logs URLs that failed to parse

## Installation

```bash
# Clone or navigate to the tool directory
cd tools/research-gatherer

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Basic Workflow

#### 1. Search and Collect Links

```bash
# Single keyword
python research_gatherer.py -k "artificial intelligence" -o ai_research

# Multiple keywords from file
python research_gatherer.py -l keywords.txt -o research_output
```

#### 2. Parse Collected Links

```bash
# Parse all collected links
python research_gatherer.py --parse-only -o research_output

# Parse with filtering
python research_gatherer.py --parse-only --filter "github" -o research_output
```

#### 3. Full Automated Workflow

```bash
# Search and automatically parse
python research_gatherer.py -k "machine learning" --auto-parse -o ml_research
```

### Advanced Options

```bash
# Debug mode for troubleshooting
python research_gatherer.py -k "cybersecurity" -d --auto-parse

# Process keyword list with auto-parse
python research_gatherer.py -l research_topics.txt --auto-parse -o deep_research
```

## Keyword List Format

Create a text file with one keyword per line:

```text
# research_topics.txt
machine learning algorithms
natural language processing
computer vision
deep learning frameworks
# Lines starting with # are ignored
```

## Output Structure

```
research_output/
├── collected_links.txt          # All collected URLs
├── failed_urls.txt              # URLs that failed to parse
├── RESEARCH_SUMMARY.md          # Statistics and overview
└── parsed_content/              # Organized markdown files
    ├── github.com/              # Categorized by domain
    │   ├── document1.md
    │   └── document2.md
    ├── stackoverflow.com/
    │   └── article.md
    └── medium.com/
        └── blog_post.md
```

## Document Format

Each parsed document includes metadata:

```markdown
---
source: https://example.com/article
parsed_date: 2026-02-05 10:00:00
domain: example.com
---

# Article Title

Content here...
```

## Workflow Examples

### Research Project Setup

```bash
# 1. Create keywords file
echo "quantum computing
quantum algorithms
quantum cryptography" > quantum_keywords.txt

# 2. Run full research gathering
python research_gatherer.py -l quantum_keywords.txt --auto-parse -o quantum_research

# 3. Review summary
cat quantum_research/RESEARCH_SUMMARY.md
```

### Incremental Research

```bash
# Day 1: Collect links
python research_gatherer.py -k "blockchain technology" -o blockchain_research

# Day 2: Add more keywords
python research_gatherer.py -k "smart contracts" -o blockchain_research

# Day 3: Parse everything
python research_gatherer.py --parse-only -o blockchain_research
```

### Targeted Parsing

```bash
# Collect links from multiple sources
python research_gatherer.py -l topics.txt -o research

# Parse only GitHub links
python research_gatherer.py --parse-only --filter "github.com" -o research
```

## Command Reference

| Option | Short | Description |
|--------|-------|-------------|
| `--keyword` | `-k` | Single keyword to search |
| `--keyword-list` | `-l` | File with keywords (one per line) |
| `--output` | `-o` | Output directory (default: research_output) |
| `--parse-only` | | Parse previously collected links only |
| `--auto-parse` | | Automatically parse after collecting |
| `--filter` | | Filter links by keyword when parsing |
| `--debug` | `-d` | Enable debug logging |

## Search Engines Included

1. Google
2. Bing
3. Yahoo
4. Yandex
5. DuckDuckGo
6. Ask.com
7. AOL
8. Lycos
9. Mojeek
10. MetaGer
11. Gigablast
12. Seznam
13. Naver
14. And more...

## Tips & Best Practices

### Efficient Research

1. **Start Broad**: Use general keywords first
2. **Refine**: Use `--filter` to focus on specific domains
3. **Batch Process**: Use keyword lists for large research projects
4. **Review Links**: Check `collected_links.txt` before parsing

### Rate Limiting

- Built-in 0.5s delay between Jina API calls
- Search engines use parallel processing for speed
- For large batches, consider running overnight

### Organization

- Use descriptive output directory names
- Keep keyword files for reproducibility
- Back up `collected_links.txt` for re-parsing

### Troubleshooting

```bash
# Enable debug mode to see detailed logs
python research_gatherer.py -k "test" -d

# Check failed URLs
cat research_output/failed_urls.txt

# Re-parse failed URLs after fixing issues
# (manually edit collected_links.txt to only include failed URLs)
python research_gatherer.py --parse-only -o retry_output
```

## Use Cases

### Academic Research
```bash
python research_gatherer.py -l academic_topics.txt --auto-parse -o literature_review
```

### Competitive Intelligence
```bash
python research_gatherer.py -k "competitor product features" --auto-parse -o competitor_analysis
```

### Technology Monitoring
```bash
python research_gatherer.py -l tech_trends.txt --auto-parse -o tech_watch
```

### Content Curation
```bash
python research_gatherer.py -k "industry news" --filter "techcrunch" --auto-parse
```

## Dependencies

- `requests`: HTTP library for API calls
- `beautifulsoup4`: HTML parsing (for search engines)
- `lxml`: XML/HTML parser
- `selenium`: Browser automation (optional for some engines)

See `requirements.txt` for complete list.

## Notes

- **Jina AI**: Uses free Jina Reader API (https://r.jina.ai/)
- **Rate Limits**: Respects service rate limits automatically
- **Privacy**: All processing is local except Jina API calls
- **Legal**: Ensure compliance with website ToS and robots.txt

## License

This tool combines features from:
- pyse (Search Engine Tool)
- jina-parser (Jina AI Parser)

For research and educational purposes.

## Support

For issues or questions, review:
1. Debug logs (`-d` flag)
2. `failed_urls.txt` for parsing errors
3. Engine-specific errors in console output
