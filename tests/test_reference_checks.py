"""Tests for the checker, the scorer, the committed runs, the apply step, the run-log and outreach checks.

    python -m unittest discover -s tests -v
"""

import csv
import hashlib
import json
import os
import shutil
import sys
import tempfile
import unittest
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import apply_changes  # noqa: E402
import outreach_check  # noqa: E402
import run_log_check  # noqa: E402
from check_links import broken_links  # noqa: E402
from key_vs_checker import compare  # noqa: E402
from reference_check import (  # noqa: E402
    CRM_RULES,
    INVENTORY_RULES,
    InputError,
    bounced_address,
    check_crm,
    check_inventory,
    name_match,
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

# The keys are written by hand and are NOT required to match the checker. What the
# checker does with each dataset is pinned here, so any disagreement is visible
# and has to be explained in the README, not silently "fixed" in either one.
CHECKER_VS_KEY = {
    "crm-1": "agree", "crm-2": "agree", "crm-3": "agree",
    "inv-1": "agree", "inv-2": "agree", "inv-3": "agree",
    "crm-messy": "error", "inv-messy": "error",
}

# Messy exports, mechanically repaired step by step (the obvious script fixes).
MESSY_HEADERS = {
    "crm-messy": {
        "partners.csv": {"id": "partner_id", "company": "name", "stage": "status", "prio": "priority",
                         "account_owner": "owner", "country": "market", "next_action": "next_step",
                         "due": "next_step_date", "last_touch": "last_contact", "active_offers": "live_offers"},
        "contacts.csv": {"partner": "partner_id", "e-mail": "email", "state": "status"},
        "activity.csv": {"when": "date", "partner": "partner_id", "channel": "source", "note": "summary"},
    },
    "inv-messy": {
        "stock-master.csv": {"SKU": "item_id", "Qty on hand": "on_hand", "Status": "status"},
        "marketplace-a.csv": {"sku": "item_id", "qty_listed": "listed_qty", "state": "status"},
        "marketplace-b.csv": {"Item ID": "item_id", "Available": "listed_qty", "Listing status": "status"},
    },
}
DATE_COLUMNS = ("date", "next_step_date", "last_contact")


def to_iso(value):
    for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%b %d %Y"):
        try:
            return datetime.strptime(value, fmt).date().isoformat()
        except ValueError:
            pass
    return value


def repaired_copy(test, name, dates):
    key = load_key(name)
    tmp = Path(tempfile.mkdtemp())
    test.addCleanup(shutil.rmtree, tmp)
    for file, mapping in MESSY_HEADERS[name].items():
        with (ROOT / key["folder"] / file).open(newline="", encoding="utf-8") as f:
            rows = list(csv.reader(f))
        rows[0] = [mapping.get(h, h) for h in rows[0]]
        if dates:
            cols = [i for i, h in enumerate(rows[0]) if h in DATE_COLUMNS]
            for r in rows[1:]:
                for i in cols:
                    r[i] = to_iso(r[i])
        with (tmp / file).open("w", newline="", encoding="utf-8") as f:
            csv.writer(f, lineterminator="\n").writerows(rows)
    return tmp


class AnswerKeysAndChecker(unittest.TestCase):
    """Two separate opinions: hand-written keys and the mechanical checker."""

    def test_checker_vs_key_outcome_is_pinned(self):
        self.assertEqual({k["dataset"] for k in all_keys()}, set(CHECKER_VS_KEY))
        for key in all_keys():
            with self.subTest(dataset=key["dataset"]):
                r = compare(key)
                outcome = "error" if "error" in r else "agree" if not (r["checker_only"] or r["key_only"]) else "differ"
                self.assertEqual(outcome, CHECKER_VS_KEY[key["dataset"]], r)

    def test_messy_crm_defeats_the_checker_at_every_repair_step(self):
        with self.assertRaisesRegex(InputError, "missing column"):
            check_crm(ROOT / "examples/crm/crm-messy")
        with self.assertRaisesRegex(InputError, "not a YYYY-MM-DD date"):
            check_crm(repaired_copy(self, "crm-messy", dates=False))
        r = compare(load_key("crm-messy"), repaired_copy(self, "crm-messy", dates=True))
        self.assertEqual(r["key_only"], [  # free-text status, e-mail logged under another channel name
            ("C1", "P03", "person"), ("C3", "P04", "safe"), ("D5", "P02", "person")])
        self.assertEqual(r["checker_only"], [  # an e-mail channel taken for a job, contact missed
            ("A1", "E-mail (inbound)", "person"), ("D4", "P04", "person")])

    def test_messy_inventory_defeats_the_checker(self):
        with self.assertRaisesRegex(InputError, "missing column"):
            check_inventory(ROOT / "examples/inventory/inv-messy")
        r = compare(load_key("inv-messy"), repaired_copy(self, "inv-messy", dates=False))
        self.assertEqual(r["key_only"], [  # "Sold out" is not "sold", "Active" is not "live"
            ("I1", "SK-102", "confirmed"), ("I5", "SK-103", "confirmed"),
            ("I6", "SK-101", "human"), ("I6", "SK-105", "human")])
        self.assertEqual([f[:2] for f in r["checker_only"]],
                         [("I2", "SK-101"), ("I2", "SK-102"), ("I2", "SK-103"), ("I2", "SK-105")])

    def test_keys_do_not_flag_their_own_negatives(self):
        for key in all_keys():
            flagged = {(f["rule"], f["entity"]) for f in key["findings"]}
            for neg in key["negatives"]:
                with self.subTest(dataset=key["dataset"], negative=neg["entity"]):
                    self.assertNotIn((neg["rule"], neg["entity"]), flagged)

    def test_checker_does_not_flag_negatives_where_it_runs(self):
        for key in all_keys():
            if CHECKER_VS_KEY[key["dataset"]] == "error":
                continue
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

    def test_short_or_different_names_are_not_duplicates(self):
        for a, b in (("Lumo", "Limo"), ("Nova", "Nora"), ("Bolt Bikes", "Bold Bikes"), ("Bolt", "Bold Bikes"),
                     ("Lumo Lighting", "Limo Lighting")):
            with self.subTest(pair=(a, b)):
                self.assertFalse(near_same_name(a, b))
        self.assertTrue(near_same_name("Ferrow Ceramics", "Ferow Ceramics"))  # typo in a long word
        self.assertTrue(near_same_name("Kettle & Crumb", "Kettle and Crumb Ltd."))
        self.assertTrue(near_same_name("Nova", "NOVA GmbH"))  # exact after normalising
        self.assertEqual(name_match("Bolt", "Bolt Bikes"), "near")  # needs a second signal
        self.assertFalse(near_same_name("Bolt", "Bolt Bikes"))

    def crm_with(self, partners, contacts):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp)
        head = "partner_id,name,status,priority,owner,market,next_step,next_step_date,last_contact,live_offers\n"
        (tmp / "partners.csv").write_text(head + "".join(
            f"{pid},{name},Live,A,Mia,DE,Call,2026-12-01,2026-11-19,1\n" for pid, name in partners), encoding="utf-8")
        (tmp / "contacts.csv").write_text("contact_id,partner_id,email,status,phone\n" + "".join(
            f"{c},{pid},{mail},Active,{phone}\n" for c, pid, mail, phone in contacts), encoding="utf-8")
        (tmp / "activity.csv").write_text("date,partner_id,source,summary\n2026-11-20,,nightly-sync,ok\n",
                                          encoding="utf-8")
        return {f.key for f in check_crm(tmp)}

    def test_short_near_names_need_a_second_signal(self):
        partners = [("P01", "Bolt"), ("P02", "Bolt Bikes"), ("P03", "Lumo"), ("P04", "Limo")]
        no_signal = self.crm_with(partners, [("C1", "P01", "a@bolt.example", "+49 30 1111 1111"),
                                             ("C2", "P02", "b@boltbikes.example", "+49 30 2222 2222"),
                                             ("C3", "P03", "c@lumo.example", ""), ("C4", "P04", "d@limo.example", "")])
        self.assertNotIn(("B1", "P01+P02"), no_signal)
        same_phone = self.crm_with(partners, [("C1", "P01", "a@bolt.example", "+49 30 1111 1111"),
                                              ("C2", "P02", "b@boltbikes.example", "030 1111 1111"),
                                              ("C3", "P03", "c@lumo.example", ""), ("C4", "P04", "d@limo.example", "")])
        self.assertIn(("B1", "P01+P02"), same_phone)
        self.assertNotIn(("B1", "P03+P04"), same_phone)  # Lumo/Limo are not near at all

    def test_repeated_partner_id_keeps_checking_the_second_row(self):
        d = self.copy("crm-1")
        with (d / "partners.csv").open("a", encoding="utf-8") as f:
            f.write("P01,Nordlicht Coffee,Lost,A,Mia,DE,Chase,2026-10-20,2026-10-08,2\n")
        flagged = {f.key for f in check_crm(d)}
        self.assertIn(("B3", "P01"), flagged)
        self.assertIn(("C1", "P01"), flagged)  # only the second row is Lost with live offers
        self.assertIn(("D3", "P01"), flagged)

    def test_scheduled_jobs_come_from_the_data_and_start_at_their_first_line(self):
        d = self.copy("crm-1")
        with (d / "activity.csv").open("a", encoding="utf-8") as f:
            f.write("2026-10-12,,weekly-export,Run OK\n2026-10-13,,weekly-export,Run OK\n")
            f.write("2026-10-11,,stock-mirror,Run OK\n2026-10-13,,stock-mirror,Run OK\n")
        flagged = {f.key for f in check_crm(d)}
        self.assertNotIn(("A1", "weekly-export"), flagged)  # started 10-12, daily since
        self.assertIn(("A1", "stock-mirror"), flagged)  # no line on 10-12
        only = {f.key for f in check_crm(d, jobs=["morning-digest"]) if f.rule == "A1"}
        self.assertEqual(only, set())

    def test_bounce_prefers_the_failed_recipient_line(self):
        text = ("Returned mail: see transcript. From: postmaster@mx.x.example. "
                "Original-Recipient: rfc822; jo@x.example. Final-Recipient: rfc822; jo.wren@x.example")
        self.assertEqual(bounced_address(text), "jo.wren@x.example")
        text = "Undeliverable: Original-Recipient: rfc822;<kim@x.example> (from ops@y.example)"
        self.assertEqual(bounced_address(text), "kim@x.example")

    def inventory_with(self, sot, channels):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp)
        (tmp / "storefront.csv").write_text("item_id,status,on_hand\n" + "".join(
            f"{i},{st},{q}\n" for i, st, q in sot), encoding="utf-8")
        for name, rows in channels.items():
            (tmp / name).write_text("item_id,status,listed_qty\n" + "".join(
                f"{i},{st},{q}\n" for i, st, q in rows), encoding="utf-8")
        return {f.key for f in check_inventory(tmp)}

    def test_multi_unit_oversell(self):
        flagged = self.inventory_with(
            [("SK-1", "live", 2), ("SK-2", "live", 4), ("SK-3", "live", 4), ("SK-4", "sold", 0)],
            {"a.csv": [("SK-1", "live", 3), ("SK-2", "live", 3), ("SK-3", "live", 2), ("SK-4", "live", 1)],
             "b.csv": [("SK-1", "live", 1), ("SK-2", "live", 2), ("SK-3", "ended", 5)]})
        self.assertIn(("I5", "SK-1"), flagged)  # one channel alone lists 3 of 2
        self.assertNotIn(("I6", "SK-1"), flagged)
        self.assertIn(("I6", "SK-2"), flagged)  # 3 + 2 of 4
        self.assertNotIn(("I6", "SK-3"), flagged)  # an ended listing's quantity doesn't count
        self.assertIn(("I1", "SK-4"), flagged)
        self.assertNotIn(("I5", "SK-4"), flagged)

    def test_bad_quantity_is_a_clear_error(self):
        with self.assertRaisesRegex(InputError, "listed_qty.*not a whole number"):
            self.inventory_with([("SK-1", "live", 2)], {"a.csv": [("SK-1", "live", "two")]})

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

    def test_correct_all_clear_is_perfect(self):
        clean = {"pattern": "crm", "findings": [], "negatives": []}
        s = score(clean, parse_findings(block([])))
        self.assertEqual((s.precision, s.recall), (1.0, 1.0))
        s = score(self.key, parse_findings(block([])))  # silence when there are findings is not precise
        self.assertEqual((s.precision, s.recall), (0.0, 0.0))

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
    "inv-messy": (9, 0, 0),
    "crm-1": (13, 0, 0),
    "crm-2": (11, 0, 0),
    "crm-3": (11, 0, 0),
    "crm-messy": (15, 0, 1),  # missed E2 P05, see tests/answer_keys/crm-messy.json "revisions"
}


