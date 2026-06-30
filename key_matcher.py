#!/usr/bin/env python3
"""
Key Matcher — Parse plaintext / markdown files for Anthropic API keys & secrets.

Reads regex patterns from key_match-regex.txt, walks a directory of parsed
content (.md files), and extracts matches with context.

Usage:
    python key_matcher.py
    python key_matcher.py -d anthropic_keys/parsed_content
    python key_matcher.py -d anthropic_keys/parsed_content -o results.json
    python key_matcher.py -d anthropic_keys/parsed_content -o results.txt --format text
    python key_matcher.py -d anthropic_keys\parsed_content\github.com -o results.txt --format text
"""

import os
import re
import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Optional, Set, Tuple
from dataclasses import dataclass, field, asdict


# ---------------------------------------------------------------------------
# Placeholder / example patterns — matches that look like keys but are NOT
# real secrets (documentation examples, "your-key-here", etc.)
# ---------------------------------------------------------------------------
PLACEHOLDER_PATTERNS: List[str] = [
    r'sk-ant-api\d{2}-\.{3,}',               # sk-ant-api03-...
    r'sk-ant-api\d{2}-your[-_]?key[-_]?here', # sk-ant-api03-your-key-here
    r'sk-ant-api\d{2}-dev-\.{3,}',            # sk-ant-api03-dev-...
    r'sk-ant-api\d{2}-stg-\.{3,}',            # sk-ant-api03-stg-...
    r'sk-ant-api\d{2}-prd-\.{3,}',            # sk-ant-api03-prd-...
    r'sk-ant-oat\d{2}-\.{3,}',                # sk-ant-oat01-...
    r'sk-ant-(?:api|oat)\d{2}-<',             # sk-ant-api03-<...>
    r'sk-ant-(?:api|oat)\d{2}-\$',            # sk-ant-api03-$VAR
    r'sk-ant-(?:api|oat)\d{2}-\{',            # sk-ant-api03-{...}
    r'sk-ant-(?:api|oat)\d{2}-xxxx',          # sk-ant-api03-xxxx...
    r'sk-ant-(?:api|oat)\d{2}-example',       # sk-ant-api03-example
    r'sk-ant-(?:api|oat)\d{2}-test',          # sk-ant-api03-test
    r'sk-ant-(?:api|oat)\d{2}-demo',          # sk-ant-api03-demo
    r'sk-ant-(?:api|oat)\d{2}-sample',        # sk-ant-api03-sample
    r'sk-ant-(?:api|oat)\d{2}-dummy',         # sk-ant-api03-dummy
    r'sk-ant-(?:api|oat)\d{2}-fake',          # sk-ant-api03-fake
    r'sk-ant-(?:api|oat)\d{2}-placeholder',   # sk-ant-api03-placeholder
]

