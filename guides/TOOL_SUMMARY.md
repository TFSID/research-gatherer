# Research Gatherer - Tool Summary

## Overview

**Research Gatherer** is a comprehensive deep research tool that combines the power of multiple search engines with AI-driven content parsing to streamline the research process.

## Key Features

### 🔍 Multi-Engine Search System
- **14 Search Engines** working in parallel
- **Automatic Deduplication** of results
- **Keyword List Support** for batch processing
- **Threaded Execution** for maximum speed

### 📄 AI-Powered Content Parsing
- **Jina AI Integration** for clean markdown conversion
- **Automatic Title Extraction** from content
- **Smart Filename Generation** from titles
- **Metadata Enrichment** (source, date, domain)

### 📁 Intelligent Organization
- **Domain-Based Categorization** for easy navigation
- **Duplicate File Handling** with auto-numbering
- **Summary Report Generation** with statistics
- **Failed Link Tracking** for troubleshooting

## Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                    Research Gatherer Workflow                │
└─────────────────────────────────────────────────────────────┘

1. INPUT
   ├── Single Keyword (-k "keyword")
   └── Keyword List (-l keywords.txt)
          │
          ▼
2. SEARCH & COLLECT
   ├── Launch 14 search engines in parallel
   ├── Collect all URLs from results
   ├── Deduplicate against existing links
   └── Save to collected_links.txt
          │
          ▼
3. PARSE & CONVERT
   ├── Read URLs from collected_links.txt
   ├── Send to Jina AI Reader API
   ├── Convert each page to markdown
   ├── Extract title and metadata
   └── Handle rate limiting
          │
          ▼
4. ORGANIZE & SAVE
   ├── Extract domain from URL
   ├── Create domain-specific folders
   ├── Generate clean filenames from titles
   ├── Add metadata headers
   └── Save organized markdown files
          │
          ▼
5. OUTPUT
   ├── Categorized markdown documents
   ├── Research summary report
   ├── Link collection database
   └── Failed URL log
```

## File Structure

```
tools/research-gatherer/
├── research_gatherer.py      # Main application
├── requirements.txt           # Python dependencies
├── README.md                  # Full documentation
├── QUICKSTART.md              # Getting started guide
├── test.py                    # Test suite
├── example_keywords.txt       # Sample keyword list
│
├── engines/                   # Search engine modules
│   ├── __init__.py
│   ├── google.py
│   ├── bing.py
│   ├── yahoo.py
│   └── ... (14 engines total)
│
├── utils/                     # Utility modules
│   ├── __init__.py
│   └── helper.py             # Logging and helpers
│
└── libs/                      # Shared libraries
    ├── __init__.py
    ├── fetch.py              # HTTP fetching
    └── html_parser.py        # HTML parsing
```

## Output Structure

```
research_output/
├── collected_links.txt          # All unique URLs collected
├── failed_urls.txt              # URLs that failed to parse
├── RESEARCH_SUMMARY.md          # Statistics and structure
│
└── parsed_content/              # Organized markdown files
    ├── github.com/
    │   ├── awesome-list.md
    │   └── repository-readme.md
    ├── medium.com/
    │   └── article-title.md
    ├── stackoverflow.com/
    │   └── question-answer.md
    └── arxiv.org/
        └── research-paper.md
```

## Use Cases

### 1. Academic Research
- Collect papers and articles on specific topics
- Organize by source (journals, conferences, preprints)
- Build literature review database

### 2. Competitive Intelligence
- Monitor competitor content and announcements
- Track industry trends and news
- Analyze market positioning

### 3. Technical Documentation
- Gather tutorials and guides
- Collect API documentation
- Build knowledge base

### 4. Content Curation
- Research trending topics
- Collect reference materials
- Organize thought leadership content

## Components

### 1. SearchEngineLoader
```python
- Dynamically loads all engine modules
- Manages parallel search execution
- Aggregates results from all engines
```

### 2. LinkManager
```python
- Maintains unique link collection
- Persistent storage in text file
- Deduplication logic
```

### 3. JinaParser
```python
- Interfaces with Jina AI Reader API
- Converts HTML to clean markdown
- Extracts titles and metadata
- Handles rate limiting
```

### 4. ResearchGatherer
```python
- Orchestrates entire workflow
- Manages search and parse phases
- Organizes output structure
- Generates summary reports
```

## Advantages

### Compared to Manual Research
- **10-100x faster** link collection
- **Automatic organization** by domain
- **Clean markdown** instead of HTML
- **Persistent storage** for incremental research

### Compared to Single-Engine Tools
- **Higher coverage** with 14 engines
- **Parallel processing** for speed
- **Built-in deduplication**
- **Automated categorization**

### Compared to Simple Web Scrapers
- **AI-powered parsing** removes ads, navigation
- **Metadata enrichment** for context
- **Smart filename generation** from content
- **Organized structure** instead of flat files

## Technical Details

### Dependencies
- `requests` - HTTP client for API calls
- `beautifulsoup4` - HTML parsing for search engines
- `lxml` - Fast XML/HTML processing
- `selenium` - Browser automation (optional)

### API Usage
- **Jina AI Reader**: https://r.jina.ai/{url}
  - Free tier available
  - Rate limit: ~1 request per 0.5s (built into tool)
  - No authentication required

### Performance
- **Search**: ~10-30 seconds for 14 engines
- **Parsing**: ~1-2 seconds per URL
- **Memory**: <100MB typical usage
- **Storage**: ~10-50KB per markdown file

## Best Practices

### For Efficiency
1. Search first, parse later (two-step process)
2. Use keyword lists for batch operations
3. Filter before parsing for large collections
4. Run parsing overnight for 100+ URLs

### For Organization
1. Use descriptive output directory names
2. One project per directory
3. Keep keyword files with output
4. Back up collected_links.txt

### For Quality
1. Review collected links before parsing
2. Check failed_urls.txt for patterns
3. Use domain filtering for focused research
4. Validate summary statistics

## Limitations

### Technical
- Requires internet connection
- Subject to search engine rate limits
- Some sites may block Jina parser
- Large PDFs may fail to parse

### Legal/Ethical
- Respects robots.txt (search engines)
- Uses public APIs (Jina)
- No authentication bypass
- Fair use applies to parsed content

## Future Enhancements

### Planned Features
- [ ] Custom search engine integration
- [ ] Advanced filtering (date, filetype)
- [ ] Batch retry for failed URLs
- [ ] Export to other formats (PDF, DOCX)
- [ ] Duplicate content detection
- [ ] Keyword  extraction from parsed content
- [ ] Citation management integration

### Possible Integrations
- Obsidian vaults
- Notion databases
- Zotero libraries
- Elasticsearch indexing

## Credits

This tool combines and extends:
- **pyse** - Multi-engine search tool
- **jina-parser** - Jina AI Reader integration

Built for the Infradyne project research infrastructure.

---

**Version**: 1.0.0  
**Created**: 2026-02-05  
**Status**: Production Ready
