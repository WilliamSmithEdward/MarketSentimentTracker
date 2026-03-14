"""
HTTP scraping module.
Standard implementation: requests.Session with timeout, redirect handling, explicit headers, and JSON response support.
"""

from __future__ import annotations

from typing import Any

import requests


DEFAULT_TIMEOUT_SECONDS = 30
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0.0.0 Safari/537.36"
)


class WebScraper:
    """
    Fetches raw HTML or JSON from a URL.
    """

    def __init__(
        self,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
        user_agent: str = DEFAULT_USER_AGENT,
    ) -> None:
        self._timeout_seconds = timeout_seconds
        self._session = requests.Session()
        self._session.headers.update(
            {
                "User-Agent": user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,application/json;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
            }
        )

    def get_html(self, url: str) -> str:
        """
        Executes an HTTP GET request and returns the response body as a string.
        """
        response = self._session.get(
            url,
            timeout=self._timeout_seconds,
            allow_redirects=True,
        )
        response.raise_for_status()
        return response.text

    def get_json(self, url: str) -> dict[str, Any]:
        """
        Executes an HTTP GET request and returns the response body as parsed JSON.
        """
        response = self._session.get(
            url,
            timeout=self._timeout_seconds,
            allow_redirects=True,
        )
        response.raise_for_status()
        return response.json()


def get_html(url: str, timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS) -> str:
    """
    Convenience function that fetches raw HTML from a URL.
    """
    scraper = WebScraper(timeout_seconds=timeout_seconds)
    return scraper.get_html(url)


def get_json(url: str, timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS) -> dict[str, Any]:
    """
    Convenience function that fetches JSON from a URL.
    """
    scraper = WebScraper(timeout_seconds=timeout_seconds)
    return scraper.get_json(url)