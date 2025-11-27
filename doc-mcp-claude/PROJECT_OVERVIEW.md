# Documentation Gateway MCP Server - Project Overview

## Project Summary

The **Documentation Gateway MCP Server** is a comprehensive Model Context Protocol (MCP) server that serves as a gateway for coding agents (Claude Code, Codex, etc.) to retrieve library documentation, search code repositories, and access package metadata from multiple sources.

This server integrates with PyPI, Google Search, and GitHub APIs to provide a unified interface for documentation discovery and code exploration.

## Key Features

✅ **PyPI Package Metadata** - Fetch package versions, descriptions, and documentation links
✅ **Google Search Integration** - Search documentation across the web
✅ **GitHub Repository Search** - Find relevant repositories by language and topic
✅ **GitHub Code Search** - Search for specific code patterns and implementations
✅ **Unified Documentation Search** - Combined search across all sources
✅ **Async-first Architecture** - Non-blocking I/O for efficient API calls
✅ **Environment Configuration** - Easy setup with optional API authentication
✅ **Comprehensive Testing** - Test suite and usage examples included

## Project Structure

```
doc-mcp-claude/
├── server.py                 # Main MCP server implementation
├── requirements.txt          # Python dependencies
├── run.sh                   # Server startup script
├── test_server.py           # Comprehensive test suite
├── example_usage.py         # Usage examples
├── .env.example             # Environment configuration template
├── .gitignore               # Git ignore rules
├── README.md                # Full documentation
├── QUICKSTART.md            # Quick start guide
└── PROJECT_OVERVIEW.md      # This file
```

## Installation & Setup

### Step 1: Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment (Optional)
```bash
cp .env.example .env
# Edit .env to add GitHub token for higher API limits
```

### Step 4: Start the Server
```bash
./run.sh
# Or: source venv/bin/activate && python server.py
```

## Available Tools

### 1. Search Library Documentation
**search_library_docs** - Combined search across PyPI, Google, and GitHub

```json
{
  "library": "requests",
  "limit": 5
}
```

Returns comprehensive documentation information from all sources.

### 2. Get PyPI Metadata
**pypi_metadata** - Retrieve package information from PyPI

```json
{
  "package": "numpy"
}
```

Returns: version, summary, URLs, requirements, project links

### 3. Google Search
**google_search** - Search documentation using Google

```json
{
  "query": "FastAPI tutorial",
  "limit": 10
}
```

Returns: Search result links and information

### 4. GitHub Repository Search
**github_repo_search** - Find relevant repositories

```json
{
  "query": "async web framework",
  "language": "Python",
  "limit": 10
}
```

Returns: Repository name, description, stars, URL, language

### 5. GitHub Code Search
**github_code_search** - Search for code patterns

```json
{
  "query": "async def handle_request",
  "repo": "aio-libs/aiohttp",
  "limit": 5
}
```

Returns: File names, paths, repositories, URLs

## Technical Details

### Architecture
- **Framework**: MCP (Model Context Protocol) 1.22.0
- **Language**: Python 3.8+
- **HTTP Client**: httpx (async/await)
- **APIs**: PyPI, GitHub, Google
- **Pattern**: Async-first, non-blocking

### Dependencies
```
mcp==1.22.0                 # Model Context Protocol SDK
httpx>=0.24.0             # Async HTTP client
beautifulsoup4>=4.12.0    # HTML parsing
requests>=2.31.0          # HTTP library
python-dotenv>=1.0.0      # Environment variables
```

### API Integration

| Service | Endpoint | Rate Limit | Auth Required |
|---------|----------|-----------|---------------|
| PyPI | api.pypi.org/pypi | No limit | No |
| GitHub Repos | api.github.com/search/repositories | 60/hr (10,000/hr with token) | Optional |
| GitHub Code | api.github.com/search/code | 60/hr (10,000/hr with token) | Optional |
| Google | www.google.com | Limited | Optional (API key) |

## Testing

### Run Test Suite
```bash
source venv/bin/activate
python test_server.py
```

Tests include:
- PyPI metadata retrieval ✓
- GitHub repository search ✓
- Google search ✓
- Library documentation search ✓
- Code search (requires GitHub token)

### Run Examples
```bash
source venv/bin/activate
python example_usage.py
```

Demonstrates:
- Complete library searches
- Package comparisons
- Repository discovery
- Code pattern examples
- Best practice repositories

## Configuration

### Environment Variables

Create `.env` file with:

```
# GitHub API token (optional, for higher rate limits)
GITHUB_TOKEN=your_github_token

# Google API credentials (optional)
GOOGLE_API_KEY=your_google_api_key
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id

# Logging level
LOG_LEVEL=INFO
```

### Getting API Keys

