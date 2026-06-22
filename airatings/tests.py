from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from airatings.guard import check_blurb
from airatings.pipeline import _apply_stat_corrections, _apply_verdict_corrections
from airatings.verdict import map_to_verdict


class VerdictTests(SimpleTestCase):
    """Unit tests for the deterministic signal → verdict mapping."""

    # -----------------------------------------------------------------------
    # Case 1: Clear thriller
    # base = 5×0.30 + 5×0.25 + 5×0.25 + 4×0.20 = 4.80
    # bonus = LDM(+0.35) + con1(+0.35) + lc3(+0.30) = +1.00
    # raw = 5.80 → clamped 5.00 → 5★ → hot_watch
    # -----------------------------------------------------------------------
    def test_clear_thriller_is_hot_watch(self):
        result = map_to_verdict({
            "excitement":               5,
            "drama":                    5,
            "competitiveness":          4,
            "late_tension":             5,
            "controversy":              1,
            "lead_changes":             3,
            "had_late_decisive_moment": True,
        })
        self.assertEqual(result["verdict"], "hot_watch")
        self.assertEqual(result["stars"],   5)

    # -----------------------------------------------------------------------
    # Case 2: Clear dud
    # base = 1×0.30 + 1×0.25 + 1×0.25 + 2×0.20 = 1.20
    # bonus = 0
    # score = 1.20 → 1★ → not_watch
    # -----------------------------------------------------------------------
    def test_clear_dud_is_not_watch(self):
        result = map_to_verdict({
            "excitement":               1,
            "drama":                    1,
            "competitiveness":          2,
            "late_tension":             1,
            "controversy":              0,
            "lead_changes":             0,
            "had_late_decisive_moment": False,
        })
        self.assertEqual(result["verdict"], "not_watch")
        self.assertEqual(result["stars"], 1)

    # -----------------------------------------------------------------------
    # Case 3: Mid match
    # base = 3×0.30 + 2×0.25 + 2×0.25 + 3×0.20 = 2.50
    # bonus = lc1(+0.10) = +0.10
    # score = 2.60 → 3★ (≥2.2) → mid_temp   [0.40 above the threshold]
    # -----------------------------------------------------------------------
    def test_mid_event_is_mid_temp(self):
        result = map_to_verdict({
            "excitement":               3,
            "drama":                    2,
            "competitiveness":          3,
            "late_tension":             2,
            "controversy":              0,
            "lead_changes":             1,
            "had_late_decisive_moment": False,
        })
        self.assertEqual(result["verdict"], "mid_temp")
        self.assertEqual(result["stars"],   3)

    # -----------------------------------------------------------------------
    # Case 4: Controversial low-scorer — boring match rescued by controversy
    # and a late decisive incident (e.g. VAR red card / penalty drama)
    # base = 2×0.30 + 2×0.25 + 1×0.25 + 1×0.20 = 1.55
    # bonus = LDM(+0.35) + con3(+1.05) = +1.40
    # score = 2.95 → 3★ → mid_temp
    # -----------------------------------------------------------------------
    def test_controversial_low_scorer_is_mid_temp(self):
        result = map_to_verdict({
            "excitement":               2,
            "drama":                    2,
            "late_tension":             1,
            "competitiveness":          1,
            "controversy":              3,
            "lead_changes":             0,
            "had_late_decisive_moment": True,
        })
        self.assertEqual(result["verdict"], "mid_temp")
        self.assertEqual(result["stars"],   3)

    # -----------------------------------------------------------------------
    # Case 5: NZ vs Egypt profile — comeback win, settled early
    # base = 4×0.30 + 3×0.25 + 2×0.25 + 3×0.20 = 3.05
    # bonus = 0  (no LDM, no controversy, no lead changes in scoring fields)
    # score = 3.05 → 3★ → mid_temp
    # Note: comeback is a stats field, not a signal field — doesn't affect score
    # -----------------------------------------------------------------------
    def test_nz_vs_egypt_profile_is_mid_temp(self):
        result = map_to_verdict({
            "excitement":               4,
            "drama":                    3,
            "competitiveness":          3,
            "late_tension":             2,
            "controversy":              0,
            "lead_changes":             0,
            "had_late_decisive_moment": False,
        })
        self.assertEqual(result["verdict"], "mid_temp")
        self.assertEqual(result["stars"],   3)

    # -----------------------------------------------------------------------
    # Sanity: rationale_internal is always a non-empty string
    # -----------------------------------------------------------------------
    def test_rationale_internal_present(self):
        result = map_to_verdict({
            "excitement": 3, "drama": 3, "late_tension": 3,
            "competitiveness": 3, "controversy": 0,
            "lead_changes": 0, "had_late_decisive_moment": False,
        })
        self.assertIsInstance(result["rationale_internal"], str)
        self.assertGreater(len(result["rationale_internal"]), 10)


# ---------------------------------------------------------------------------
# Guard tests
# ---------------------------------------------------------------------------

