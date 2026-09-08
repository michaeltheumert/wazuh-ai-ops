#!/usr/bin/env python3
"""Validate a candidate Wazuh rule against parser and match-behaviour checks.

The command installs a candidate XML rule temporarily in a non-production Wazuh
container, runs ``wazuh-analysisd -t``, then feeds positive and negative fixture
lines through ``wazuh-logtest``. It succeeds only when every positive fixture
matches the expected rule ID and every negative fixture avoids that rule ID.

No claim is made that a rule is validated until this script has actually been
run against a named Wazuh version and its result recorded.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Iterable

RULE_ID_RE = re.compile(r"\bid:\s*['\"]?(\d+)['\"]?")


def run(command: list[str], *, stdin: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        input=stdin,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def load_fixtures(path: Path) -> list[str]:
    lines: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        lines.append(line)
    if not lines:
        raise ValueError(f"fixture file contains no events: {path}")
    return lines


def matched_rule_ids(output: str) -> set[str]:
    return set(RULE_ID_RE.findall(output))


def run_logtest(container: str, event: str) -> tuple[set[str], str]:
    result = run(
        ["docker", "exec", "-i", container, "/var/ossec/bin/wazuh-logtest"],
        stdin=event + "\n",
    )
    return matched_rule_ids(result.stdout), result.stdout


def check_events(
    *,
    container: str,
    fixtures: Iterable[str],
    expected_rule_id: str,
    should_match: bool,
    label: str,
) -> bool:
    ok = True
    for index, event in enumerate(fixtures, start=1):
        rule_ids, output = run_logtest(container, event)
        matched = expected_rule_id in rule_ids
        passed = matched if should_match else not matched
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {label} fixture {index}: expected rule {expected_rule_id} "
              f"to {'match' if should_match else 'stay silent'}")
        if not passed:
            ok = False
            print("  event:", event)
            print("  observed rule ids:", ", ".join(sorted(rule_ids)) or "none")
            print("  wazuh-logtest output:")
            print(output.rstrip())
    return ok


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--container", required=True, help="Docker container running the non-production Wazuh manager")
    parser.add_argument("--rule-file", required=True, type=Path, help="Candidate Wazuh XML rule file")
    parser.add_argument("--expected-rule-id", required=True, help="Rule ID that positive fixtures must match")
    parser.add_argument("--positive", required=True, type=Path, help="Text file with one positive log event per line")
    parser.add_argument("--negative", required=True, type=Path, help="Text file with one negative log event per line")
    args = parser.parse_args()

    for path in (args.rule_file, args.positive, args.negative):
        if not path.is_file():
            parser.error(f"file not found: {path}")

    try:
        positive = load_fixtures(args.positive)
        negative = load_fixtures(args.negative)
    except ValueError as exc:
        parser.error(str(exc))

    remote_rule = f"/var/ossec/etc/rules/_ai_ops_candidate_{os.getpid()}.xml"

    copy_result = run(["docker", "cp", str(args.rule_file), f"{args.container}:{remote_rule}"])
    if copy_result.returncode != 0:
        print(copy_result.stdout, file=sys.stderr)
        return 2

    try:
        syntax = run([
            "docker", "exec", args.container,
            "/var/ossec/bin/wazuh-analysisd", "-t",
        ])
        if syntax.returncode != 0:
            print("[FAIL] wazuh-analysisd -t rejected the candidate rule")
            print(syntax.stdout.rstrip())
            return 1
        print("[PASS] wazuh-analysisd -t accepted the candidate rule")

        positives_ok = check_events(
            container=args.container,
            fixtures=positive,
            expected_rule_id=args.expected_rule_id,
            should_match=True,
            label="positive",
        )
        negatives_ok = check_events(
            container=args.container,
            fixtures=negative,
            expected_rule_id=args.expected_rule_id,
            should_match=False,
            label="negative",
        )

        if positives_ok and negatives_ok:
            print("[PASS] candidate rule passed parser and match-behaviour validation")
            return 0

        print("[FAIL] candidate rule failed match-behaviour validation")
        return 1
    finally:
        cleanup = run(["docker", "exec", args.container, "rm", "-f", remote_rule])
        if cleanup.returncode != 0:
            print("warning: failed to remove temporary candidate rule", file=sys.stderr)
            print(cleanup.stdout.rstrip(), file=sys.stderr)


if __name__ == "__main__":
    raise SystemExit(main())
