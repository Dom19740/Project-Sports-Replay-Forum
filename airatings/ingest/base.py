import logging

logger = logging.getLogger(__name__)


class EventDataSource:
    """
    Adapter base class. One concrete subclass per external stats API.
    get_stats()   — objective structured data used as LLM context.
    get_reports() — Phase 2: free-text sources (press summaries, commentary).
    """

    def get_stats(self, event) -> dict:
        raise NotImplementedError

    def get_reports(self, event) -> list:
        return []