def sha256(path):
    # hash LF-normalised bytes so a Windows checkout with autocrlf gives the same value as CI
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


class CommittedRuns(unittest.TestCase):
    def test_every_dataset_has_a_run(self):
        self.assertEqual({p.parent.name for p in RUNS.glob("*/output.md")}, {k["dataset"] for k in all_keys()})

    def test_scores_are_pinned(self):
        self.assertEqual(set(EXPECTED_RUN_SCORES), {k["dataset"] for k in all_keys()})
        for name, (tp, fp, fn) in EXPECTED_RUN_SCORES.items():
            with self.subTest(dataset=name):
                s = score(load_key(name), parse_findings((RUNS / name / "output.md").read_text(encoding="utf-8")))
                self.assertEqual((len(s.tp), len(s.fp), len(s.fn)), (tp, fp, fn))

    def test_run_metadata(self):
        for name in EXPECTED_RUN_SCORES:
            with self.subTest(dataset=name):
                meta = json.loads((RUNS / name / "run.json").read_text(encoding="utf-8"))
                for field in ("date", "model", "prompt", "command", "tools_available", "files_given", "output_sha256"):
                    self.assertIn(field, meta)
                self.assertEqual(meta["tools_available"], ["Read", "Grep", "Glob"])
                self.assertNotIn("Write", meta["prompt"])
                given = [f["path"] for f in meta["files_given"]]
                self.assertFalse([g for g in given if "output" in g or "answer" in g or g.endswith(".json")])
                self.assertNotRegex(json.dumps(meta), r"[A-Za-z]:[\\/]|/Users/|/home/")  # no local paths

    def test_run_hashes_match_the_files_in_this_repo(self):
        for name in EXPECTED_RUN_SCORES:
            meta = json.loads((RUNS / name / "run.json").read_text(encoding="utf-8"))
            with self.subTest(dataset=name, file="output.md"):
                self.assertEqual(sha256(RUNS / name / "output.md"), meta["output_sha256"])
            for f in meta["files_given"]:
                with self.subTest(dataset=name, file=f["copy_of"]):
                    self.assertEqual(sha256(ROOT / f["copy_of"]), f["sha256"])


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

    def test_two_changes_to_one_field_are_refused(self):
        twice = dict(self.spec["changes"][0], new="2026-10-06")
        spec = {"approved_by": "Mia", "changes": [self.spec["changes"][0], twice]}
        before = (self.d / "partners.csv").read_bytes()
        with self.assertRaisesRegex(apply_changes.ChangeError, "overwrite each other"):
            apply_changes.apply(self.d, spec, self.log)
        self.assertEqual((self.d / "partners.csv").read_bytes(), before)

    def test_id_column_is_found_by_name_not_position(self):
        path = self.d / "contacts.csv"
        with path.open(newline="", encoding="utf-8") as f:
            rows = list(csv.reader(f))
        rows = [[r[1], r[0], *r[2:]] for r in rows]  # partner_id first, contact_id second
        with path.open("w", newline="", encoding="utf-8") as f:
            csv.writer(f, lineterminator="\n").writerows(rows)
        apply_changes.apply(self.d, self.spec, self.log)
        with path.open(newline="", encoding="utf-8") as f:
            by_contact = {r["contact_id"]: r for r in csv.DictReader(f)}
        self.assertEqual(by_contact["C11"]["status"], "Bounced")
        self.assertEqual(by_contact["C09"]["status"], "Active")  # same partner P09, untouched

    def test_interrupted_apply_leaves_a_journal_and_blocks_the_next_run(self):
        real = os.replace
        calls = []

        def failing(src, dst):
            calls.append(dst)
            if len(calls) == 2:
                raise OSError("disk full")
            real(src, dst)

        apply_changes.os.replace = failing
        try:
            with self.assertRaises(OSError):
                apply_changes.apply(self.d, self.spec, self.log)
        finally:
            apply_changes.os.replace = real
        self.assertFalse(self.log.exists())  # the log is written only after every file is replaced
        journal = apply_changes.journal_path(self.log)
        self.assertEqual(len(json.loads(journal.read_text(encoding="utf-8"))["changes"]), 2)
        with self.assertRaisesRegex(apply_changes.ChangeError, "did not finish"):
            apply_changes.apply(self.d, self.spec, self.log)

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

    def test_daily_job_counts_from_its_own_first_line(self):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp)
        (tmp / "schedule.json").write_text(json.dumps({"jobs": {
            "old-job": {"every": "day"}, "new-job": {"every": "day"}, "never-ran": {"every": "day"}}}),
            encoding="utf-8")
        lines = ["2026-10-01,old-job,run", "2026-10-02,old-job,run", "2026-10-03,old-job,run",
                 "2026-10-02,new-job,run", "2026-10-03,new-job,run", "2026-10-01,never-ran,read"]
        (tmp / "run-log.csv").write_text("date,job,action,target,field,old,new,items\n" + "".join(
            f"{x},,,,,\n" for x in lines), encoding="utf-8")
        found = {(r, e) for r, e, _ in run_log_check.check(tmp)}
        self.assertEqual(found, {("S1", "never-ran")})

    def test_empty_log_is_an_error(self):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp)
        shutil.copy(ROOT / "examples/scheduled/healthy/schedule.json", tmp)
        (tmp / "run-log.csv").write_text("date,job,action,target,field,old,new,items\n", encoding="utf-8")
        with self.assertRaisesRegex(run_log_check.InputError, "empty"):
            run_log_check.check(tmp)


