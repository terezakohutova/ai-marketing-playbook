"""Tests for the checker, the scorer, the committed runs, the apply step and the run-log check.

    python -m unittest discover -s tests -v
"""

import csv
import json
import shutil
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import apply_changes  # noqa: E402
import run_log_check  # noqa: E402
from check_links import broken_links  # noqa: E402
from reference_check import (  # noqa: E402
    CRM_RULES,
    INVENTORY_RULES,
    InputError,
    bounced_address,
    check_crm,
    check_inventory,
    near_same_name,
)
from score_run import ScoreError, parse_findings, score  # noqa: E402

KEYS = ROOT / "tests" / "answer_keys"
RUNS = ROOT / "examples" / "runs"


def load_key(name):
    return json.loads((KEYS / f"{name}.json").read_text(encoding="utf-8"))


def all_keys():
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(KEYS.glob("*.json"))]


def run_checker(key, folder=None):
    folder = folder or ROOT / key["folder"]
    if key["pattern"] == "inventory":
        return check_inventory(folder, key.get("source_of_truth"))
    return check_crm(folder, date.fromisoformat(key["today"]))


def block(findings):
    return "Some prose.\n\n```findings\n" + json.dumps(findings) + "\n```\n"


# ------------------------------------------------------------ answer keys


class AnswerKeysAgreeWithChecker(unittest.TestCase):
    """The hand-written keys and the mechanical checker are two separate opinions; they must agree."""

    def test_every_key_matches_the_checker(self):
        for key in all_keys():
            with self.subTest(dataset=key["dataset"]):
                got = {(f.rule, f.entity, f.bucket) for f in run_checker(key)}
                want = {(f["rule"], f["entity"], f["bucket"]) for f in key["findings"]}
                self.assertEqual(got, want)

    def test_negatives_are_not_flagged(self):
        for key in all_keys():
            flagged = {f.key for f in run_checker(key)}
            for neg in key["negatives"]:
                with self.subTest(dataset=key["dataset"], negative=neg["entity"]):
                    self.assertNotIn((neg["rule"], neg["entity"]), flagged)

    def test_every_rule_has_a_positive_and_a_negative_case(self):
        for pattern, rules in (("crm", CRM_RULES), ("inventory", INVENTORY_RULES)):
            keys = [k for k in all_keys() if k["pattern"] == pattern]
            pos = {f["rule"] for k in keys for f in k["findings"]}
            neg = {f["rule"] for k in keys for f in k["negatives"]}
            self.assertEqual(set(rules) - pos, set(), f"{pattern} rules without a positive case")
            self.assertEqual(set(rules) - neg, set(), f"{pattern} rules without a negative case")

    def test_answer_keys_live_outside_the_input_folders(self):
        for key in all_keys():
            inputs = ROOT / key["folder"]
            self.assertEqual(sorted(p.suffix for p in inputs.iterdir() if p.suffix not in (".csv", ".md")), [])
            self.assertFalse(list(inputs.glob("*output*")), f"{inputs} holds an output file")


# --------------------------------------------------------------- checker


