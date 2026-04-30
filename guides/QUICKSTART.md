# Quick Start Guide

## Installation

```bash
# Navigate to the tool directory
cd tools/research-gatherer

# Install dependencies
pip install -r requirements.txt
```

## Quick Examples

### 1. Single Keyword Research (Full Workflow)

"cdn.studio.f5.com"

```bash
python research_gatherer.py -k "cybersecurity best practices" --auto-parse -o security_research
```

This will:
- Search across all 14 search engines
- Collect unique URLs
- Parse each URL to markdown
- Organize by domain
- Generate summary report

### 2. Multiple Keywords from File

```bash
# Use the example file
python research_gatherer.py -l example_keywords.txt --auto-parse -o example_output
```

### 3. Two-Step Process (Recommended for Large Projects)

```bash
# Step 1: Collect links (fast)
python research_gatherer.py -k "artificial intelligence" -o ai_research

# Step 2: Review collected links
cat ai_research/collected_links.txt

# Step 3: Parse (slower, can be done later)
python research_gatherer.py --parse-only -o ai_research
```

### 4. Filtered Parsing

```bash
# Collect from all sources
python research_gatherer.py -l topics.txt -o research

# Parse only GitHub links
python research_gatherer.py --parse-only --filter "github.com" -o research
```

## View Results

```bash
# See summary
cat research_output/RESEARCH_SUMMARY.md

# Browse organized content
cd research_output/parsed_content/
ls -l
```

## Common Workflows

### Academic Research
1. Create keyword list of research topics
2. Run with `--auto-parse`
3. Review summary and organized documents
4. Use as reference material

### Competitive Intelligence
1. Search for competitor names/products
2. Collect links first
3. Review and filter
4. Parse only relevant domains

### Tech Monitoring
1. Create keywords for technologies you're tracking
2. Run weekly with same output directory
3. New content automatically added
4. Deduplicated automatically

## Troubleshooting

### No results?
- Check internet connection
- Try with `-d` flag for debug logs
- Some engines may be blocked by firewall

### Parsing failures?
- Check `failed_urls.txt`
- Some sites block Jina parser
- Try again later (temporary failures)

### Too slow?
- Use two-step process
- Parse in batches with `--filter`
- Run overnight for large projects

## Next Steps

1. Read full [README.md](README.md) for all options
2. Customize keyword lists for your needs
3. Integrate into your research workflow
4. Automate with cron/scheduled tasks