class OutreachCheck(unittest.TestCase):
    def setUp(self):
        self.queue = outreach_check.load(ROOT / "examples/outreach/queue.json")

    def test_example_queue_has_one_finding_per_rule(self):
        found = {(r, d) for r, d, _ in outreach_check.check(self.queue)}
        self.assertEqual(found, {("O1", "D02"), ("O2", "D03"), ("O3", "D02"), ("O4", "D04"), ("O5", "D06")})

    def test_approved_and_sent_by_a_person_is_clear(self):
        d = dict(self.queue["drafts"][0])
        self.assertEqual(outreach_check.check({"drafts": [d]}), [])

    def test_approval_after_sending_does_not_count(self):
        d = dict(self.queue["drafts"][0], approved_at="2026-11-02T10:00:00")
        self.assertEqual([r for r, _, _ in outreach_check.check({"drafts": [d]})], ["O1"])

    def test_malformed_queue_is_an_error(self):
        with self.assertRaises(outreach_check.InputError):
            outreach_check.check({"drafts": [dict(self.queue["drafts"][0], sent_at="yesterday")]})


class Links(unittest.TestCase):
    def test_relative_links_and_anchors_resolve(self):
        self.assertEqual(broken_links(), [])


if __name__ == "__main__":
    unittest.main()
