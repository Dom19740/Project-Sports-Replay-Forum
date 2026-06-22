from .f1 import F1DataSource
from .football import FootballDataSource

# Map Competition.league → adapter class.
# Adding a new sport = one new adapter file + one entry here.
_SOURCES = {
    "Formula 1": F1DataSource,
    "FIFA World Cup": FootballDataSource,
    "English Premier League": FootballDataSource,
    "UEFA Champions League": FootballDataSource,
    "UEFA Europa League": FootballDataSource,
    "Scottish Premier League": FootballDataSource,
    "MotoGP": None,   # placeholder — Phase 3
    "NFL": None,
    "NBA": None,
    "NHL": None,
}


def get_source_for_event(event):
    """Return an instantiated EventDataSource for the given event, or None."""
    cls = _SOURCES.get(event.event_list.league)
    if cls is None:
        return None
    return cls()
