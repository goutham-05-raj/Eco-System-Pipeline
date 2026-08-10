from __future__ import annotations
from urllib.parse import urlparse, urlunparse, urlencode, parse_qsl


def normalise_url(url: str) -> str:
    """
    Canonical URL form:
    - lowercase scheme + host
    - sorted query params
    - fragment stripped
    """
    url = url.strip()
    parsed = urlparse(url)
    qs = urlencode(sorted(parse_qsl(parsed.query)))
    normalised = urlunparse((
        parsed.scheme.lower(),
        parsed.netloc.lower(),
        parsed.path,
        parsed.params,
        qs,
        "",   # strip fragment
    ))
    return normalised


def extract_domain(url: str) -> str:
    """Return just the netloc (e.g. 'openai.com')."""
    return urlparse(url).netloc.lower().lstrip("www.")
