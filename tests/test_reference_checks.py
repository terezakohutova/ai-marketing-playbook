"""Pins the rule-derived findings for both sample datasets, checks that the
committed agent outputs contain every one of them, and that all links resolve.

    python -m unittest discover -s tests -v
"""

import sys
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from check_links import broken_links  # noqa: E402
from reference_check import (  # noqa: E402
    CONFIRMED,
    HUMAN,
    check_crm,
    check_inventory,
    crm_missing_from,
    inventory_missing_from,
)

INVENTORY = ROOT / "examples" / "sample-run"
CRM = ROOT / "examples" / "crm-audit"


class InventorySample(unittest.TestCase):
    def setUp(self):
        self.findings = check_inventory(INVENTORY)

    def test_buckets(self):
        self.assertEqual(
            {k: v["bucket"] for k, v in self.findings.items()},
            {
                "ITM-014": CONFIRMED,  # sold in storefront, live on both marketplaces
                "ITM-040": CONFIRMED,  # sold, still live on marketplace-b
                "ITM-058": CONFIRMED,  # "Sold" vs "LIVE " (case and whitespace)
                "ITM-022": HUMAN,  # sold on one marketplace only
                "ITM-043": HUMAN,  # "reserved" is not a storefront status
                "ITM-055": HUMAN,  # two channels agree on sold, the source of truth doesn't
                "ITM-052": HUMAN,  # listed on a marketplace, unknown to the storefront
            },
        )

    def test_clean_items_are_not_flagged(self):
        for item in ("ITM-031", "ITM-035", "ITM-061", "ITM-063"):
            self.assertNotIn(item, self.findings)

    def test_agent_output_covers_every_finding(self):
        output = (INVENTORY / "proposal-queue-output.md").read_text(encoding="utf-8")
        self.assertEqual(inventory_missing_from(output, self.findings), [])


    def test_checker_catches_a_wrong_bucket(self):
        output = (INVENTORY / "proposal-queue-output.md").read_text(encoding="utf-8")
        swapped = output.replace("| ITM-055 Rattan armchair", "| ITM-999 moved").replace(
            "| ITM-040 Walnut side table", "| ITM-055 Rattan armchair"
        )
        self.assertIn("ITM-055", inventory_missing_from(swapped, self.findings))


class CrmSample(unittest.TestCase):
    def setUp(self):
        self.findings = check_crm(CRM, date(2026, 10, 13))

    def test_findings(self):
        self.assertEqual(
            {(pid, section) for pid, section, _ in self.findings},
            {
                ("ALL", "A"),
                ("P01", "B"), ("P07", "B"),
                ("P04", "C"),
                ("P02", "D"), ("P03", "D"), ("P06", "D"),
                ("P06", "E"), ("P07", "E"), ("P09", "E"),
                ("P07", "F"), ("P08", "F"),
            },
        )

    def test_clean_partners(self):
        flagged = {pid for pid, _, _ in self.findings}
        self.assertEqual({f"P{i:02d}" for i in range(1, 11)} - flagged, {"P05", "P10"})

    def test_first_run_covers_every_finding(self):
        output = (CRM / "audit-output.md").read_text(encoding="utf-8")
        self.assertEqual(crm_missing_from(output, self.findings), [])

    def test_second_run_misses_exactly_the_documented_one(self):
        # audit-output-rerun.md says it missed P06's former-only contact; keep that claim true.
        output = (CRM / "audit-output-rerun.md").read_text(encoding="utf-8")
        self.assertEqual(crm_missing_from(output, self.findings), [("P06", "E", "no verified current contact")])

    def test_checker_catches_a_missing_row(self):
        output = (CRM / "audit-output.md").read_text(encoding="utf-8")
        trimmed = "\n".join(line for line in output.splitlines() if not line.startswith("| F6 "))
        self.assertIn(("P09", "E", "bounced contact C11 still active"), crm_missing_from(trimmed, self.findings))


class Links(unittest.TestCase):
    def test_relative_links_resolve(self):
        self.assertEqual(broken_links(), [])


if __name__ == "__main__":
    unittest.main()