class GuardTests(SimpleTestCase):
    """Unit tests for check_blurb() in airatings/guard.py."""

    def _mock_event(
        self,
        event_type: str = "Spain vs Cape Verde",
        league: str = "FIFA World Cup",
        comp_name: str = "FIFA World Cup",
    ) -> MagicMock:
        event = MagicMock()
        event.pk = 271
        event.idEvent = "2391739"
        event.event_type = event_type
        event.event_list.name = comp_name
        event.event_list.league = league
        event.date_time.year = 2026
        return event

    # --- Pattern tests (name extraction bypassed) ---

    @patch("airatings.guard._build_banned_names", return_value=set())
    def test_clean_blurb_passes(self, _):
        is_safe, reasons = check_blurb(
            "An intense and gripping contest that kept viewers on edge throughout.",
            self._mock_event(),
        )
        self.assertTrue(is_safe)
        self.assertEqual(reasons, [])

    @patch("airatings.guard._build_banned_names", return_value=set())
    def test_result_verb_caught(self, _):
        is_safe, reasons = check_blurb(
            "One side won convincingly in an enthralling affair.",
            self._mock_event(),
        )
        self.assertFalse(is_safe)
        self.assertTrue(any("won" in r for r in reasons))

    @patch("airatings.guard._build_banned_names", return_value=set())
    def test_digit_scoreline_caught(self, _):
        is_safe, reasons = check_blurb(
            "The final margin was a comfortable 3-1.",
            self._mock_event(),
        )
        self.assertFalse(is_safe)
        self.assertTrue(any("digit scoreline" in r for r in reasons))

    @patch("airatings.guard._build_banned_names", return_value=set())
    def test_written_score_caught(self, _):
        is_safe, reasons = check_blurb(
            "Two goals in quick succession changed the complexion entirely.",
            self._mock_event(),
        )
        self.assertFalse(is_safe)
        self.assertTrue(any("written score" in r for r in reasons))

    @patch("airatings.guard._build_banned_names", return_value=set())
    def test_banned_phrase_caught(self, _):
        is_safe, reasons = check_blurb(
            "One side took the lead early and never looked back.",
            self._mock_event(),
        )
        self.assertFalse(is_safe)
        self.assertTrue(any("banned phrase" in r for r in reasons))

    # --- Name detection ---

    def test_team_name_caught(self):
        banned = {"spain", "cape verde", "cape", "verde"}
        with patch("airatings.guard._build_banned_names", return_value=banned):
            is_safe, reasons = check_blurb(
                "Spain looked dominant in an absorbing contest.",
                self._mock_event(),
            )
        self.assertFalse(is_safe)
        self.assertTrue(any("spain" in r for r in reasons))

    def test_player_name_caught(self):
        banned = {"williams", "spain", "cape", "verde", "cape verde"}
        with patch("airatings.guard._build_banned_names", return_value=banned):
            is_safe, reasons = check_blurb(
                "Williams was the standout performer in a tense encounter.",
                self._mock_event(),
            )
        self.assertFalse(is_safe)
        self.assertTrue(any("williams" in r for r in reasons))

    # --- Deliberately leaky blurb (all categories at once) ---

    def test_maximally_leaky_blurb_caught(self):
        """A blurb stuffed with every leak type must raise multiple reasons."""
        banned = {"spain", "verde", "cape", "cape verde"}
        leaky = (
            "Spain beat Cape Verde 3-1 — two goals sealed it. "
            "Spain won after they took the lead with a comeback."
        )
        with patch("airatings.guard._build_banned_names", return_value=banned):
            is_safe, reasons = check_blurb(leaky, self._mock_event())

        self.assertFalse(is_safe)
        categories = {r.split(":")[0] for r in reasons}
        # Must catch: result verb, digit scoreline, written score, banned phrase, named entity
        self.assertIn("result verb",    categories)
        self.assertIn("digit scoreline", categories)
        self.assertIn("written score",  categories)
        self.assertIn("banned phrase",  categories)
        self.assertIn("named entity",   categories)
        self.assertGreaterEqual(len(reasons), 5)


# ---------------------------------------------------------------------------
# Stat correction tests
# ---------------------------------------------------------------------------

