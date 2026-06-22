from django.test import SimpleTestCase
from airatings.verdict import map_to_verdict


class VerdictTests(SimpleTestCase):
    """Unit tests for the deterministic signal → verdict mapping."""

    def _verdict(self, **kwargs) -> str:
        return map_to_verdict(kwargs)["verdict"]

    def _stars(self, **kwargs) -> int:
        return map_to_verdict(kwargs)["stars"]

    # -----------------------------------------------------------------------
    # Case 1: Clear thriller — everything maxed out
    # -----------------------------------------------------------------------
    def test_clear_thriller_is_hot_watch(self):
        result = map_to_verdict({
            "excitement":              5,
            "drama":                   5,
            "late_tension":            5,
            "competitiveness":         5,
            "controversy":             1,
            "lead_changes":            4,
            "had_late_decisive_moment": True,
        })
        self.assertEqual(result["verdict"], "hot_watch")
        self.assertEqual(result["stars"],   5)

    # -----------------------------------------------------------------------
    # Case 2: Clear dud — nothing happened
    # -----------------------------------------------------------------------
    def test_clear_dud_is_not_watch(self):
        result = map_to_verdict({
            "excitement":              1,
            "drama":                   1,
            "late_tension":            1,
            "competitiveness":         1,
            "controversy":             0,
            "lead_changes":            0,
            "had_late_decisive_moment": False,
        })
        self.assertEqual(result["verdict"], "not_watch")
        self.assertLessEqual(result["stars"], 2)

    # -----------------------------------------------------------------------
    # Case 3: Mid-quality event — average across the board, no bonuses
    # -----------------------------------------------------------------------
    def test_mid_event_is_mid_temp(self):
        result = map_to_verdict({
            "excitement":              3,
            "drama":                   3,
            "late_tension":            3,
            "competitiveness":         3,
            "controversy":             0,
            "lead_changes":            1,
            "had_late_decisive_moment": False,
        })
        self.assertEqual(result["verdict"], "mid_temp")
        self.assertEqual(result["stars"],   3)

    # -----------------------------------------------------------------------
    # Case 4: Controversial low-scorer — boring match rescued by controversy
    # and a late decisive incident (e.g. VAR red card / penalty-miss drama)
    # -----------------------------------------------------------------------
    def test_controversial_low_scorer_is_mid_temp(self):
        result = map_to_verdict({
            "excitement":              2,
            "drama":                   2,
            "late_tension":            1,
            "competitiveness":         1,
            "controversy":             3,
            "lead_changes":            0,
            "had_late_decisive_moment": True,
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
