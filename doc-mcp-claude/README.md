# Documentation Gateway MCP Server

A comprehensive MCP (Model Context Protocol) server that acts as a gateway for coding agents (Claude Code, Codex, etc.) to retrieve library documentation, search code repositories, and access package metadata.

> **Note**: This server was developed and validated using the `@doc-mcp` server itself! See [DOC_MCP_RESEARCH.md](DOC_MCP_RESEARCH.md) for details on how the documentation tools helped create this documentation tool.

## Features

- **PyPI Metadata Retrieval**: Fetch package information, versions, and documentation links from PyPI
- **Google Search**: Search for library documentation across the web
- **GitHub Repository Search**: Find relevant repositories by language and topic
- **GitHub Code Search**: Search for specific code implementations across GitHub
- **Unified Library Documentation Search**: Combined search across multiple sources

## Available Tools

### 1. `search_library_docs`
Searches for library documentation across PyPI, Google, and GitHub in one command.

**Parameters:**
- `library` (string, required): The name of the library to search for
- `limit` (integer, optional): Maximum number of results (default: 5)

**Example:**
```json
{
  "library": "requests",
  "limit": 5
}
```

### 2. `pypi_metadata`
Retrieves comprehensive package information from PyPI.

**Parameters:**
- `package` (string, required): The name of the package on PyPI

**Example:**
```json
{
  "package": "numpy"
}
```

### 3. `google_search`
Performs a Google search for documentation and resources.

**Parameters:**
- `query` (string, required): The search query
- `limit` (integer, optional): Maximum number of results (default: 5)

**Example:**
```json
{
  "query": "Flask REST API tutorial",
  "limit": 10
}
```

### 4. `github_repo_search`
Searches GitHub repositories by topic and programming language.

**Parameters:**
- `query` (string, required): The search query
- `language` (string, optional): Programming language filter (default: "Python")
- `limit` (integer, optional): Maximum number of results (default: 5)

**Example:**
```json
{
  "query": "async web framework",
  "language": "Python",
  "limit": 10
}
```

### 5. `github_code_search`
Searches for specific code patterns across GitHub.

**Parameters:**
- `query` (string, required): The code search query
- `repo` (string, optional): Specific repository to scope search (e.g., "owner/repo")
- `limit` (integer, optional): Maximum number of results (default: 5)

**Example:**
```json
{
  "query": "async def handle_request",
  "repo": "aio-libs/aiohttp",
  "limit": 5
}
```

## Installation

### Prerequisites
- Python 3.8+
- pip

### Setup

1. Clone the repository and navigate to the project directory:
```bash
cd doc-mcp-claude
```

2. Create a Python virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. (Optional) Create a `.env` file for configuration:
```bash
cp .env.example .env
```

## Configuration

### Environment Variables

The server can be configured using environment variables in a `.env` file:

- `GITHUB_TOKEN`: GitHub API token for higher rate limits (optional)
- `GOOGLE_API_KEY`: Google Custom Search API key (optional)
- `GOOGLE_SEARCH_ENGINE_ID`: Google Custom Search Engine ID (optional)
- `LOG_LEVEL`: Logging level (default: INFO)

### Rate Limiting

- **GitHub API**: 60 requests/hour (unauthenticated), 5000 requests/hour (authenticated)
- **Google Search**: Requires API key for production use
- **PyPI**: No rate limits for API access

For production use with high volume, obtain API credentials:
1. GitHub: https://github.com/settings/tokens
2. Google Custom Search: https://cse.google.com/cse/

## Usage

### Starting the Server

```bash
# Using the startup script
./run.sh

# Or directly
source venv/bin/activate
python server.py
```

The server will start on the default MCP port and be ready to receive tool calls from connected agents.

### Integration with Claude Code

To integrate with Claude Code, configure it in your Claude Code settings or environment:

```bash
export MCP_SERVERS='{"doc-gateway": "python /path/to/server.py"}'
```

### Example Queries

#### Search for library documentation
```
Agent: "I need to learn about the requests library"
Server: Returns PyPI metadata, documentation links, and GitHub repositories
```

#### Find code examples
```
Agent: "Show me examples of async/await in aiohttp"
Server: Searches GitHub code and returns relevant implementations
```

#### Get package metadata
```
Agent: "What version of Django is currently available?"
Server: Queries PyPI and returns version, dependencies, and links
```

## Architecture

```
┌─────────────────────────────────────────┐
│     Coding Agent (Claude, Codex, etc)   │
└────────────┬────────────────────────────┘
             │
        MCP Protocol
             │
┌────────────▼────────────────────────────┐
│   Documentation Gateway MCP Server       │
├─────────────────────────────────────────┤
│  • search_library_docs                  │
│  • pypi_metadata                        │
│  • google_search                        │
│  • github_repo_search                   │
│  • github_code_search                   │
└────────────┬────────────────────────────┘
             │
     ┌───────┴────────┬──────────┬──────────┐
     │                │          │          │
     ▼                ▼          ▼          ▼
   PyPI           Google      GitHub     External
  Registry       Search        API       APIs
```

## Dependencies

- `mcp` (1.22.0): Model Context Protocol SDK
- `httpx` (>=0.28.0): Async HTTP client (researched & updated via @doc-mcp)
- `pydantic` (>=2.0.0): Data validation with Python type hints (new, researched via @doc-mcp)
- `beautifulsoup4` (>=4.12.0): HTML parsing
- `requests` (>=2.31.0): HTTP library
- `python-dotenv` (>=1.0.0): Environment variable management

**Research Note**: Dependencies were validated using the `@doc-mcp` server. See [DOC_MCP_RESEARCH.md](DOC_MCP_RESEARCH.md) for detailed findings on library versions and alternatives.

## Development

### Adding New Tools

To add a new tool, follow this pattern in `server.py`:

1. Add tool definition to `TOOLS` list
2. Implement async function matching tool parameters
3. Return `ToolResult` with `TextContent`
4. Add case to `call_tool()` function

Example:
```python
async def new_tool(param: str) -> ToolResult:
    """Tool description"""
    try:
        # Implementation
        return ToolResult(content=[TextContent(type="text", text=result)])
    except Exception as e:
        return ToolResult(content=[TextContent(type="text", text=f"Error: {str(e)}")])
```

### Testing

Run individual tools:
```python
import asyncio
from server import pypi_metadata

result = asyncio.run(pypi_metadata("requests"))
print(result)
```

## Troubleshooting

### Rate Limiting
If you encounter rate limit errors:
- For GitHub: Add `GITHUB_TOKEN` environment variable
- For Google: Consider implementing backoff or API key

### Connection Issues
- Verify internet connectivity
- Check firewall settings
- Ensure API endpoints are accessible

### Missing Dependencies
```bash
pip install --upgrade -r requirements.txt
```

## Security Considerations

- **API Keys**: Never commit `.env` files with real credentials
- **Rate Limiting**: Implement exponential backoff for API calls
- **Input Validation**: Server validates all tool parameters
- **Timeout Protection**: All HTTP requests have 10-second timeout

## Future Enhancements

- [ ] Caching layer for frequently accessed documentation
- [ ] Support for additional package managers (npm, Maven, Cargo)
- [ ] Real-time documentation updates
- [ ] Custom search engine integration
- [ ] Documentation summarization
- [ ] API rate limit management
- [ ] Support for private/enterprise repositories

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## Support

For issues, questions, or suggestions:
- GitHub Issues: [Create an issue](https://github.com/yourusername/doc-mcp/issues)
- Documentation: Check README.md and code comments
