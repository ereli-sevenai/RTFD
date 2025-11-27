#!/usr/bin/env python3
"""
Test script for Documentation Gateway MCP Server
Demonstrates and verifies all available tools
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


async def test_pypi():
    """Test PyPI metadata retrieval"""
    print("\n" + "="*60)
    print("TEST: PyPI Metadata Retrieval")
    print("="*60)

    packages = ["requests", "numpy", "flask"]

    for package in packages:
        print(f"\nFetching metadata for: {package}")
        result = await pypi_metadata(package)
        if result.content:
            content = result.content[0].text
            print(f"Result:\n{content[:200]}...")


async def test_github_repos():
    """Test GitHub repository search"""
    print("\n" + "="*60)
    print("TEST: GitHub Repository Search")
    print("="*60)

    queries = ["async web framework", "data science", "testing framework"]

    for query in queries:
        print(f"\nSearching repositories for: {query}")
        result = await github_repo_search(query, "Python", 3)
        if result.content:
            content = result.content[0].text
            data = json.loads(content)
            for repo in data[:2]:
                print(f"  - {repo.get('name')} ({repo.get('stars')} stars)")
                print(f"    {repo.get('description')}")


async def test_github_code():
    """Test GitHub code search"""
    print("\n" + "="*60)
    print("TEST: GitHub Code Search")
    print("="*60)

    queries = ["async def", "def __init__", "class Request"]

    for query in queries:
        print(f"\nSearching code for: {query}")
        result = await github_code_search(query, None, 2)
        if result.content:
            content = result.content[0].text
            try:
                data = json.loads(content)
                for item in data[:2]:
                    print(f"  - {item.get('name')} in {item.get('repository')}")
            except json.JSONDecodeError:
                print(f"  Result: {content[:100]}")


async def test_google_search():
    """Test Google search"""
    print("\n" + "="*60)
    print("TEST: Google Search")
    print("="*60)

    queries = ["Python requests library", "FastAPI documentation", "Django REST framework"]

    for query in queries:
        print(f"\nSearching for: {query}")
        result = await google_search(query, 3)
        if result.content:
            print(f"  Result: {result.content[0].text[:100]}...")


async def test_library_search():
    """Test combined library documentation search"""
    print("\n" + "="*60)
    print("TEST: Combined Library Documentation Search")
    print("="*60)

    libraries = ["requests", "fastapi"]

    for library in libraries:
        print(f"\nSearching documentation for: {library}")
        result = await search_library_docs(library, 3)
        if result.content:
            print(f"  Result: {result.content[0].text[:200]}...")


async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("Documentation Gateway MCP Server - Test Suite")
    print("="*60)

    try:
        await test_pypi()
        await test_github_repos()
        await test_github_code()
        await test_google_search()
        await test_library_search()

        print("\n" + "="*60)
        print("All tests completed successfully!")
        print("="*60 + "\n")

    except Exception as e:
        print(f"\nError during testing: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