class CheckerRobustness(unittest.TestCase):
    def copy(self, name):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp)
        shutil.copytree(ROOT / load_key(name)["folder"], tmp / "d")
        return tmp / "d"

    def edit(self, path, old, new):
        path.write_text(path.read_text(encoding="utf-8").replace(old, new, 1), encoding="utf-8")

    def test_near_same_names(self):
        self.assertTrue(near_same_name("Nordlicht Coffee", "Nordlicht Coffee Roasters"))
        self.assertTrue(near_same_name("Brightwater GmbH", "Brightwater"))
        self.assertTrue(near_same_name("Pebble Pet Co.", "Pebble Pets"))
        self.assertFalse(near_same_name("Alder Bike Works", "Alder Coffee"))
        self.assertFalse(near_same_name("Fennel & Fig", "Juniper Yarns"))

    def test_bounce_phrases(self):
        self.assertEqual(bounced_address("Delivery failure: a@x.example (mailbox does not exist)"), "a@x.example")
        self.assertEqual(bounced_address("Undeliverable: 550 5.1.1 <B@x.example>: User unknown"), "b@x.example")
        self.assertEqual(bounced_address("Mail delivery failed: returning message (c@x.example)"), "c@x.example")
        self.assertIsNone(bounced_address("Courier delivery failed twice; re-send the samples"))
        self.assertIsNone(bounced_address("d@x.example confirmed the delivery date"))

    def test_free_mail_domain_is_not_a_duplicate(self):
        flagged = {f.key for f in check_crm(ROOT / "examples/crm/crm-2", date(2026, 11, 20))}
        self.assertNotIn(("B1", "P08+P09"), flagged)

    def test_inventory_finding_in_one_bucket_does_not_hide_another(self):
        flagged = {f.key for f in check_inventory(ROOT / "examples/inventory/inv-2")}
        self.assertIn(("I1", "PRT-101"), flagged)
        self.assertIn(("I2", "PRT-101"), flagged)

    def test_source_of_truth_is_detected_not_hard_coded(self):
        flagged = {f.key for f in check_inventory(ROOT / "examples/inventory/inv-3")}
        self.assertIn(("I3", "BK-205"), flagged)

    def test_ambiguous_source_of_truth_is_an_error(self):
        d = self.copy("inv-1")
        shutil.copy(d / "storefront.csv", d / "inventory.csv")
        with self.assertRaisesRegex(InputError, "source of truth"):
            check_inventory(d)

    def test_bad_int_is_a_clear_error(self):
        d = self.copy("crm-1")
        self.edit(d / "partners.csv", "2026-10-08,2\n", "2026-10-08,two\n")
        with self.assertRaisesRegex(InputError, "live_offers.*not a whole number"):
            check_crm(d)

    def test_malformed_date_is_a_clear_error(self):
        d = self.copy("crm-1")
        self.edit(d / "partners.csv", "2026-10-02", "02/10/2026")
        with self.assertRaisesRegex(InputError, "next_step_date.*YYYY-MM-DD"):
            check_crm(d)

    def test_empty_log_is_a_clear_error(self):
        d = self.copy("crm-1")
        (d / "activity.csv").write_text("date,partner_id,source,summary\n", encoding="utf-8")
        with self.assertRaisesRegex(InputError, "empty"):
            check_crm(d)

    def test_missing_column_is_a_clear_error(self):
        d = self.copy("crm-1")
        self.edit(d / "contacts.csv", "contact_id,", "id,")
        with self.assertRaisesRegex(InputError, "missing column"):
            check_crm(d)

    def test_duplicate_contact_row_is_found(self):
        d = self.copy("crm-1")
        with (d / "contacts.csv").open("a", encoding="utf-8") as f:
            f.write("C05,P04,Anna Reiter,anna@kestrel-outdoor.example,E-commerce,Active\n")
        self.assertIn(("B3", "C05"), {f.key for f in check_crm(d)})


# ---------------------------------------------------------------- scorer


