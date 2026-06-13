# web-mcp

Puppeteer/Playwright-based web browsing MCP server.
Exposes a REST API for page extraction used by WebBrowseTool.

TODO: implement Node.js Express server with endpoints:
- POST /browse  → extract full page content from URL
- GET  /status  → health check
