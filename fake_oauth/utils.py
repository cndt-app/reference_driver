from typing import Any
from urllib.parse import urlencode, urlparse


def add_query_to_url(url: str, query: dict[str, Any]) -> str:
    encoded_query = urlencode(query)
    url_parsed = urlparse(url)._replace(query=encoded_query)
    return url_parsed.geturl()
