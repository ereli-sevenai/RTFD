#!/usr/bin/env python3
"""
Documentation Gateway MCP Server
Provides tools for retrieving library documentation, searching code, and accessing PyPI metadata
"""

import json
import httpx
import os
from typing import Any, Optional, List
from mcp.server import Server
from mcp.types import Tool, TextContent, CallToolResult
import logging
from dotenv import load_dotenv
from pydantic import BaseModel, Field, validator

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration constants
REQUEST_TIMEOUT = 10.0
DEFAULT_RESULT_LIMIT = 5
MAX_RESULT_LIMIT = 100

# Get GitHub token from environment (optional)
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# ============================================================================
# Pydantic Models for Type Validation
# ============================================================================

class SearchRequest(BaseModel):
    """Request model for library search"""
    query: str = Field(..., min_length=1, max_length=200)
    limit: int = Field(5, ge=1, le=MAX_RESULT_LIMIT)

class PackageRequest(BaseModel):
    """Request model for package metadata"""
    package: str = Field(..., min_length=1, max_length=200)

class RepositorySearchRequest(BaseModel):
    """Request model for repository search"""
    query: str = Field(..., min_length=1, max_length=200)
    language: str = Field("Python", min_length=1, max_length=50)
    limit: int = Field(5, ge=1, le=MAX_RESULT_LIMIT)

class CodeSearchRequest(BaseModel):
    """Request model for code search"""
    query: str = Field(..., min_length=1, max_length=200)
    repo: Optional[str] = Field(None, max_length=200)
    limit: int = Field(5, ge=1, le=MAX_RESULT_LIMIT)

class PackageInfo(BaseModel):
    """Package information model"""
    name: str
    version: str
    summary: Optional[str] = None
    home_page: Optional[str] = None
    project_urls: dict = {}
    requires_python: Optional[str] = None

class Repository(BaseModel):
    """Repository information model"""
    name: str
    full_name: str
    description: Optional[str] = None
    url: str
    stars: int = 0
    language: Optional[str] = None

# Initialize MCP server
server = Server("doc-gateway")

