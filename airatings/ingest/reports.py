import re
import calendar
import logging
import datetime

import feedparser
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

_TIMEOUT = 10
_ARTICLE_TIMEOUT = 8
_MIN_SUMMARY_LEN = 300   # below this we try to fetch the full article
_MAX_ARTICLE_CHARS = 3000

_ARTICLE_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; SIWSBot/1.0; +https://shouldiwatchsports.com)"
    ),
    "Accept": "text/html,application/xhtml+xml",
}

# Tags whose text content we join to build the article body
_BODY_TAGS = {"p", "h2", "h3", "li"}

# Domains known to require login / hard paywall — skip fetch attempt
_SKIP_FETCH_DOMAINS = {"theathletic.com", "ft.com", "wsj.com"}


def _entry_dt(entry) -> datetime.datetime | None:
    """Return a UTC-aware datetime from a feedparser entry, or None."""
    t = getattr(entry, "published_parsed", None) or getattr(entry, "updated_parsed", None)
    if t is None:
        return None
    ts = calendar.timegm(t)
    return datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc)


def _clean(text: str) -> str:
    """Strip HTML tags and collapse whitespace."""
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _matches(entry, keywords: list[str]) -> bool:
    """True if title+summary contains ALL keywords (case-insensitive)."""
    haystack = (
        _clean(getattr(entry, "title", "")) + " " +
        _clean(getattr(entry, "summary", ""))
    ).lower()
    return all(kw.lower() in haystack for kw in keywords)


def _fetch_article_text(url: str) -> str | None:
    """
    Attempt to fetch and extract the main article text from a URL.
    Returns cleaned plain text (up to _MAX_ARTICLE_CHARS), or None on failure.
    Skips known paywall domains silently.
    """
    from urllib.parse import urlparse
    domain = urlparse(url).netloc.lstrip("www.")
    if any(skip in domain for skip in _SKIP_FETCH_DOMAINS):
        return None

    try:
        resp = requests.get(url, headers=_ARTICLE_HEADERS, timeout=_ARTICLE_TIMEOUT)
        resp.raise_for_status()
    except Exception as exc:
        logger.debug("article fetch failed for %s: %s", url, exc)
        return None

    try:
        soup = BeautifulSoup(resp.text, "lxml")
    except Exception:
        soup = BeautifulSoup(resp.text, "html.parser")

    # Remove nav, footer, script, style, ads
    for tag in soup(["nav", "footer", "script", "style", "aside", "header",
                      "form", "button", "noscript"]):
        tag.decompose()

    # Prefer <article> or <main> containers; fall back to <body>
    container = soup.find("article") or soup.find("main") or soup.body
    if not container:
        return None

    paragraphs = [
        t.get_text(" ", strip=True)
        for t in container.find_all(_BODY_TAGS)
        if len(t.get_text(strip=True)) > 40
    ]
    text = " ".join(paragraphs)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:_MAX_ARTICLE_CHARS] if text else None


def _snippet(entry) -> str:
    """
    Return the best available text for this RSS entry.
    Priority:
      1. Full article fetch (when summary is short or absent)
      2. feedparser content field (Atom full-text feeds)
      3. RSS summary/description
    """
    title   = _clean(getattr(entry, "title",   ""))
    summary = _clean(getattr(entry, "summary", ""))

    # Try feedparser's content field (Atom <content> or <content:encoded>)
    content_field = ""
    for c in getattr(entry, "content", []):
        val = _clean(c.get("value", ""))
        if len(val) > len(content_field):
            content_field = val

    best_body = content_field if len(content_field) > len(summary) else summary

    # If what we have is thin, try fetching the full article
    if len(best_body) < _MIN_SUMMARY_LEN:
        url = getattr(entry, "link", None)
        if url:
            fetched = _fetch_article_text(url)
            if fetched and len(fetched) > len(best_body):
                best_body = fetched

    body = best_body.strip()
    return f"{title}\n{body}" if body else title


def fetch_matching_reports(
    feed_urls: list[str],
    keywords: list[str],
    since: datetime.datetime,
    until: datetime.datetime,
    limit: int = 3,
) -> list[str]:
    """
    Parse each feed, keep entries dated [since, until] that contain all
    keywords. Returns up to `limit` title + body snippets.
    Never raises — unreachable/malformed feeds are logged and skipped.
    """
    results: list[tuple[datetime.datetime, str]] = []

    feedparser.api.PARSE_MICROFORMATS = False

    for url in feed_urls:
        try:
            feed = feedparser.parse(url, request_headers={"User-Agent": "SIWS/1.0"})
        except Exception as exc:
            logger.warning("RSS fetch failed for %s: %s", url, exc)
            continue

        if feed.get("bozo") and not feed.entries:
            logger.warning("RSS feed malformed / unreachable: %s", url)
            continue

        for entry in feed.entries:
            dt = _entry_dt(entry)
            if dt is None:
                continue
            if not (since <= dt <= until):
                continue
            if not _matches(entry, keywords):
                continue
            results.append((dt, _snippet(entry)))

    results.sort(key=lambda x: x[0], reverse=True)
    return [text for _, text in results[:limit]]