PLACEHOLDER_RE = re.compile('|'.join(PLACEHOLDER_PATTERNS), re.IGNORECASE)


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class Match:
    """A single regex match found in a file."""
    file: str           # Relative file path
    line: int           # Line number (1-based)
    pattern: str        # Which regex pattern matched
    matched: str        # The full matched text
    key: str            # Extracted key (group 1 if capture group exists)
    context_before: List[str] = field(default_factory=list)  # 2 lines before
    context_after: List[str] = field(default_factory=list)   # 2 lines after


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def load_patterns(pattern_file: str) -> List[Tuple[str, re.Pattern]]:
    """Load regex patterns from file. Returns list of (description, compiled_re)."""
    patterns: List[Tuple[str, re.Pattern]] = []
    if not os.path.exists(pattern_file):
        print(f"[!] Pattern file not found: {pattern_file}", file=sys.stderr)
        return patterns

    with open(pattern_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            try:
                patterns.append((line, re.compile(line, re.MULTILINE | re.IGNORECASE)))
            except re.error as e:
                print(f"[!] Invalid regex '{line}': {e}", file=sys.stderr)

    return patterns


def is_placeholder(key: str) -> bool:
    """Check if a matched key looks like a placeholder / example."""
    return bool(PLACEHOLDER_RE.search(key))


def extract_key(match_obj: re.Match, pattern_str: str) -> str:
    """Extract the actual key from a match. Prefer group 1 if it exists."""
    groups = match_obj.groups()
    if groups:
        # Return the first non-None group
        for g in groups:
            if g is not None:
                return g
    return match_obj.group(0)


def get_context(lines: List[str], line_idx: int, before: int = 2, after: int = 2) -> Tuple[List[str], List[str]]:
    """Get context lines around a match."""
    ctx_before = []
    ctx_after = []

    for i in range(max(0, line_idx - before), line_idx):
        ctx_before.append(lines[i].rstrip())

    for i in range(line_idx + 1, min(len(lines), line_idx + 1 + after)):
        ctx_after.append(lines[i].rstrip())

    return ctx_before, ctx_after


def scan_file(filepath: str, patterns: List[Tuple[str, re.Pattern]], rel_path: str) -> List[Match]:
    """Scan a single file for all patterns. Returns list of Match objects."""
    matches: List[Match] = []

    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
    except Exception as e:
        print(f"[!] Error reading {filepath}: {e}", file=sys.stderr)
        return matches

    lines = content.split('\n')

    for pattern_str, compiled_re in patterns:
        for m in compiled_re.finditer(content):
            key = extract_key(m, pattern_str)

            # Skip placeholders
            if is_placeholder(key):
                continue

            # Calculate line number
            line_num = content[:m.start()].count('\n') + 1
            line_idx = line_num - 1

            ctx_before, ctx_after = get_context(lines, line_idx)

            matches.append(Match(
                file=rel_path,
                line=line_num,
                pattern=pattern_str,
                matched=m.group(0),
                key=key,
                context_before=ctx_before,
                context_after=ctx_after,
            ))

    return matches


def scan_directory(root_dir: str, patterns: List[Tuple[str, re.Pattern]]) -> List[Match]:
    """Walk a directory tree and scan all .md / .txt files."""
    all_matches: List[Match] = []
    root = Path(root_dir)

    if not root.exists():
        print(f"[!] Directory not found: {root_dir}", file=sys.stderr)
        return all_matches

    # Ignored extensions (binary, media, and compressed files)
    ignored_exts = {
        # Images
        '.png', '.jpg', '.jpeg', '.gif', '.webp', '.ico', '.svg', '.bmp', '.tiff', '.psd',
        # Audio/Video
        '.mp3', '.mp4', '.wav', '.avi', '.mov', '.flv', '.mkv', '.webm',
        # Archives/Compressed
        '.zip', '.tar', '.gz', '.rar', '.7z', '.bz2', '.xz',
        # Executables/Binaries/Libraries
        '.exe', '.dll', '.so', '.dylib', '.bin', '.pyc', '.class', '.o', '.a', '.lib',
        # Fonts
        '.woff', '.woff2', '.ttf', '.eot', '.otf',
        # Databases/Objects
        '.db', '.sqlite', '.sqlite3', '.pkl', '.pickle', '.h5',
        # Office documents (usually binary zip structures)
        '.docx', '.xlsx', '.pptx', '.pdf', '.doc', '.xls', '.ppt'
    }

    file_count = 0
    for filepath in root.rglob('*'):
        if filepath.is_file() and filepath.suffix.lower() not in ignored_exts:
            file_count += 1
            rel = str(filepath.relative_to(root))
            matches = scan_file(str(filepath), patterns, rel)
            all_matches.extend(matches)

    print(f"Scanned {file_count} files, found {len(all_matches)} matches", file=sys.stderr)
    return all_matches


def deduplicate(matches: List[Match]) -> List[Match]:
    """Remove duplicate keys, keeping the first occurrence."""
    seen: Set[str] = set()
    unique: List[Match] = []
    for m in matches:
        normalized = m.key.strip().lower()
        if normalized not in seen:
            seen.add(normalized)
            unique.append(m)
    return unique


# ---------------------------------------------------------------------------
# Output formatters
# ---------------------------------------------------------------------------

def format_json(matches: List[Match]) -> str:
    """Format matches as JSON."""
    return json.dumps([asdict(m) for m in matches], indent=2, ensure_ascii=False)


def format_text(matches: List[Match]) -> str:
    """Format matches as human-readable text."""
    lines: List[str] = []
    lines.append("=" * 80)
    lines.append(f"KEY MATCHER RESULTS -- {len(matches)} unique matches found")
    lines.append("=" * 80)

    for i, m in enumerate(matches, 1):
        lines.append(f"\n{'-' * 80}")
        lines.append(f"[{i}] {m.key}")
        lines.append(f"    File : {m.file}:{m.line}")
        lines.append(f"    Regex: {m.pattern}")

        if m.context_before:
            lines.append(f"    Context (before):")
            for ctx in m.context_before:
                lines.append(f"        {ctx}")

        lines.append(f"    >>> {m.matched.strip()}")

        if m.context_after:
            lines.append(f"    Context (after):")
            for ctx in m.context_after:
                lines.append(f"        {ctx}")

    lines.append(f"\n{'=' * 80}")
    lines.append("SUMMARY")
    lines.append("=" * 80)

    # Count by file
    file_counts: Dict[str, int] = {}
    for m in matches:
        file_counts[m.file] = file_counts.get(m.file, 0) + 1

    lines.append(f"\nTotal unique keys found: {len(matches)}")
    lines.append(f"\nKeys per file:")
    for fname, count in sorted(file_counts.items(), key=lambda x: -x[1]):
        lines.append(f"  {count:3d}  {fname}")

    # List all keys compactly
    lines.append(f"\n{'-' * 80}")
    lines.append("ALL KEYS (compact):")
    lines.append(f"{'-' * 80}")
    for i, m in enumerate(matches, 1):
        lines.append(f"  [{i:3d}] {m.key}")

    return '\n'.join(lines)


def format_csv(matches: List[Match]) -> str:
    """Format matches as CSV."""
    import csv
    import io
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['index', 'key', 'file', 'line', 'pattern'])
    for i, m in enumerate(matches, 1):
        writer.writerow([i, m.key, m.file, m.line, m.pattern])
    return output.getvalue()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='Key Matcher — Extract Anthropic API keys from parsed content',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python key_matcher.py
  python key_matcher.py -d anthropic_keys/parsed_content
  python key_matcher.py -d anthropic_keys/parsed_content -o results.json
  python key_matcher.py -d anthropic_keys/parsed_content -o results.txt --format text
  python key_matcher.py -d anthropic_keys/parsed_content --format csv
        """
    )
    parser.add_argument('-d', '--directory',
                        default='anthropic_keys/parsed_content',
                        help='Directory to scan (default: anthropic_keys/parsed_content)')
    parser.add_argument('-p', '--patterns',
                        default='key_match-regex.txt',
                        help='Regex patterns file (default: key_match-regex.txt)')
    parser.add_argument('-o', '--output',
                        help='Output file (default: stdout)')
    parser.add_argument('--format', '-f',
                        choices=['json', 'text', 'csv'],
                        default='text',
                        help='Output format (default: text)')
    parser.add_argument('--no-dedup',
                        action='store_true',
                        help='Show all matches including duplicates')
    parser.add_argument('--include-placeholders',
                        action='store_true',
                        help='Include placeholder/example keys (normally excluded)')
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    # Resolve paths relative to script directory
    script_dir = Path(__file__).parent
    patterns_file = script_dir / args.patterns
    scan_dir = script_dir / args.directory

    if not patterns_file.exists():
        # Try relative to CWD
        patterns_file = Path(args.patterns)
    if not scan_dir.exists():
        scan_dir = Path(args.directory)

    print(f"Patterns file: {patterns_file}", file=sys.stderr)
    print(f"Scan directory: {scan_dir}", file=sys.stderr)

    # Load patterns
    patterns = load_patterns(str(patterns_file))
    if not patterns:
        print("[!] No valid patterns loaded. Exiting.", file=sys.stderr)
        sys.exit(1)
    print(f"Loaded {len(patterns)} patterns", file=sys.stderr)

    # Scan
    matches = scan_directory(str(scan_dir), patterns)

    # Filter placeholders (unless --include-placeholders)
    if not args.include_placeholders:
        before = len(matches)
        matches = [m for m in matches if not is_placeholder(m.key)]
        skipped = before - len(matches)
        if skipped:
            print(f"Filtered out {skipped} placeholder/example keys", file=sys.stderr)

    # Deduplicate (unless --no-dedup)
    if not args.no_dedup:
        before = len(matches)
        matches = deduplicate(matches)
        dupes = before - len(matches)
        if dupes:
            print(f"Removed {dupes} duplicate keys", file=sys.stderr)

    # Format output
    formatters = {
        'json': format_json,
        'text': format_text,
        'csv': format_csv,
    }
    output = formatters[args.format](matches)

    # Write output
    if args.output:
        out_path = script_dir / args.output
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"Results written to: {out_path}", file=sys.stderr)
    else:
        # Use sys.stdout with utf-8 encoding to avoid UnicodeEncodeError on Windows
        # This is a common issue on Windows with default console encoding (cp1252)
        # when printing Unicode characters.
        sys.stdout.buffer.write(output.encode('utf-8', errors='replace'))
        sys.stdout.write('\n') # Add a newline at the end


if __name__ == '__main__':
    main()