class Scorer(unittest.TestCase):
    def setUp(self):
        self.key = load_key("crm-1")
        self.perfect = [{k: f[k] for k in ("rule", "entity", "bucket")} for f in self.key["findings"]]

    def test_perfect_output(self):
        s = score(self.key, parse_findings(block(self.perfect)))
        self.assertEqual((s.precision, s.recall), (1.0, 1.0))

    def test_old_style_junk_table_row_scores_nothing(self):
        # The row that scored 14/14 under the previous scorer.
        with self.assertRaises(ScoreError):
            parse_findings("| F1 | A/B/C/D/E/F | all P01…P10 | x |\n")

    def test_catch_all_entities_are_wrong_flags(self):
        junk = [{"rule": r, "entity": e, "bucket": "person"}
                for r in ("D4", "B1", "E1", "A1")
                for e in ("all", "P01-P10", "P01, P02", "*", "P01+P01", "")]
        s = score(self.key, parse_findings(block(junk)))
        self.assertEqual(len(s.tp), 0)
        self.assertEqual(s.precision, 0.0)
        self.assertEqual(s.recall, 0.0)

    def test_flagging_everything_has_low_precision(self):
        partners = [f"P{i:02d}" for i in range(1, 11)]
        contacts = [f"C{i:02d}" for i in range(1, 12)]
        spray = []
        for rule, bucket in CRM_RULES.items():
            ents = {"A1": ["nightly-sync", "morning-digest"], "B2": contacts, "E1": contacts,
                    "B1": [f"{a}+{b}" for a in partners for b in partners if a < b],
                    "B3": partners + contacts}.get(rule, partners)
            spray += [{"rule": rule, "entity": e, "bucket": bucket} for e in ents]
        s = score(self.key, parse_findings(block(spray)))
        self.assertEqual(s.recall, 1.0)
        self.assertLess(s.precision, 0.1)  # 13 right out of ~220 flags

    def test_wrong_bucket_is_a_wrong_flag_and_a_miss(self):
        out = [dict(f, bucket="person") if f["rule"] == "C3" else f for f in self.perfect]
        s = score(self.key, parse_findings(block(out)))
        self.assertIn(("C3", "P04"), s.fn)
        self.assertEqual([x[:2] for x in s.fp], [("C3", "P04")])

    def test_ids_match_exactly(self):
        out = [dict(f, entity="P020") if f["entity"] == "P02" else f for f in self.perfect]
        s = score(self.key, parse_findings(block(out)))
        self.assertIn(("D1", "P02"), s.fn)
        self.assertIn(("D1", "P020", "not in the answer key"), s.fp)

    def test_repeats_count_once_and_pair_order_does_not_matter(self):
        out = self.perfect + [{"rule": "B1", "entity": "P07+P01", "bucket": "person"}]
        s = score(self.key, parse_findings(block(out)))
        self.assertEqual((s.precision, s.recall), (1.0, 1.0))

    def test_unknown_rule_is_a_wrong_flag(self):
        s = score(self.key, parse_findings(block(self.perfect + [{"rule": "Z9", "entity": "P01", "bucket": "person"}])))
        self.assertEqual(len(s.fp), 1)

    def test_block_problems_are_errors(self):
        with self.assertRaises(ScoreError):
            parse_findings(block(self.perfect) + block(self.perfect))
        with self.assertRaises(ScoreError):
            parse_findings("```findings\n[{\"rule\": \"D4\",]\n```\n")
        with self.assertRaises(ScoreError):
            parse_findings("```findings\n{\"rule\": \"D4\"}\n```\n")


# ------------------------------------------------------- committed runs

# Scores of the committed blind runs, pinned so that README numbers stay true.
EXPECTED_RUN_SCORES = {
    # dataset: (true positives, wrong flags, misses)
    "inv-1": (7, 0, 0),
    "inv-2": (6, 0, 0),
    "inv-3": (5, 0, 0),
    "crm-1": (13, 0, 0),
    "crm-2": (11, 0, 0),
    "crm-3": (11, 0, 0),
}


class CommittedRuns(unittest.TestCase):
    def test_every_dataset_has_a_run(self):
        self.assertEqual({p.parent.name for p in RUNS.glob("*/output.md")}, {k["dataset"] for k in all_keys()})

    def test_scores_are_pinned(self):
        for name, (tp, fp, fn) in EXPECTED_RUN_SCORES.items():
            with self.subTest(dataset=name):
                s = score(load_key(name), parse_findings((RUNS / name / "output.md").read_text(encoding="utf-8")))
                self.assertEqual((len(s.tp), len(s.fp), len(s.fn)), (tp, fp, fn))

    def test_run_metadata(self):
        for name in EXPECTED_RUN_SCORES:
            with self.subTest(dataset=name):
                meta = json.loads((RUNS / name / "run.json").read_text(encoding="utf-8"))
                for field in ("date", "model", "prompt", "files_given", "output_sha256"):
                    self.assertIn(field, meta)
                given = [f["path"] for f in meta["files_given"]]
                self.assertFalse([g for g in given if "output" in g or "answer" in g or g.endswith(".json")])


# --------------------------------------------------------------- apply