class StatCorrectionTests(SimpleTestCase):
    """Unit tests for _apply_stat_corrections() in airatings/pipeline.py."""

    def _signals(self, excitement: int = 1) -> dict:
        return {
            "excitement": excitement, "drama": 3, "competitiveness": 2,
            "late_tension": 2, "controversy": 0,
            "lead_changes": 0, "had_late_decisive_moment": False,
        }

    def test_7_goals_floors_excitement_to_5(self):
        """Germany 7-1 scenario — must never score 1★."""
        result = _apply_stat_corrections(
            self._signals(excitement=1),
            {"sport": "football", "total_goals": 7},
        )
        self.assertEqual(result["excitement"], 5)

    def test_5_goals_floors_excitement_to_4(self):
        """Sweden 5-1 scenario — must not score below 4 on excitement."""
        result = _apply_stat_corrections(
            self._signals(excitement=2),
            {"sport": "football", "total_goals": 5},
        )
        self.assertEqual(result["excitement"], 4)

    def test_4_goals_floors_excitement_to_3(self):
        """Japan 4-0 / Spain 4-0 scenario — 4 goals must not produce exc < 3."""
        result = _apply_stat_corrections(
            self._signals(excitement=1),
            {"sport": "football", "total_goals": 4},
        )
        self.assertEqual(result["excitement"], 3)

    def test_floor_does_not_lower_existing_high_score(self):
        """If LLM already gave a higher score, the floor must not reduce it."""
        result = _apply_stat_corrections(
            self._signals(excitement=5),
            {"sport": "football", "total_goals": 5},
        )
        self.assertEqual(result["excitement"], 5)

    def test_low_goals_leaves_excitement_unchanged(self):
        """A 1-1 draw should not be corrected — the LLM judgment stands."""
        result = _apply_stat_corrections(
            self._signals(excitement=3),
            {"sport": "football", "total_goals": 2},
        )
        self.assertEqual(result["excitement"], 3)

    def test_non_football_sport_is_unchanged(self):
        """F1 stats go through stage one only — no stat correction applied."""
        result = _apply_stat_corrections(
            self._signals(excitement=1),
            {"sport": "f1", "dnf_count": 5},
        )
        self.assertEqual(result["excitement"], 1)

    def test_missing_total_goals_leaves_excitement_unchanged(self):
        """If total_goals is absent (incomplete stats), no correction is applied."""
        result = _apply_stat_corrections(
            self._signals(excitement=1),
            {"sport": "football"},
        )
        self.assertEqual(result["excitement"], 1)


# ---------------------------------------------------------------------------
# Verdict correction tests
# ---------------------------------------------------------------------------

class VerdictCorrectionTests(SimpleTestCase):
    """Unit tests for _apply_verdict_corrections() in airatings/pipeline.py."""

    def _verdict(self, stars: int) -> dict:
        verdicts = {5: "hot_watch", 4: "hot_watch", 3: "mid_temp", 2: "mid_temp", 1: "not_watch"}
        return {
            "stars": stars,
            "verdict": verdicts[stars],
            "rationale_internal": f"base=test → {stars}★",
        }

    def test_7_goals_raises_3star_to_4star_hot_watch(self):
        """Germany 7-1 scenario: 3★ mid_temp → 4★ hot_watch."""
        result = _apply_verdict_corrections(
            self._verdict(3),
            {"sport": "football", "total_goals": 7},
        )
        self.assertEqual(result["stars"], 4)
        self.assertEqual(result["verdict"], "hot_watch")
        self.assertIn("verdict_correction", result["rationale_internal"])

    def test_7_goals_raises_2star_to_4star_hot_watch(self):
        """High goal count overrides a very low formula score."""
        result = _apply_verdict_corrections(
            self._verdict(2),
            {"sport": "football", "total_goals": 8},
        )
        self.assertEqual(result["stars"], 4)
        self.assertEqual(result["verdict"], "hot_watch")

    def test_5_goals_raises_2star_to_3star_mid_temp(self):
        """Sweden 5-1 scenario: 2★ mid_temp → 3★ mid_temp (no longer skippable)."""
        result = _apply_verdict_corrections(
            self._verdict(2),
            {"sport": "football", "total_goals": 5},
        )
        self.assertEqual(result["stars"], 3)
        self.assertEqual(result["verdict"], "mid_temp")

    def test_4_goals_raises_1star_to_2star_mid_temp(self):
        """Japan 4-0 / Spain 4-0 scenario: 1★ not_watch → 2★ mid_temp."""
        result = _apply_verdict_corrections(
            self._verdict(1),
            {"sport": "football", "total_goals": 4},
        )
        self.assertEqual(result["stars"], 2)
        self.assertEqual(result["verdict"], "mid_temp")
        self.assertIn("verdict_correction", result["rationale_internal"])

    def test_floor_does_not_lower_existing_high_star(self):
        """A 5★ result on a 7-goal game must not be reduced."""
        result = _apply_verdict_corrections(
            self._verdict(5),
            {"sport": "football", "total_goals": 7},
        )
        self.assertEqual(result["stars"], 5)
        self.assertEqual(result["verdict"], "hot_watch")

    def test_low_goals_leaves_verdict_unchanged(self):
        """A 2-goal game below all thresholds is not touched."""
        result = _apply_verdict_corrections(
            self._verdict(2),
            {"sport": "football", "total_goals": 2},
        )
        self.assertEqual(result["stars"], 2)
        self.assertEqual(result["verdict"], "mid_temp")

    def test_non_football_sport_is_unchanged(self):
        """F1 verdicts are never corrected by goal count."""
        result = _apply_verdict_corrections(
            self._verdict(1),
            {"sport": "f1", "total_goals": 10},
        )
        self.assertEqual(result["stars"], 1)

    def test_missing_total_goals_leaves_verdict_unchanged(self):
        """Absent total_goals applies no correction."""
        result = _apply_verdict_corrections(
            self._verdict(2),
            {"sport": "football"},
        )
        self.assertEqual(result["stars"], 2)