1. **GitHub Token**
   - Go to: https://github.com/settings/tokens
   - Create "Personal access token"
   - No specific scopes needed for public code search
   - Enables 5000 requests/hour instead of 60

2. **Google Custom Search API**
   - Go to: https://cse.google.com/cse/
   - Create a custom search engine
   - Get API key from Google Cloud Console
   - Optional, for web search enhancement

## Integration Examples

### With Claude Code

```bash
export MCP_SERVERS='{"doc-gateway": "python /path/to/server.py"}'
```

Then use in Claude Code:
```
"Find me documentation for the requests library"
→ Calls search_library_docs("requests")

"What version of Django is available?"
→ Calls pypi_metadata("Django")

"Show me examples of async patterns in Python"
→ Calls github_repo_search("async patterns")
```

### Programmatic Usage

```python
import asyncio
from server import pypi_metadata

result = asyncio.run(pypi_metadata("requests"))
print(result.content[0].text)
```

## API Response Examples

### PyPI Metadata Response
```json
{
  "name": "requests",
  "version": "2.32.5",
  "summary": "Python HTTP for Humans.",
  "home_page": "https://requests.readthedocs.io",
  "project_urls": {
    "Documentation": "https://requests.readthedocs.io",
    "Source": "https://github.com/psf/requests"
  }
}
```

### GitHub Repository Response
```json
{
  "name": "fastapi",
  "full_name": "tiangolo/fastapi",
  "description": "FastAPI framework, high performance, easy to learn",
  "url": "https://github.com/tiangolo/fastapi",
  "stars": 92416,
  "language": "Python"
}
```

## Performance Considerations

### Rate Limiting
- **PyPI**: No rate limits for public packages
- **GitHub**: 60 requests/hour (unauthenticated), 5000/hour (authenticated)
- **Google**: Depends on API plan

### Optimization Tips
1. Add GitHub token to double API limits
2. Cache frequently accessed results
3. Implement exponential backoff for retries
4. Use repository-scoped GitHub code searches
5. Batch requests when possible

## Security

✓ **Input Validation** - All tool parameters validated
✓ **Timeout Protection** - 10-second timeout on all HTTP requests
✓ **No Credentials in Code** - Uses environment variables
✓ **HTTPS Only** - All API calls use HTTPS
✓ **API Key Protection** - Never commit .env files

## Troubleshooting

### GitHub Code Search Returns 401
**Solution**: Add GitHub token to .env
```
GITHUB_TOKEN=your_token_here
```

### Rate Limit Errors
**Solutions**:
- Wait before making more requests (implement backoff)
- Add authentication tokens for higher limits
- Reduce result limit parameter

### Network Timeout Errors
**Solutions**:
- Check internet connectivity
- Verify firewall allows HTTPS
- Test API endpoints manually
- Increase timeout if needed (modify server.py)

## Future Enhancements

- [ ] Caching layer with Redis/SQLite
- [ ] Support for npm packages
- [ ] Support for Maven/Java packages
- [ ] Support for Cargo/Rust packages
- [ ] Real-time documentation monitoring
- [ ] Documentation summarization with AI
- [ ] Advanced filtering and ranking
- [ ] Custom search engine integration
- [ ] API rate limit tracking
- [ ] Webhook support for real-time updates
- [ ] GraphQL API support
- [ ] OpenAPI specification parsing

## Development

### Adding New Tools

1. Define tool in `TOOLS` list with schema
2. Implement async handler function
3. Add case to `call_tool()` dispatcher
4. Return `CallToolResult` with content

### Code Organization
- `server.py:26-120` - Tool definitions and server setup
- `server.py:125-160` - Tool dispatching
- `server.py:160-330` - Tool implementations

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Submit pull request

## License

MIT License - See LICENSE file

## Support

### Documentation
- **README.md** - Comprehensive documentation
- **QUICKSTART.md** - Quick setup guide
- **example_usage.py** - Practical examples
- **test_server.py** - Test cases

### Issues & Questions
- Check documentation first
- Review test cases for examples
- Run test_server.py for troubleshooting
- Check GitHub issues

## Version History

### v1.0.0 (Current)
- Initial release
- PyPI metadata retrieval
- GitHub repository search
- GitHub code search
- Google search integration
- Async-first implementation
- Comprehensive documentation

## Statistics

- **Tools**: 5 available
- **API Integrations**: 3 (PyPI, GitHub, Google)
- **Code Lines**: ~330
- **Test Coverage**: Comprehensive
- **Documentation**: Complete

## Quick Links

- PyPI: https://pypi.org/
- GitHub: https://github.com/
- GitHub API: https://docs.github.com/en/rest
- MCP Protocol: https://modelcontextprotocol.io/