# Tool definitions
TOOLS = [
    {
        "name": "search_library_docs",
        "description": "Search for library documentation using search engines and GitHub",
        "inputSchema": {
            "type": "object",
            "properties": {
                "library": {
                    "type": "string",
                    "description": "The name of the library to search for"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results to return",
                    "default": 5
                }
            },
            "required": ["library"]
        }
    },
    {
        "name": "pypi_metadata",
        "description": "Retrieve package metadata from PyPI including documentation URLs",
        "inputSchema": {
            "type": "object",
            "properties": {
                "package": {
                    "type": "string",
                    "description": "The name of the package on PyPI"
                }
            },
            "required": ["package"]
        }
    },
    {
        "name": "google_search",
        "description": "Search documentation using Google search",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results to return",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "github_repo_search",
        "description": "Search GitHub repositories relevant to a library or topic",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query"
                },
                "language": {
                    "type": "string",
                    "description": "Programming language filter (e.g., Python, JavaScript)",
                    "default": "Python"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results to return",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "github_code_search",
        "description": "Search GitHub code (optionally scoped to a repository)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query"
                },
                "repo": {
                    "type": "string",
                    "description": "Optional repository name to scope the search (e.g., 'owner/repo')"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results to return",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    }
]


@server.list_tools()
async def list_tools():
    """List available tools"""
    return [Tool(name=t["name"], description=t["description"], inputSchema=t["inputSchema"]) for t in TOOLS]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> CallToolResult:
    """Handle tool calls"""
    try:
        if name == "search_library_docs":
            return await search_library_docs(arguments.get("library"), arguments.get("limit", 5))
        elif name == "pypi_metadata":
            return await pypi_metadata(arguments.get("package"))
        elif name == "google_search":
            return await google_search(arguments.get("query"), arguments.get("limit", 5))
        elif name == "github_repo_search":
            return await github_repo_search(
                arguments.get("query"),
                arguments.get("language", "Python"),
                arguments.get("limit", 5)
            )
        elif name == "github_code_search":
            return await github_code_search(
                arguments.get("query"),
                arguments.get("repo"),
                arguments.get("limit", 5)
            )
        else:
            return CallToolResult(content=[TextContent(type="text", text=f"Unknown tool: {name}")])
    except Exception as e:
        logger.error(f"Error calling tool {name}: {e}")
        return CallToolResult(content=[TextContent(type="text", text=f"Error: {str(e)}")])


async def search_library_docs(library: str, limit: int = 5) -> CallToolResult:
    """Search for library documentation"""
    try:
        results = []

        # Try PyPI first
        pypi_result = await pypi_metadata(library)
        if pypi_result.content:
            results.append(f"PyPI: {pypi_result.content[0].text}")

        # Then search Google
        google_result = await google_search(f"{library} documentation", limit)
        if google_result.content:
            results.append(f"Google Search: {google_result.content[0].text}")

        # Then search GitHub
        github_result = await github_repo_search(library, "Python", limit)
        if github_result.content:
            results.append(f"GitHub Repos: {github_result.content[0].text}")

        content = "\n\n".join(results) if results else f"No documentation found for {library}"
        return CallToolResult(content=[TextContent(type="text", text=content)])
    except Exception as e:
        logger.error(f"Error searching library docs for {library}: {e}")
        return CallToolResult(content=[TextContent(type="text", text=f"Error searching library docs: {str(e)}")])


async def pypi_metadata(package: str) -> CallToolResult:
    """Retrieve PyPI package metadata"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://pypi.org/pypi/{package}/json",
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            data = response.json()

            info = data.get("info", {})
            try:
                pkg = PackageInfo(
                    name=info.get("name", "unknown"),
                    version=info.get("version", "unknown"),
                    summary=info.get("summary"),
                    home_page=info.get("home_page"),
                    project_urls=info.get("project_urls", {}),
                    requires_python=info.get("requires_python")
                )
                result = pkg.model_dump(exclude_none=True)
            except Exception as e:
                logger.warning(f"Failed to validate package info: {e}")
                result = info

            return CallToolResult(content=[TextContent(type="text", text=json.dumps(result, indent=2))])
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return CallToolResult(content=[TextContent(type="text", text=f"Package '{package}' not found on PyPI")])
        raise
    except Exception as e:
        logger.error(f"Error fetching PyPI metadata for {package}: {e}")
        return CallToolResult(content=[TextContent(type="text", text=f"Error fetching PyPI metadata: {str(e)}")])


async def google_search(query: str, limit: int = 5) -> CallToolResult:
    """Search using Google (via custom search or scraping)"""
    try:
        async with httpx.AsyncClient() as client:
            # Using a simple approach with search query parameters
            search_url = "https://www.google.com/search"
            params = {
                "q": query,
                "num": limit
            }

            # Note: Direct Google scraping has limitations. For production use,
            # consider using Google Custom Search API or a dedicated search service
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }

            response = await client.get(search_url, params=params, headers=headers, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()

            # Return raw response for now - in production, would parse HTML
            return CallToolResult(content=[TextContent(
                type="text",
                text=f"Search for '{query}' completed. Visit: https://www.google.com/search?q={query.replace(' ', '+')}"
            )])
    except Exception as e:
        logger.error(f"Error during Google search: {e}")
        return CallToolResult(content=[TextContent(type="text", text=f"Error during Google search: {str(e)}")])


async def github_repo_search(query: str, language: str = "Python", limit: int = 5) -> CallToolResult:
    """Search GitHub repositories"""
    try:
        async with httpx.AsyncClient() as client:
            search_url = "https://api.github.com/search/repositories"
            params = {
                "q": f"{query} language:{language}",
                "sort": "stars",
                "order": "desc",
                "per_page": limit
            }

            headers = {}
            if GITHUB_TOKEN:
                headers["Authorization"] = f"token {GITHUB_TOKEN}"

            response = await client.get(search_url, params=params, headers=headers, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()

            repos = []
            for item in data.get("items", []):
                try:
                    repo = Repository(
                        name=item.get("name"),
                        full_name=item.get("full_name"),
                        description=item.get("description"),
                        url=item.get("html_url"),
                        stars=item.get("stargazers_count", 0),
                        language=item.get("language")
                    )
                    repos.append(repo.model_dump())
                except Exception as e:
                    logger.warning(f"Failed to parse repository: {e}")
                    continue

            return CallToolResult(content=[TextContent(type="text", text=json.dumps(repos, indent=2))])
    except Exception as e:
        logger.error(f"Error searching GitHub repositories: {e}")
        return CallToolResult(content=[TextContent(type="text", text=f"Error searching GitHub: {str(e)}")])


async def github_code_search(query: str, repo: str = None, limit: int = 5) -> CallToolResult:
    """Search GitHub code"""
    try:
        async with httpx.AsyncClient() as client:
            search_url = "https://api.github.com/search/code"
            search_query = query
            if repo:
                search_query += f" repo:{repo}"

            params = {
                "q": search_query,
                "per_page": limit
            }

            headers = {}
            if GITHUB_TOKEN:
                headers["Authorization"] = f"token {GITHUB_TOKEN}"

            response = await client.get(search_url, params=params, headers=headers, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()

            results = []
            for item in data.get("items", []):
                result_info = {
                    "name": item.get("name"),
                    "path": item.get("path"),
                    "repository": item.get("repository", {}).get("full_name"),
                    "url": item.get("html_url")
                }
                results.append(result_info)

            return CallToolResult(content=[TextContent(type="text", text=json.dumps(results, indent=2))])
    except Exception as e:
        logger.error(f"Error searching GitHub code: {e}")
        return CallToolResult(content=[TextContent(type="text", text=f"Error searching GitHub code: {str(e)}")])


async def main():
    """Run the MCP server"""
    async with server:
        logger.info("Documentation Gateway MCP Server started")
        await server.wait_for_shutdown()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
