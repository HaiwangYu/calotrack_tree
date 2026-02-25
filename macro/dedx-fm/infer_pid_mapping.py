#!/usr/bin/env python3
"""
Infer pid_true_class -> abs(pid_pid_target) mapping from a CSV file.

Usage:
  python infer_pid_mapping.py --input /path/to/file.csv

Optional:
  --chunksize 1000000
  --quiet
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict

import pandas as pd

REQUIRED_COLUMNS = ["pid_pid_target", "pid_true_class"]
TARGET_CLASSES = {0, 1, 2, 3, 4}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Infer 1-to-1 mapping: pid_true_class (0..4) -> abs(pid_pid_target)"
    )
    parser.add_argument("--input", required=True, help="Path to input CSV file.")
    parser.add_argument(
        "--chunksize",
        type=int,
        default=1_000_000,
        help="Rows per chunk for pandas.read_csv (default: 1000000).",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress progress/info logs (errors and final mapping still print).",
    )
    return parser.parse_args()


def log(msg: str, quiet: bool) -> None:
    if not quiet:
        print(msg)


def validate_columns(input_path: Path) -> None:
    header = pd.read_csv(input_path, nrows=0)
    missing = [col for col in REQUIRED_COLUMNS if col not in header.columns]
    if missing:
        raise ValueError(
            "Missing required column(s): "
            + ", ".join(missing)
            + f"\nAvailable columns: {', '.join(header.columns)}"
        )


def parse_int(value) -> int | None:
    if pd.isna(value):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def run(args: argparse.Namespace) -> int:
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: input file does not exist: {input_path}", file=sys.stderr)
        return 2

    if args.chunksize <= 0:
        print("ERROR: --chunksize must be a positive integer.", file=sys.stderr)
        return 2

    try:
        validate_columns(input_path)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    mapping: Dict[int, int] = {}
    used_pids: Dict[int, int] = {}
    warned_invalid_class = False

    chunk_idx = 0
    rows_scanned = 0

    reader = pd.read_csv(input_path, usecols=REQUIRED_COLUMNS, chunksize=args.chunksize)
    for chunk in reader:
        chunk_idx += 1
        rows_scanned += len(chunk)

        for row in chunk.itertuples(index=False):
            raw_pid = row.pid_pid_target
            raw_class = row.pid_true_class

            c = parse_int(raw_class)
            p_raw = parse_int(raw_pid)
            if c is None or p_raw is None:
                continue

            if c not in TARGET_CLASSES:
                if not warned_invalid_class and not args.quiet:
                    print(
                        f"Warning: encountered pid_true_class={c} outside [0,4]; "
                        "skipping such rows."
                    )
                    warned_invalid_class = True
                continue

            if c in mapping:
                continue

            p = abs(p_raw)
            if p in used_pids and used_pids[p] != c:
                print(
                    "ERROR: 1-to-1 conflict detected. "
                    f"class={c} wants abs(pid)={p}, "
                    f"but abs(pid)={p} is already assigned to class={used_pids[p]}.",
                    file=sys.stderr,
                )
                print(f"Current mapping: {dict(sorted(mapping.items()))}", file=sys.stderr)
                return 1

            mapping[c] = p
            used_pids[p] = c
            log(f"Discovered mapping: class {c} -> abs(pid) {p}", args.quiet)

            if len(mapping) == len(TARGET_CLASSES):
                break

        if len(mapping) == len(TARGET_CLASSES):
            log(
                f"All classes discovered by chunk {chunk_idx} after {rows_scanned} rows.",
                args.quiet,
            )
            break

        if not args.quiet and chunk_idx % 10 == 0:
            print(
                f"Processed chunk {chunk_idx}; rows_scanned={rows_scanned}; "
                f"found={len(mapping)}/{len(TARGET_CLASSES)}"
            )

    if len(mapping) != len(TARGET_CLASSES):
        missing = sorted(TARGET_CLASSES - set(mapping.keys()))
        print(
            "ERROR: could not infer complete mapping. "
            f"Missing classes: {missing}. Partial mapping: {dict(sorted(mapping.items()))}",
            file=sys.stderr,
        )
        return 1

    sorted_mapping = dict(sorted(mapping.items()))
    print(sorted_mapping)
    return 0


def main() -> None:
    args = parse_args()
    raise SystemExit(run(args))


if __name__ == "__main__":
    main()
