#!/usr/bin/env python3
"""
Example usage of the Documentation Gateway MCP Server
Shows practical examples of using each tool
"""

import asyncio
import json
from server import (
    pypi_metadata,
    google_search,
    github_repo_search,
    github_code_search,
    search_library_docs
)


async def example_1_search_library():
    """Example 1: Search for complete library documentation"""
    print("\n" + "="*70)
    print("EXAMPLE 1: Complete Library Documentation Search")
    print("="*70)

    library = "flask"
    print(f"\nSearching documentation for: {library}\n")

    result = await search_library_docs(library, limit=3)
    if result.content:
        print(result.content[0].text)


async def example_2_get_package_info():
    """Example 2: Get specific package information"""
    print("\n" + "="*70)
    print("EXAMPLE 2: Get Package Metadata from PyPI")
    print("="*70)

    packages = ["requests", "django", "fastapi"]

    for package in packages:
        print(f"\n📦 Package: {package}")
        result = await pypi_metadata(package)
        if result.content:
            data = json.loads(result.content[0].text)
            print(f"   Version: {data['version']}")
            print(f"   Summary: {data['summary']}")
            if data.get('home_page'):
                print(f"   Home Page: {data['home_page']}")


async def example_3_find_repositories():
    """Example 3: Find relevant repositories"""
    print("\n" + "="*70)
    print("EXAMPLE 3: Find Relevant Repositories")
    print("="*70)

    queries = [
        ("web scraping", "Python"),
        ("machine learning", "Python"),
        ("REST API", "Python")
    ]

    for query, language in queries:
        print(f"\n🔍 Searching: {query} (Language: {language})")
        result = await github_repo_search(query, language, limit=2)

        if result.content:
            repos = json.loads(result.content[0].text)
            for repo in repos[:2]:
                print(f"\n   • {repo['name']}")
                print(f"     ⭐ Stars: {repo['stars']}")
                print(f"     📝 {repo['description']}")
                print(f"     🔗 {repo['url']}")


async def example_4_find_code_patterns():
    """Example 4: Find specific code patterns"""
    print("\n" + "="*70)
    print("EXAMPLE 4: Find Code Patterns")
    print("="*70)

    print("\nSearching for context manager implementation:")
    result = await github_code_search("class __enter__", limit=2)

    if result.content:
        try:
            items = json.loads(result.content[0].text)
            for item in items[:2]:
                print(f"\n   📄 {item['name']}")
                print(f"      Path: {item['path']}")
                print(f"      Repository: {item['repository']}")
                print(f"      URL: {item['url']}")
        except json.JSONDecodeError:
            print(f"   Note: {result.content[0].text}")


async def example_5_compare_packages():
    """Example 5: Compare different packages"""
    print("\n" + "="*70)
    print("EXAMPLE 5: Compare Web Frameworks")
    print("="*70)

    frameworks = ["flask", "django", "fastapi"]

    print("\nComparing Python web frameworks:\n")

    for framework in frameworks:
        result = await pypi_metadata(framework)
        if result.content:
            data = json.loads(result.content[0].text)
            print(f"📦 {data['name'].upper()}")
            print(f"   Latest Version: {data['version']}")
            print(f"   {data['summary']}")
            print()


async def example_6_find_best_practice_repos():
    """Example 6: Find repositories with best practices"""
    print("\n" + "="*70)
    print("EXAMPLE 6: Find Best Practice Repositories")
    print("="*70)

    queries = [
        "best practices testing Python",
        "production ready async",
        "scalable architecture",
    ]

    for query in queries:
        print(f"\n🎯 Finding: {query}")
        result = await github_repo_search(query, "Python", limit=1)

        if result.content:
            repos = json.loads(result.content[0].text)
            if repos:
                repo = repos[0]
                print(f"   ✓ {repo['name']}")
                print(f"     Description: {repo['description']}")
                print(f"     URL: {repo['url']}")


async def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("Documentation Gateway MCP Server - Usage Examples")
    print("="*70)

    try:
        # Run examples
        await example_1_search_library()
        await example_2_get_package_info()
        await example_3_find_repositories()
        await example_4_find_code_patterns()
        await example_5_compare_packages()
        await example_6_find_best_practice_repos()

        print("\n" + "="*70)
        print("✅ All examples completed successfully!")
        print("="*70 + "\n")

    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
