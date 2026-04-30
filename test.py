#!/usr/bin/env python3
"""
Test script for Research Gatherer
Runs a simple test to verify installation and basic functionality
"""

import os
import sys
import shutil

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    try:
        import requests
        print("✓ requests")
    except ImportError:
        print("✗ requests - Install with: pip install requests")
        return False
    
    try:
        import bs4
        print("✓ beautifulsoup4")
    except ImportError:
        print("✗ beautifulsoup4 - Install with: pip install beautifulsoup4")
        return False
    
    try:
        import lxml
        print("✓ lxml")
    except ImportError:
        print("✗ lxml - Install with: pip install lxml")
        return False
    
    print("\nAll required modules imported successfully!\n")
    return True

def test_search(keyword="test search"):
    """Test basic search functionality"""
    print(f"Testing search with keyword: '{keyword}'")
    
    try:
        # Import after we know dependencies are installed
        sys.path.insert(0, os.path.dirname(__file__))
        from research_gatherer import ResearchGatherer
        
        # Create test output directory
        test_dir = "test_output"
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
        
        gatherer = ResearchGatherer(output_dir=test_dir, debug_mode=True)
        
        print("\n✓ ResearchGatherer initialized")
        
        # Test search (will be fast as it just collects links)
        print(f"\nSearching for '{keyword}'...")
        gatherer.search_and_collect([keyword])
        
        # Check if links were collected
        links = gatherer.link_manager.get_all_links()
        if links:
            print(f"✓ Collected {len(links)} links")
            print("\nSample links:")
            for link in links[:5]:
                print(f"  - {link}")
            if len(links) > 5:
                print(f"  ... and {len(links) - 5} more")
        else:
            print("⚠ No links collected (this may be normal if engines are blocked)")
        
        print(f"\n✓ Search test completed!")
        print(f"  Links saved to: {test_dir}/collected_links.txt")
        
        # Clean up
        cleanup = input("\nDelete test output? (y/n): ").lower()
        if cleanup == 'y':
            shutil.rmtree(test_dir)
            print("✓ Test output deleted")
        else:
            print(f"Test output preserved in: {test_dir}/")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error during search test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_jina_parser():
    """Test Jina parser with a sample URL"""
    print("\nTesting Jina AI Parser...")
    
    try:
        sys.path.insert(0, os.path.dirname(__file__))
        from research_gatherer import JinaParser
        
        parser = JinaParser()
        test_url = "https://example.com"
        
        print(f"Parsing: {test_url}")
        content = parser.parse_url(test_url)
        
        if content:
            print(f"✓ Successfully parsed {len(content)} characters")
            title = parser.extract_title(content)
            if title:
                print(f"  Title: {title}")
            print(f"\nFirst 200 characters:")
            print(content[:200])
            return True
        else:
            print("✗ Failed to parse URL")
            return False
            
    except Exception as e:
        print(f"✗ Error during parser test: {e}")
        return False

def main():
    print("=" * 60)
    print("Research Gatherer - Test Suite")
    print("=" * 60)
    print()
    
    # Test 1: Imports
    if not test_imports():
        print("\n❌ Import test failed!")
        print("Install dependencies with: pip install -r requirements.txt")
        return False
    
    # Ask user if they want to continue with network tests
    cont = input("Imports successful! Run network tests? (y/n): ").lower()
    if cont != 'y':
        print("\nSkipping network tests. All done!")
        return True
    
    # Test 2: Search
    print("\n" + "=" * 60)
    keyword = input("Enter test keyword (press Enter for 'test search'): ").strip()
    if not keyword:
        keyword = "test search"
    
    if not test_search(keyword):
        print("\n❌ Search test failed!")
        return False
    
    # Test 3: Jina Parser
    print("\n" + "=" * 60)
    test_parse = input("\nTest Jina Parser? (y/n): ").lower()
    if test_parse == 'y':
        if not test_jina_parser():
            print("\n⚠ Parser test had issues (may be temporary)")
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("\nReady to use! Try:")
    print("  python research_gatherer.py -k 'your keyword' --auto-parse")
    print("=" * 60)
    
    return True

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(0)
