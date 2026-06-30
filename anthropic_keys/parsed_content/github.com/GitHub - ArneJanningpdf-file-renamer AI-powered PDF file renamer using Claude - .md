---
source: https://github.com/ArneJanning/pdf-file-renamer
parsed_date: 2026-06-27 01:28:45
domain: github.com
---

Title: GitHub - ArneJanning/pdf-file-renamer: AI-powered PDF file renamer using Claude - automatically extracts and renames PDFs based on bibliographic information

URL Source: https://github.com/ArneJanning/pdf-file-renamer

Markdown Content:
## PDF & Screenshot File Renamer

[](https://github.com/ArneJanning/pdf-file-renamer#pdf--screenshot-file-renamer)
A powerful CLI tool that automatically renames PDF files and screenshots based on their content using Claude AI. For PDFs, it extracts bibliographic information (author, year, title). For screenshots, it uses either local OCR (Tesseract) or Claude Vision to analyze content and identify applications, dates, and content types. Perfect for organizing academic papers, books, screenshots, and other documents with consistent, meaningful filenames.

**Latest Version: 0.2.1** - Now with dual OCR methods for screenshots!

## What's New in v0.2.1

[](https://github.com/ArneJanning/pdf-file-renamer#whats-new-in-v021)
*   **Claude Vision Support**: Use Claude's vision capabilities directly on screenshots for perfect accuracy
*   **Dual OCR Methods**: Choose between Tesseract (free, local) or Claude Vision (accurate, API-based)
*   **Flexible Configuration**: Set OCR method via CLI flag or environment variable
*   **No Tesseract Required**: When using Claude Vision, no local OCR installation needed

## Features

[](https://github.com/ArneJanning/pdf-file-renamer#features)
### PDF Processing

[](https://github.com/ArneJanning/pdf-file-renamer#pdf-processing)
*   🤖 **AI-Powered Extraction**: Uses Claude AI to intelligently extract bibliographic information from PDFs
*   📚 **Smart Name Detection**: Handles various naming conventions (e.g., "van Gogh", "O'Brien", "Smith Jr.")
*   📄 **Page Limit Control**: Analyzes only the first pages of PDFs for efficiency

### Screenshot Processing (NEW!)

[](https://github.com/ArneJanning/pdf-file-renamer#screenshot-processing-new)
*   🖼️ **Dual OCR Methods**: Choose between Tesseract (local) or Claude Vision (API)
*   🔍 **Intelligent Analysis**: AI identifies applications, dates, content types, and main subjects
*   📸 **Format Support**: Handles PNG, JPG, JPEG, BMP, GIF, TIFF, WEBP
*   🏷️ **Smart Categorization**: Recognizes emails, chats, errors, websites, documents, etc.

### General Features

[](https://github.com/ArneJanning/pdf-file-renamer#general-features)
*   🎯 **Flexible Templates**: Fully customizable filename templates for both PDFs and screenshots
*   📁 **Batch Processing**: Process entire directories with mixed file types
*   🔍 **Preview Mode**: Dry-run option to preview changes before applying them
*   🛡️ **Safe Operation**: Automatic handling of duplicate filenames
*   ⚡ **Fast Processing**: Efficient handling of large directories

## Table of Contents

[](https://github.com/ArneJanning/pdf-file-renamer#table-of-contents)
*   [Installation](https://github.com/ArneJanning/pdf-file-renamer#installation)
*   [Quick Start](https://github.com/ArneJanning/pdf-file-renamer#quick-start)
*   [Configuration](https://github.com/ArneJanning/pdf-file-renamer#configuration)
*   [Usage](https://github.com/ArneJanning/pdf-file-renamer#usage)
*   [PDF Templates](https://github.com/ArneJanning/pdf-file-renamer#pdf-templates)
*   [Screenshot Templates](https://github.com/ArneJanning/pdf-file-renamer#screenshot-templates)
*   [Examples](https://github.com/ArneJanning/pdf-file-renamer#examples)
*   [API Key Setup](https://github.com/ArneJanning/pdf-file-renamer#api-key-setup)
*   [Advanced Usage](https://github.com/ArneJanning/pdf-file-renamer#advanced-usage)
*   [Troubleshooting](https://github.com/ArneJanning/pdf-file-renamer#troubleshooting)
*   [Development](https://github.com/ArneJanning/pdf-file-renamer#development)
*   [License](https://github.com/ArneJanning/pdf-file-renamer#license)

## Installation

[](https://github.com/ArneJanning/pdf-file-renamer#installation)
### Prerequisites

[](https://github.com/ArneJanning/pdf-file-renamer#prerequisites)
*   Python 3.12 or higher
*   An Anthropic API key for Claude AI
*   Tesseract OCR (optional, for local screenshot OCR) 
    *   **Ubuntu/Debian**: `sudo apt install tesseract-ocr`
    *   **macOS**: `brew install tesseract`
    *   **Windows**: Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
    *   **Note**: Not needed if using Claude Vision for OCR

### Install from source

[](https://github.com/ArneJanning/pdf-file-renamer#install-from-source)
1.   Clone the repository:

git clone https://github.com/ArneJanning/pdf-file-renamer.git
cd pdf-file-renamer

1.   Create a virtual environment (recommended):

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

1.   Install the package:

pip install -e .

### Install using uv (recommended)

[](https://github.com/ArneJanning/pdf-file-renamer#install-using-uv-recommended)
If you have [uv](https://github.com/astral-sh/uv) installed:

uv pip install -e .

## Quick Start

[](https://github.com/ArneJanning/pdf-file-renamer#quick-start)
1.   **Set up your API key**:

cp .env.example .env
# Edit .env and add your Anthropic API key

1.   **Test with dry-run**:

pdf-renamer /path/to/directory --dry-run

1.   **Rename files**:

pdf-renamer /path/to/directory

## Configuration

[](https://github.com/ArneJanning/pdf-file-renamer#configuration)
### Environment Variables

[](https://github.com/ArneJanning/pdf-file-renamer#environment-variables)
Create a `.env` file in your working directory (or copy `.env.example`):

# Claude API Configuration
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# PDF file naming template
# Variables: {author}, {author_last}, {editor}, {editor_last}, 
# {author_or_editor}, {author_or_editor_last}, {year}, {title}, {subtitle}, {full_title}
# Use {full_title} for title with subtitle properly formatted (recommended)
PDF_FILENAME_TEMPLATE={author_or_editor_last} {year} - {full_title}.pdf

# Screenshot file naming template 
# Variables: {application}, {date}, {time}, {datetime}, {content_type}, {main_subject}
SCREENSHOT_FILENAME_TEMPLATE={datetime} {application} - {main_subject}.png

# Number of pages to extract for analysis (default: 10)
MAX_PAGES_TO_EXTRACT=10

# Claude model to use (default: claude-3-5-sonnet-20241022)
CLAUDE_MODEL=claude-3-5-sonnet-20241022

# OCR method for screenshots: 'tesseract' or 'claude' (default: tesseract)
OCR_METHOD=tesseract

### Configuration Options

[](https://github.com/ArneJanning/pdf-file-renamer#configuration-options)
| Option | Description | Default |
| --- | --- | --- |
| `ANTHROPIC_API_KEY` | Your Anthropic API key (required) | None |
| `PDF_FILENAME_TEMPLATE` | Template for renamed PDF files | `{author_or_editor_last} {year} - {title}.pdf` |
| `SCREENSHOT_FILENAME_TEMPLATE` | Template for renamed screenshots | `{datetime} {application} - {main_subject}.png` |
| `MAX_PAGES_TO_EXTRACT` | Number of PDF pages to analyze | 10 |
| `CLAUDE_MODEL` | Claude model to use | `claude-3-5-sonnet-20241022` |
| `OCR_METHOD` | OCR method for screenshots: `tesseract` or `claude` | `tesseract` |

## Usage

[](https://github.com/ArneJanning/pdf-file-renamer#usage)
### Basic Command

[](https://github.com/ArneJanning/pdf-file-renamer#basic-command)

pdf-renamer [OPTIONS] DIRECTORY

### Options

[](https://github.com/ArneJanning/pdf-file-renamer#options)
| Option | Short | Description |
| --- | --- | --- |
| `--output` | `-o` | Output directory for renamed files (default: input directory) |
| `--dry-run` | `-n` | Preview changes without renaming files |
| `--pdf-template` |  | Override the PDF filename template from .env |
| `--screenshot-template` |  | Override the screenshot filename template from .env |
| `--ocr-method` |  | OCR method for screenshots: `tesseract` or `claude` |
| `--help` |  | Show help message |

### Command Examples

[](https://github.com/ArneJanning/pdf-file-renamer#command-examples)
**Preview changes (dry-run)**:

pdf-renamer ~/Documents/Papers --dry-run

**Rename to a different directory**:

pdf-renamer ~/Downloads/PDFs --output ~/Documents/Organized

**Use custom templates**:

# Custom PDF template
pdf-renamer ~/Papers --pdf-template "{author_last}, {author} ({year}) - {title}.pdf"

# Custom screenshot template
pdf-renamer ~/Screenshots --screenshot-template "{application} - {content_type} - {main_subject}.png"

**Process current directory**:

pdf-renamer .

## PDF Templates

[](https://github.com/ArneJanning/pdf-file-renamer#pdf-templates)
### Available Variables

[](https://github.com/ArneJanning/pdf-file-renamer#available-variables)
| Variable | Description | Example |
| --- | --- | --- |
| `{author}` | Full author name | "F. Scott Fitzgerald" |
| `{author_last}` | Author's last name only | "Fitzgerald" |
| `{editor}` | Full editor name | "John Smith" |
| `{editor_last}` | Editor's last name only | "Smith" |
| `{author_or_editor}` | Author or editor (with suffix) | "F. Scott Fitzgerald" or "John Smith (Ed.)" |
| `{author_or_editor_last}` | Last name of author or editor | "Fitzgerald" or "Smith" |
| `{year}` | Publication year | "1925" |
| `{title}` | Main title only | "Red Mafiya" |
| `{subtitle}` | Subtitle only (if present) | "How the Russian Mob Has Invaded America" |
| `{full_title}` | Title with subtitle properly formatted | "Red Mafiya. How the Russian Mob Has Invaded America" |

### Template Examples

[](https://github.com/ArneJanning/pdf-file-renamer#template-examples)
1.   **Default format** (clean and simple, with subtitle support):

```
{author_or_editor_last} {year} - {full_title}.pdf
→ Fitzgerald 1925 - The Great Gatsby.pdf
→ Friedman 2000 - Red Mafiya. How the Russian Mob Has Invaded America.pdf
``` 
2.   **Academic citation style**:

```
{author_last}, {author} ({year}). {full_title}.pdf
→ Fitzgerald, F. Scott Fitzgerald (1925). The Great Gatsby.pdf
→ Friedman, Robert I. Friedman (2000). Red Mafiya. How the Russian Mob Has Invaded America.pdf
``` 
3.   **Library style**:

```
[{year}] {author_or_editor} - {full_title}.pdf
→ [1925] F. Scott Fitzgerald - The Great Gatsby.pdf
→ [2000] Robert I. Friedman - Red Mafiya. How the Russian Mob Has Invaded America.pdf
``` 
4.   **Title and subtitle separate**:

```
{author_last}-{year}-{title}_{subtitle}.pdf
→ Friedman-2000-Red Mafiya_How the Russian Mob Has Invaded America.pdf
``` 
5.   **Full information**:

```
{author} ({year}) - {full_title} [{author_last}].pdf
→ F. Scott Fitzgerald (1925) - The Great Gatsby [Fitzgerald].pdf
→ Robert I. Friedman (2000) - Red Mafiya. How the Russian Mob Has Invaded America [Friedman].pdf
``` 

## Screenshot Templates

[](https://github.com/ArneJanning/pdf-file-renamer#screenshot-templates)
### Available Variables

[](https://github.com/ArneJanning/pdf-file-renamer#available-variables-1)
| Variable | Description | Example |
| --- | --- | --- |
| `{application}` | Application/software name | "Chrome", "WhatsApp", "Terminal" |
| `{date}` | Date from screenshot | "2025-01-15" |
| `{time}` | Time from screenshot | "14:30" |
| `{datetime}` | Combined date and time | "2025-01-15 14:30" |
| `{content_type}` | Type of content | "email", "chat", "error", "website" |
| `{main_subject}` | AI-determined subject | "Project Meeting Schedule" |

### Template Examples

[](https://github.com/ArneJanning/pdf-file-renamer#template-examples-1)
1.   **Default format** (chronological organization):

```
{datetime} {application} - {main_subject}.png
→ 2025-01-15 14:30 Gmail - Project Meeting Schedule Email.png
``` 
2.   **Application-based organization**:

```
{application}/{date} - {main_subject}.png
→ Gmail/2025-01-15 - Project Meeting Schedule Email.png
``` 
3.   **Content type grouping**:

```
{content_type}/{application} - {main_subject}.png
→ email/Gmail - Project Meeting Schedule Email.png
``` 
4.   **Minimal format**:

```
{date} - {main_subject}.png
→ 2025-01-15 - Project Meeting Schedule Email.png
``` 
5.   **Detailed format**:

```
{date} {time} - {application} ({content_type}) - {main_subject}.png
→ 2025-01-15 14:30 - Gmail (email) - Project Meeting Schedule Email.png
``` 

## Examples

[](https://github.com/ArneJanning/pdf-file-renamer#examples)
### Example 1: Organizing Research Papers

[](https://github.com/ArneJanning/pdf-file-renamer#example-1-organizing-research-papers)

# Preview the renaming
pdf-renamer ~/Downloads/papers --dry-run

# Output:
# Processing: quantum_computing_2023.pdf
# Author/Editor: Alice Johnson
# Year: 2023
# Title: Advances in Quantum Computing Algorithms
# New filename: Johnson 2023 - Advances in Quantum Computing Algorithms.pdf
# [DRY RUN] Would copy to: ~/Downloads/papers/Johnson 2023 - Advances in Quantum Computing Algorithms.pdf

# Apply the renaming
pdf-renamer ~/Downloads/papers

### Example 2: Custom Organization System

[](https://github.com/ArneJanning/pdf-file-renamer#example-2-custom-organization-system)

# Organize by year with custom template
pdf-renamer ~/Library/PDFs \
  --template "[{year}] {author_last} - {title}.pdf" \
  --output ~/Library/Organized

### Example 3: Processing Books

[](https://github.com/ArneJanning/pdf-file-renamer#example-3-processing-books)

# Books often have editors instead of authors
pdf-renamer ~/Books --pdf-template "{author_or_editor} - {title} ({year}).pdf"

# Output example:
# Original: handbook_of_ai.pdf
# Renamed: Smith (Ed.) - Handbook of Artificial Intelligence (2022).pdf

### Example 4: Processing Screenshots

[](https://github.com/ArneJanning/pdf-file-renamer#example-4-processing-screenshots)

# Process a directory of screenshots
pdf-renamer ~/Screenshots --dry-run

# Output:
# Processing: email_screenshot.png
# Application: Gmail
# Date: 2025-01-15
# Content Type: email
# Main Subject: Project Meeting Schedule Email
# New filename: 2025-01-15 1430 Gmail - Project Meeting Schedule Email.png
# [DRY RUN] Would copy to: ~/Screenshots/2025-01-15 1430 Gmail - Project Meeting Schedule Email.png

### Example 5: Mixed Directory (PDFs and Screenshots)

[](https://github.com/ArneJanning/pdf-file-renamer#example-5-mixed-directory-pdfs-and-screenshots)

# Process a Downloads folder with both PDFs and screenshots
pdf-renamer ~/Downloads

# Output:
# Found 150 PDF files and 45 screenshot files to process
# Processing PDF files...
# Processing: research_paper.pdf
# New filename: Johnson 2024 - Machine Learning in Healthcare.pdf
# Processing screenshot files...
# Processing: screenshot_2024.png
# New filename: 2024-01-20 1030 Terminal - Docker Container Status.png

### Example 6: Using Claude Vision for Screenshots

[](https://github.com/ArneJanning/pdf-file-renamer#example-6-using-claude-vision-for-screenshots)

# Use Claude Vision for more accurate screenshot analysis
pdf-renamer ~/Screenshots --ocr-method claude

# Output:
# Processing: error_dialog.png
# Application: Microsoft Windows
# Date: 2025-01-16
# Content Type: error
# Main Subject: Application Error 0x80070005
# New filename: 2025-01-16 1145 Microsoft Windows - Application Error 0x80070005.png
# Note: Using Claude Vision - no OCR errors!

## API Key Setup

[](https://github.com/ArneJanning/pdf-file-renamer#api-key-setup)
### Getting an Anthropic API Key

[](https://github.com/ArneJanning/pdf-file-renamer#getting-an-anthropic-api-key)
1.   Sign up at [console.anthropic.com](https://console.anthropic.com/)
2.   Navigate to API Keys section
3.   Create a new API key
4.   Copy the key (starts with `sk-ant-api...`)

### Setting the API Key

[](https://github.com/ArneJanning/pdf-file-renamer#setting-the-api-key)
**Method 1: Environment file (recommended)**

echo "ANTHROPIC_API_KEY=sk-ant-api..." > .env

**Method 2: Export in shell**

export ANTHROPIC_API_KEY="sk-ant-api..."

**Method 3: Pass via environment**

ANTHROPIC_API_KEY="sk-ant-api..." pdf-renamer /path/to/pdfs

## Advanced Usage

[](https://github.com/ArneJanning/pdf-file-renamer#advanced-usage)
### OCR Methods for Screenshots

[](https://github.com/ArneJanning/pdf-file-renamer#ocr-methods-for-screenshots)
The tool supports two OCR methods for processing screenshots:

#### 1. Tesseract (Default)

[](https://github.com/ArneJanning/pdf-file-renamer#1-tesseract-default)
*   **Pros**: Fast, free, runs locally, no API costs
*   **Cons**: May have OCR errors, requires Tesseract installation
*   **Usage**: Default method, or use `--ocr-method tesseract`

# Using Tesseract (default)
pdf-renamer ~/Screenshots

# Explicitly specify Tesseract
pdf-renamer ~/Screenshots --ocr-method tesseract

#### 2. Claude Vision

[](https://github.com/ArneJanning/pdf-file-renamer#2-claude-vision)
*   **Pros**: More accurate, no OCR errors, understands visual context, no Tesseract needed
*   **Cons**: Uses more API credits (~10x), slightly slower
*   **Usage**: Use `--ocr-method claude` or set `OCR_METHOD=claude` in .env

# Using Claude Vision for better accuracy
pdf-renamer ~/Screenshots --ocr-method claude

# Set in .env file for permanent configuration
echo "OCR_METHOD=claude" >> .env

**Comparison Example**:

*   Tesseract might read: "Mierosoft Windows" (OCR error)
*   Claude Vision reads: "Microsoft Windows" (accurate)

**Recommendation**: Use Tesseract for bulk processing to save costs, Claude Vision for important files where accuracy matters.

### Handling Special Cases

[](https://github.com/ArneJanning/pdf-file-renamer#handling-special-cases)
**Multiple authors**: Claude will intelligently handle papers with multiple authors, often using "et al." for many authors:

```
Original: collaborative_research.pdf
Renamed: Smith et al 2023 - Collaborative Research Methods.pdf
```

**Non-English names**: The AI correctly handles various naming conventions:

```
van Gogh → van Gogh (not "Gogh")
O'Brien → O'Brien (not "Brien")
José García → García (not "José")
```

**Missing information**: Files with missing data use defaults:

```
No author: Unknown 2023 - Title.pdf
No year: Author Unknown Year - Title.pdf
```

### Performance Tips

[](https://github.com/ArneJanning/pdf-file-renamer#performance-tips)
1.   **Batch size**: Process directories with 100-200 PDFs at a time for best performance
2.   **Page extraction**: Reduce `MAX_PAGES_TO_EXTRACT` for faster processing of large PDFs
3.   **Model selection**: Use `claude-3-5-sonnet` for best accuracy, or `claude-3-haiku` for speed

### Integration with File Managers

[](https://github.com/ArneJanning/pdf-file-renamer#integration-with-file-managers)
**macOS Automator**: Create a Quick Action to rename PDFs from Finder **Windows**: Add to Send To menu for right-click renaming **Linux**: Create a Nautilus script or KDE Service Menu

## Troubleshooting

[](https://github.com/ArneJanning/pdf-file-renamer#troubleshooting)
### Common Issues

[](https://github.com/ArneJanning/pdf-file-renamer#common-issues)
**"ANTHROPIC_API_KEY not found"**

*   Ensure your `.env` file is in the current directory
*   Check the API key is correctly formatted
*   Try exporting the key: `export ANTHROPIC_API_KEY="your-key"`

**"Failed to extract text from PDF"**

*   The PDF might be scanned/image-based
*   The PDF might be corrupted
*   Try opening the PDF in a reader to verify it's valid

**"Failed to extract text from screenshot"**

*   Ensure Tesseract is installed: `which tesseract` (only needed for Tesseract OCR)
*   Try switching to Claude Vision: `--ocr-method claude`
*   The image might be corrupted or in an unsupported format
*   Try a different image format (PNG usually works best)
*   Check if the image contains readable text

**"Failed to extract bibliographic information"**

*   The PDF might not contain clear bibliographic information
*   Try increasing `MAX_PAGES_TO_EXTRACT`
*   The PDF might be in an unsupported language

**Rate limiting errors**

*   Add delays between large batches
*   Reduce concurrent processing
*   Check your API tier limits

### Debug Mode

[](https://github.com/ArneJanning/pdf-file-renamer#debug-mode)
Run with logging to see detailed information:

# Set logging level
export LOG_LEVEL=DEBUG
pdf-renamer /path/to/pdfs

## Development

[](https://github.com/ArneJanning/pdf-file-renamer#development)
### Project Structure

[](https://github.com/ArneJanning/pdf-file-renamer#project-structure)

```
pdf-file-renamer/
├── file_renamer/
│   ├── __init__.py          # Package initialization
│   ├── __main__.py          # Entry point
│   ├── cli.py               # CLI interface
│   ├── models.py            # Pydantic models
│   ├── ai_extractor.py      # Claude AI integration
│   └── pdf_extractor.py     # PDF and screenshot text extraction
├── tests/                   # Comprehensive test suite
│   ├── conftest.py         # Test fixtures
│   ├── test_models.py      # Model tests
│   ├── test_pdf_extractor.py # PDF extraction tests
│   ├── test_ai_extractor.py # AI integration tests
│   ├── test_cli.py         # CLI tests
│   ├── test_integration.py # Integration tests
│   └── test_performance.py # Performance tests
├── .github/workflows/      # CI/CD workflows
├── .env.example            # Example configuration
├── pyproject.toml          # Project configuration
├── README.md               # This file
├── CHANGELOG.md            # Version history
├── SCREENSHOT_TEST_RESULTS.md # Screenshot functionality test results
├── TEST_SUMMARY.md         # Test suite documentation
└── LICENSE                 # MIT License
```

### Running from Source

[](https://github.com/ArneJanning/pdf-file-renamer#running-from-source)

# Clone the repository
git clone https://github.com/ArneJanning/pdf-file-renamer.git
cd pdf-file-renamer

# Install in development mode
pip install -e .

# Run directly
python -m file_renamer /path/to/pdfs

### Testing

[](https://github.com/ArneJanning/pdf-file-renamer#testing)
The project includes a comprehensive test suite with 80+ tests covering:

**Install test dependencies:**

pip install -e ".[test]"

**Run all tests:**

pytest tests/ -v

**Run with coverage:**

pytest tests/ --cov=file_renamer --cov-report=term-missing

**Run performance tests:**

pytest tests/test_performance.py -v

**Use the test runner:**

python run_tests.py --install

**Test categories:**

*   **Unit Tests**: Individual component functionality
*   **Integration Tests**: End-to-end workflows
*   **Performance Tests**: Scalability and efficiency
*   **CLI Tests**: Command-line interface behavior

See [TEST_SUMMARY.md](https://github.com/ArneJanning/pdf-file-renamer/blob/main/TEST_SUMMARY.md) for detailed test documentation.

### Contributing

[](https://github.com/ArneJanning/pdf-file-renamer#contributing)
1.   Fork the repository
2.   Create a feature branch: `git checkout -b feature-name`
3.   Make your changes
4.   Run tests: `pytest`
5.   Commit: `git commit -am 'Add feature'`
6.   Push: `git push origin feature-name`
7.   Create a Pull Request

### Adding New Features

[](https://github.com/ArneJanning/pdf-file-renamer#adding-new-features)
To add a new template variable:

1.   Update `models.py` to add the field
2.   Update the Claude prompt in `ai_extractor.py`
3.   Add the variable to `format_filename()`
4.   Update documentation

## License

[](https://github.com/ArneJanning/pdf-file-renamer#license)
MIT License - see LICENSE file for details.

## Acknowledgments

[](https://github.com/ArneJanning/pdf-file-renamer#acknowledgments)
*   Built with [PydanticAI](https://ai.pydantic.dev/) for structured AI interactions
*   Powered by [Claude](https://www.anthropic.com/) from Anthropic for content analysis
*   PDF processing via [pypdf](https://pypdf.readthedocs.io/)
*   OCR processing via [pytesseract](https://github.com/madmaze/pytesseract) and [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) (optional)
*   Claude Vision API for direct image analysis (alternative to OCR)
*   Image handling with [Pillow](https://python-pillow.org/)
*   CLI interface using [Click](https://click.palletsprojects.com/)

## Support

[](https://github.com/ArneJanning/pdf-file-renamer#support)
*   **Issues**: [GitHub Issues](https://github.com/ArneJanning/pdf-file-renamer/issues)
*   **Discussions**: [GitHub Discussions](https://github.com/ArneJanning/pdf-file-renamer/discussions)
*   **Email**: [your-email@example.com](mailto:your-email@example.com)

* * *

Made with ❤️ by Arne Janning