class ApplyChanges(unittest.TestCase):
    def setUp(self):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp)
        self.d = tmp / "crm"
        shutil.copytree(ROOT / "examples/crm/crm-1", self.d)
        self.log = tmp / "change-log.csv"
        self.spec = json.loads((ROOT / "examples/apply/crm-1-confirmed.json").read_text(encoding="utf-8"))

    def rows(self, name):
        with (self.d / name).open(newline="", encoding="utf-8") as f:
            return {r[next(iter(r))]: r for r in csv.DictReader(f)}

    def test_applies_and_logs_old_value_first(self):
        apply_changes.apply(self.d, self.spec, self.log, at="2026-10-13T09:00:00+00:00")
        self.assertEqual(self.rows("partners.csv")["P04"]["last_contact"], "2026-10-05")
        self.assertEqual(self.rows("contacts.csv")["C11"]["status"], "Bounced")
        with self.log.open(newline="", encoding="utf-8") as f:
            log = list(csv.DictReader(f))
        self.assertEqual([(r["id"], r["old"], r["new"], r["approved_by"]) for r in log],
                         [("P04", "2026-09-12", "2026-10-05", "Mia"), ("C11", "Active", "Bounced", "Mia")])

    def test_refuses_stale_proposal_and_writes_nothing(self):
        self.spec["changes"][1]["old"] = "To verify"
        before = (self.d / "partners.csv").read_bytes()
        with self.assertRaisesRegex(apply_changes.ChangeError, "re-run the audit"):
            apply_changes.apply(self.d, self.spec, self.log)
        self.assertEqual((self.d / "partners.csv").read_bytes(), before)
        self.assertFalse(self.log.exists())

    def test_refuses_without_approver(self):
        self.spec["approved_by"] = ""
        with self.assertRaisesRegex(apply_changes.ChangeError, "approved_by"):
            apply_changes.apply(self.d, self.spec, self.log)

    def test_refuses_path_outside_folder_and_unknown_rows(self):
        for bad in ({"file": "../partners.csv"}, {"id": "P99"}, {"field": "partner_id"}, {"field": "nope"}):
            spec = {"approved_by": "Mia", "changes": [dict(self.spec["changes"][0], **bad)]}
            with self.subTest(bad=bad), self.assertRaises(apply_changes.ChangeError):
                apply_changes.apply(self.d, spec, self.log)

    def test_dry_run_writes_nothing(self):
        before = (self.d / "partners.csv").read_bytes()
        apply_changes.apply(self.d, self.spec, self.log, dry_run=True)
        self.assertEqual((self.d / "partners.csv").read_bytes(), before)
        self.assertFalse(self.log.exists())


# ------------------------------------------------------- run-log check


class RunLogCheck(unittest.TestCase):
    def test_healthy_log_is_clear(self):
        self.assertEqual(run_log_check.check(ROOT / "examples/scheduled/healthy"), [])

    def test_broken_log(self):
        found = {(r, e) for r, e, _ in run_log_check.check(ROOT / "examples/scheduled/broken")}
        self.assertEqual(found, {
            ("S1", "nightly-sync"),  # stopped after 10-10
            ("S1", "weekly-heartbeat"),  # 11 days since the last heartbeat
            ("S2", "nightly-sync/partners.status"),  # a human-owned field
            ("S3", "nightly-sync/partners"),  # created a partner from an e-mail
            ("S4", "nightly-sync/partners.last_contact"),  # no old value
            ("S5", "morning-digest/2026-10-12"),  # digest with nothing in it
        })

    def test_empty_log_is_an_error(self):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp)
        shutil.copy(ROOT / "examples/scheduled/healthy/schedule.json", tmp)
        (tmp / "run-log.csv").write_text("date,job,action,target,field,old,new,items\n", encoding="utf-8")
        with self.assertRaisesRegex(run_log_check.InputError, "empty"):
            run_log_check.check(tmp)


class Links(unittest.TestCase):
    def test_relative_links_and_anchors_resolve(self):
        self.assertEqual(broken_links(), [])


if __name__ == "__main__":
    unittest.main()
