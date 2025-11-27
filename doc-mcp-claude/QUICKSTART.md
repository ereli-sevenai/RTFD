# Quick Start Guide - Documentation Gateway MCP Server

## Installation (5 minutes)

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) Set up environment variables
cp .env.example .env
# Edit .env to add GitHub token if needed for higher API limits
```

## Run the Server

```bash
# Option 1: Using the startup script
./run.sh

# Option 2: Direct execution
source venv/bin/activate
python server.py
```

## Test the Server

```bash
# In another terminal, run the test suite
source venv/bin/activate
python test_server.py
```

## Available Tools

### 1. Search Library Documentation
Get comprehensive information about any Python library:

```json
{
  "tool": "search_library_docs",
  "params": {
    "library": "requests",
    "limit": 5
  }
}
```

**Returns:**
- PyPI metadata
- Google search results
- GitHub repositories

### 2. Get PyPI Package Info
Retrieve package details directly from PyPI:

```json
{
  "tool": "pypi_metadata",
  "params": {
    "package": "numpy"
  }
}
```

**Returns:**
- Package name and version
- Summary and description
- Documentation links
- Project URLs
- Python version requirements

### 3. Search the Web
Search for documentation and resources:

```json
{
  "tool": "google_search",
  "params": {
    "query": "FastAPI tutorial beginners",
    "limit": 10
  }
}
```

### 4. Find Code Examples
Search for repositories implementing specific features:

```json
{
  "tool": "github_repo_search",
  "params": {
    "query": "async HTTP client",
    "language": "Python",
    "limit": 10
  }
}
```

**Returns:**
- Repository name and description
- Star count
- GitHub URL
- Primary language

### 5. Search Code Examples
Find specific code patterns and implementations:

```json
{
  "tool": "github_code_search",
  "params": {
    "query": "async def handle_request",
    "repo": "aio-libs/aiohttp",
    "limit": 5
  }
}
```

**Note:** Requires GitHub API token for authentication

## Integration with Claude Code

Add to your Claude Code settings:

```bash
# In your shell environment
export MCP_SERVERS='{"doc-gateway": "python /path/to/server.py"}'
```

Then use the tools from within Claude Code!

## Common Use Cases

### Find documentation for a new library
```
Agent: "Show me documentation for the pandas library"
→ Uses: search_library_docs("pandas")
```

### Get current package version
```
Agent: "What's the latest version of Django?"
→ Uses: pypi_metadata("Django")
```

### Find code examples
```
Agent: "Show me examples of async/await patterns"
→ Uses: github_repo_search("async patterns", "Python")
```

### Search for specific implementations
```
Agent: "How do I implement authentication in FastAPI?"
→ Uses: github_code_search("def authenticate", repo="tiangolo/fastapi")
```

## Troubleshooting

### GitHub Code Search Returns 401 Error
**Solution:** Add your GitHub token to `.env`:
```
GITHUB_TOKEN=your_github_token_here
```

Get a token at: https://github.com/settings/tokens

### High API Rate Limiting
**Solutions:**
1. Add GitHub token (60 → 5000 requests/hour)
2. Add Google API key for better search results
3. Implement caching layer

### Network Connectivity Issues
- Check internet connection
- Verify firewalls allow HTTPS
- Try API endpoints manually to test connectivity

## Next Steps

- Customize tools for your needs
- Add caching layer for frequently accessed data
- Integrate with your coding agent
- Set up CI/CD for automated documentation updates

## Support

For issues or questions:
- Check README.md for detailed documentation
- Review code comments in server.py
- Test with test_server.py script
