from django.test import SimpleTestCase
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
