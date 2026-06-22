import re
import calendar
import logging
import datetime
import feedparser

logger = logging.getLogger(__name__)

_TIMEOUT = 10  # feedparser socket timeout (set via agent attribute)


def _entry_dt(entry) -> datetime.datetime | None:
    """Return a UTC-aware datetime from a feedparser entry, or None."""
    t = getattr(entry, "published_parsed", None) or getattr(entry, "updated_parsed", None)
    if t is None:
        return None
    # published_parsed is a time.struct_time interpreted as UTC
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


def _snippet(entry) -> str:
    title   = _clean(getattr(entry, "title",   ""))
    summary = _clean(getattr(entry, "summary", ""))
    return f"{title}\n{summary}" if summary else title


def fetch_matching_reports(
    feed_urls: list[str],
    keywords: list[str],
    since: datetime.datetime,
    until: datetime.datetime,
    limit: int = 3,
) -> list[str]:
    """
    Parse each feed, keep entries dated [since, until] that contain all
    keywords. Returns up to `limit` TITLE + SUMMARY snippets.
    Never raises — unreachable/malformed feeds are logged and skipped.
    """
    results: list[tuple[datetime.datetime, str]] = []

    feedparser.api.PARSE_MICROFORMATS = False  # speed up, we don't need them

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

    # Most-recent first, then cap
    results.sort(key=lambda x: x[0], reverse=True)
    return [text for _, text in results[:limit]]
