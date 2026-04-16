"""Web tools for the DeepAgents adapter — web search and URL fetching."""

from __future__ import annotations


def create_web_search_tool():
    """Create and return a LangChain tool for web search via Tavily.

    The tool reads TAVILY_API_KEY from the environment at call time (lazy).

    Returns:
        A LangChain @tool function named 'web_search'.
    """
    from langchain_core.tools import tool

    @tool
    def web_search(query: str) -> str:
        """Search the web for information about a topic.

        Args:
            query: The search query string.

        Returns:
            Formatted search results with title, URL, and content snippet,
            or an error message if the search fails.
        """
        import os

        from tavily import TavilyClient

        api_key = os.environ.get("TAVILY_API_KEY")
        if not api_key:
            return (
                "Error: TAVILY_API_KEY not configured. "
                "Set TAVILY_API_KEY environment variable to enable web search."
            )

        try:
            import json

            client = TavilyClient(api_key=api_key)
            response = client.search(query, max_results=5)
            results = response.get("results", [])

            if not results:
                return f"No results found for: {query}"

            # Return JSON so the TUI widget can use its rich web-search formatter
            payload = {
                "query": query,
                "results": [
                    {
                        "title": r.get("title", ""),
                        "url": r.get("url", ""),
                        "content": r.get("content", ""),
                    }
                    for r in results
                ],
            }
            return json.dumps(payload)
        except Exception as e:
            return f"Search error: {str(e)}"

    return web_search


def create_fetch_url_tool():
    """Create and return a LangChain tool for fetching and converting URLs to markdown.

    Uses httpx for HTTP requests and markdownify for HTML-to-markdown conversion.

    Returns:
        A LangChain @tool function named 'fetch_url'.
    """
    from langchain_core.tools import tool

    @tool
    def fetch_url(url: str) -> str:
        """Fetch the content of a URL and convert it to markdown text.

        Args:
            url: The URL to fetch.

        Returns:
            The page content as markdown text (truncated to 10000 chars),
            or an error message if the fetch fails.
        """
        try:
            import json

            import httpx
            from markdownify import markdownify

            response = httpx.get(url, timeout=30, follow_redirects=True)
            response.raise_for_status()
            markdown = markdownify(response.text)[:10000]
            # Return JSON so the TUI widget can use its rich fetch-url formatter
            return json.dumps({"url": url, "markdown_content": markdown})
        except httpx.HTTPStatusError as e:
            return f"Error fetching {url}: HTTP {e.response.status_code}"
        except Exception as e:
            return f"Error fetching {url}: {str(e)}"

    return fetch_url
