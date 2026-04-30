#!/usr/bin/env python3
"""
Research Content Reconstructor
Combines separated parsed markdown files into comprehensive documents
Organizes by domain, filters low-quality content, removes duplicates
"""

import os
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import re

class ResearchReconstructor:
    """Reconstruct and organize parsed research content"""
    
    def __init__(self, research_dir):
        self.research_dir = Path(research_dir)
        self.parsed_content_dir = self.research_dir / 'parsed_content'
        
        # Content organization
        self.by_domain = defaultdict(list)
        self.by_category = defaultdict(list)
        
        # Quality filters
        self.skip_domains = [
            'exam', 'dump', 'cert', 'braindump', 'vce', 'practice',
            'jobs', 'careers', 'jooble', 'bayt', 'linkedin',
            '404', 'not found', 'page not found'
        ]
        
        # Category keywords
        self.categories = {
            'Official Documentation': ['docs.paloaltonetworks', 'pan.dev', 'live.paloaltonetworks'],
            'Technical Blogs': ['blog.', 'medium.com', 'avleonov.com'],
            'Security News': ['security', 'cyber', 'threat', 'vulnerability'],
            'Product Information': ['paloaltonetworks.com', 'paloguard'],
            'Implementation Guides': ['configuration', 'deployment', 'setup', 'guide'],
            'Comparisons & Reviews': ['vs', 'comparison', 'review', 'alternative'],
        }
    
    def should_skip_file(self, file_path, content):
        """Determine if file should be skipped based on quality filters"""
        file_name = file_path.name.lower()
        domain = file_path.parent.name.lower()
        
        # Skip based on domain
        for skip_term in self.skip_domains:
            if skip_term in domain or skip_term in file_name:
                return True
        
        # Skip based on content
        if len(content) < 100:  # Too short
            return True
        
        if '404' in file_name or 'not found' in file_name:
            return True
        
        # Skip exam dump sites
        if any(term in content[:500].lower() for term in ['exam questions', 'practice test', 'dumps pdf', 'certification exam']):
            return True
        
        return False
    
    def categorize_content(self, domain, file_path, content):
        """Categorize content based on domain and keywords"""
        assigned_category = 'Other Resources'
        
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword in domain or keyword in content[:1000].lower():
                    assigned_category = category
                    break
            if assigned_category != 'Other Resources':
                break
        
        return assigned_category
    
    def load_all_content(self):
        """Load all markdown files from parsed_content directory"""
        print(f"[*] Loading content from: {self.parsed_content_dir}")
        
        total_files = 0
        loaded_files = 0
        skipped_files = 0
        
        for domain_dir in sorted(self.parsed_content_dir.iterdir()):
            if not domain_dir.is_dir():
                continue
            
            domain = domain_dir.name
            
            for md_file in domain_dir.glob('*.md'):
                total_files += 1
                
                try:
                    with open(md_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Quality filter
                    if self.should_skip_file(md_file, content):
                        skipped_files += 1
                        continue
                    
                    # Store by domain
                    self.by_domain[domain].append({
                        'file': md_file.name,
                        'path': md_file,
                        'content': content,
                        'size': len(content)
                    })
                    
                    # Categorize
                    category = self.categorize_content(domain, md_file, content)
                    self.by_category[category].append({
                        'domain': domain,
                        'file': md_file.name,
                        'path': md_file,
                        'content': content,
                        'size': len(content)
                    })
                    
                    loaded_files += 1
                    
                except Exception as e:
                    print(f"[!] Error loading {md_file}: {str(e)}")
                    skipped_files += 1
        
        print(f"[+] Loaded {loaded_files} files from {len(self.by_domain)} domains")
        print(f"[+] Skipped {skipped_files} low-quality files")
        print(f"[+] Categorized into {len(self.by_category)} categories")
        
        return loaded_files
    
    def export_by_domain(self, output_file):
        """Export content organized by domain"""
        print(f"\n[*] Exporting domain-organized content...")
        
        md = f"# Research Content - Organized by Domain\n\n"
        md += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        md += f"**Total Domains:** {len(self.by_domain)}\n"
        md += f"**Total Documents:** {sum(len(docs) for docs in self.by_domain.values())}\n\n"
        md += "---\n\n"
        
        # Table of contents
        md += "## Table of Contents\n\n"
        for domain in sorted(self.by_domain.keys()):
            doc_count = len(self.by_domain[domain])
            md += f"- [{domain}](#{domain.replace('.', '')}) ({doc_count} documents)\n"
        md += "\n---\n\n"
        
        # Content by domain
        for domain in sorted(self.by_domain.keys()):
            docs = self.by_domain[domain]
            
            md += f"## {domain}\n\n"
            md += f"**Documents:** {len(docs)}\n\n"
            
            for doc in docs:
                md += f"### {doc['file']}\n\n"
                md += f"**Size:** {doc['size']:,} characters\n\n"
                md += "---\n\n"
                md += doc['content']
                md += "\n\n---\n\n"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(md)
        
        print(f"[+] Domain-organized export saved: {output_file}")
        print(f"    Size: {len(md):,} characters")
    
    def export_by_category(self, output_file):
        """Export content organized by category"""
        print(f"\n[*] Exporting category-organized content...")
        
        md = f"# Research Content - Organized by Category\n\n"
        md += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # Category summary
        md += "## Categories\n\n"
        for category in sorted(self.by_category.keys()):
            doc_count = len(self.by_category[category])
            total_size = sum(doc['size'] for doc in self.by_category[category])
            md += f"- **{category}**: {doc_count} documents ({total_size:,} characters)\n"
        md += "\n---\n\n"
        
        # Content by category
        for category in sorted(self.by_category.keys()):
            docs = self.by_category[category]
            
            md += f"# {category}\n\n"
            md += f"**Total Documents:** {len(docs)}\n\n"
            
            # Group by domain within category
            category_by_domain = defaultdict(list)
            for doc in docs:
                category_by_domain[doc['domain']].append(doc)
            
            for domain in sorted(category_by_domain.keys()):
                domain_docs = category_by_domain[domain]
                md += f"## {domain}\n\n"
                
                for doc in domain_docs:
                    md += f"### {doc['file']}\n\n"
                    md += doc['content']
                    md += "\n\n---\n\n"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(md)
        
        print(f"[+] Category-organized export saved: {output_file}")
        print(f"    Size: {len(md):,} characters")
    
    def export_curated_essentials(self, output_file):
        """Export only high-quality, essential content"""
        print(f"\n[*] Exporting curated essentials...")
        
        # Priority categories
        priority_categories = [
            'Official Documentation',
            'Technical Blogs',
            'Implementation Guides'
        ]
        
        md = f"# Research Content - Curated Essentials\n\n"
        md += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        md += "This document contains only high-quality, educational content from official sources and technical blogs.\n\n"
        md += "---\n\n"
        
        total_docs = 0
        
        for category in priority_categories:
            if category not in self.by_category:
                continue
            
            docs = self.by_category[category]
            md += f"# {category}\n\n"
            
            # Sort by size (larger = more comprehensive)
            docs_sorted = sorted(docs, key=lambda x: x['size'], reverse=True)
            
            for doc in docs_sorted[:20]:  # Top 20 per category
                md += f"## {doc['domain']} - {doc['file']}\n\n"
                md += doc['content']
                md += "\n\n---\n\n"
                total_docs += 1
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(md)
        
        print(f"[+] Curated essentials saved: {output_file}")
        print(f"    Documents: {total_docs}")
        print(f"    Size: {len(md):,} characters")
    
    def export_summary_report(self, output_file):
        """Export statistical summary of the research"""
        print(f"\n[*] Generating summary report...")
        
        md = f"# Research Content Summary\n\n"
        md += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # Overall statistics
        total_docs = sum(len(docs) for docs in self.by_domain.values())
        total_size = sum(sum(doc['size'] for doc in docs) for docs in self.by_domain.values())
        
        md += "## Overall Statistics\n\n"
        md += f"- **Total Domains:** {len(self.by_domain)}\n"
        md += f"- **Total Documents:** {total_docs}\n"
        md += f"- **Total Content Size:** {total_size:,} characters ({total_size / 1024 / 1024:.2f} MB)\n"
        md += f"- **Average Document Size:** {total_size / total_docs:,.0f} characters\n\n"
        
        # Top domains by document count
        md += "## Top Domains by Document Count\n\n"
        top_domains = sorted(self.by_domain.items(), key=lambda x: len(x[1]), reverse=True)[:20]
        
        for domain, docs in top_domains:
            total_size = sum(doc['size'] for doc in docs)
            md += f"- **{domain}**: {len(docs)} documents ({total_size:,} characters)\n"
        md += "\n"
        
        # Category breakdown
        md += "## Category Breakdown\n\n"
        for category in sorted(self.by_category.keys()):
            docs = self.by_category[category]
            total_size = sum(doc['size'] for doc in docs)
            md += f"### {category}\n\n"
            md += f"- Documents: {len(docs)}\n"
            md += f"- Total Size: {total_size:,} characters\n"
            md += f"- Average Size: {total_size / len(docs):,.0f} characters\n\n"
        
        # Largest documents
        md += "## Largest Documents\n\n"
        all_docs = []
        for domain, docs in self.by_domain.items():
            for doc in docs:
                all_docs.append({**doc, 'domain': domain})
        
        largest_docs = sorted(all_docs, key=lambda x: x['size'], reverse=True)[:20]
        
        for doc in largest_docs:
            md += f"- **{doc['domain']}/{doc['file']}**: {doc['size']:,} characters\n"
        md += "\n"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(md)
        
        print(f"[+] Summary report saved: {output_file}")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Research Content Reconstructor')
    parser.add_argument('research_dir', help='Research output directory (e.g., "research_output/Palo Alto NGFW")')
    parser.add_argument('--all', action='store_true', help='Export all formats')
    parser.add_argument('--by-domain', help='Export organized by domain')
    parser.add_argument('--by-category', help='Export organized by category')
    parser.add_argument('--curated', help='Export curated essentials only')
    parser.add_argument('--summary', help='Export summary report')
    
    args = parser.parse_args()
    
    research_dir = Path(args.research_dir)
    if not research_dir.exists():
        print(f"[!] Directory not found: {research_dir}")
        return
    
    print("=" * 60)
    print("Research Content Reconstructor")
    print("=" * 60)
    print(f"\n[*] Processing: {research_dir.name}\n")
    
    reconstructor = ResearchReconstructor(research_dir)
    
    # Load content
    loaded = reconstructor.load_all_content()
    
    if loaded == 0:
        print("[!] No content loaded. Check the directory structure.")
        return
    
    print(f"\n[*] Exporting...\n")
    
    # Export based on arguments
    if args.all:
        output_dir = research_dir / 'reconstructed'
        output_dir.mkdir(exist_ok=True)
        
        reconstructor.export_summary_report(output_dir / 'SUMMARY.md')
        reconstructor.export_curated_essentials(output_dir / 'CURATED_ESSENTIALS.md')
        reconstructor.export_by_category(output_dir / 'BY_CATEGORY.md')
        reconstructor.export_by_domain(output_dir / 'BY_DOMAIN.md')
        
        print(f"\n[+] All exports saved to: {output_dir}")
    else:
        if args.summary:
            reconstructor.export_summary_report(args.summary)
        if args.curated:
            reconstructor.export_curated_essentials(args.curated)
        if args.by_category:
            reconstructor.export_by_category(args.by_category)
        if args.by_domain:
            reconstructor.export_by_domain(args.by_domain)

if __name__ == '__main__':
    main()
