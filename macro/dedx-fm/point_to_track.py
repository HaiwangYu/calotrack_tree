#!/usr/bin/env python3
"""
Convert per-point CSV rows into per-reco-track rows using majority voting.

Usage:
  python point_to_track.py --input /path/to/input.csv --output /path/to/output.csv

If --output is omitted, output is written next to input as:
  <input_stem>_per_track.csv
"""

from __future__ import annotations

import argparse
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Tuple

import pandas as pd

REQUIRED_COLUMNS = [
    "track_batch_idx",
    "track_pred_assignment",
    "track_energy",
    "track_seg_target",
    "pid_pred_class",
    "pid_true_class",
]

VOTE_COLUMNS = [
    "track_energy",
    "pid_pred_class",
    "pid_true_class",
]

OUTPUT_COLUMNS = [
    "track_pred_assignment",
    "track_energy_majority",
    "pid_pred_class_majority",
    "pid_true_class_majority",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Aggregate per-point CSV into per-reco-track CSV by majority vote."
    )
    parser.add_argument("--input", required=True, help="Path to input per-point CSV.")
    parser.add_argument(
        "--output",
        default=None,
        help="Path to output per-track CSV. Defaults to <input>_per_track.csv",
    )
    parser.add_argument(
        "--chunksize",
        type=int,
        default=200000,
        help="Number of rows per chunk for pandas.read_csv (default: 200000).",
    )
    parser.add_argument(
        "--log-every",
        type=int,
        default=10,
        help="Print progress every N chunks (default: 10).",
    )
    return parser.parse_args()


def is_missing(value: Any) -> bool:
    return pd.isna(value)


def coerce_sortable(value: Any) -> Tuple[int, Any]:
    """
    Deterministic key used for stable ordering.
    Priority:
      1) Numeric values sorted numerically.
      2) Non-numeric values sorted lexicographically by string form.
    """
    if is_missing(value):
        return (2, "")

    if isinstance(value, bool):
        return (1, str(value))

    try:
        numeric = float(value)
        if math.isfinite(numeric):
            return (0, numeric)
    except (TypeError, ValueError):
        pass

    return (1, str(value))


def choose_majority(counter: Counter) -> Any:
    """
    Return the majority value from a Counter with deterministic tie-break:
    - If tied and values are numeric/coercible numeric, choose smallest numeric value.
    - Otherwise choose lexicographically smallest string representation.
    """
    if not counter:
        return ""

    max_count = max(counter.values())
    candidates = [k for k, v in counter.items() if v == max_count]
    chosen = min(candidates, key=coerce_sortable)
    return chosen


def build_output_path(input_path: Path, output_path: str | None) -> Path:
    if output_path:
        return Path(output_path)
    return input_path.with_name(f"{input_path.stem}_per_track.csv")


def validate_columns(input_path: Path) -> None:
    header = pd.read_csv(input_path, nrows=0)
    missing = [col for col in REQUIRED_COLUMNS if col not in header.columns]
    if missing:
        msg = (
            "Missing required column(s): "
            + ", ".join(missing)
            + f"\nAvailable columns: {', '.join(header.columns)}"
        )
        raise ValueError(msg)


def update_aggregate(
    aggregate: Dict[Tuple[Any, Any], Dict[str, Counter]], chunk: pd.DataFrame
) -> int:
    groups = chunk.groupby(["track_batch_idx", "track_pred_assignment"], sort=False)
    group_count = 0
    for key, group_df in groups:
        group_count += 1
        per_field = aggregate[key]
        for column in VOTE_COLUMNS:
            counts = group_df[column].value_counts(dropna=True)
            if counts.empty:
                continue
            for value, count in counts.items():
                per_field[column][value] += int(count)
    return group_count


def run(args: argparse.Namespace) -> int:
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: input file does not exist: {input_path}", file=sys.stderr)
        return 2

    output_path = build_output_path(input_path, args.output)

    try:
        validate_columns(input_path)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    aggregate: Dict[Tuple[Any, Any], Dict[str, Counter]] = defaultdict(
        lambda: {col: Counter() for col in VOTE_COLUMNS}
    )

    total_rows = 0
    total_groups_seen = 0
    chunk_idx = 0

    reader = pd.read_csv(
        input_path,
        usecols=REQUIRED_COLUMNS,
        chunksize=args.chunksize,
    )

    for chunk in reader:
        chunk_idx += 1
        total_rows += len(chunk)
        total_groups_seen += update_aggregate(aggregate, chunk)
        if args.log_every > 0 and chunk_idx % args.log_every == 0:
            print(
                f"Processed chunk {chunk_idx} "
                f"(rows={total_rows}, unique_tracks={len(aggregate)})"
            )

    rows = []
    sorted_keys = sorted(
        aggregate.keys(),
        key=lambda k: (coerce_sortable(k[0]), coerce_sortable(k[1])),
    )
    for key in sorted_keys:
        field_counts = aggregate[key]
        rows.append(
            {
                "track_pred_assignment": key[1],
                "track_energy_majority": choose_majority(field_counts["track_energy"]),
                "pid_pred_class_majority": choose_majority(
                    field_counts["pid_pred_class"]
                ),
                "pid_true_class_majority": choose_majority(
                    field_counts["pid_true_class"]
                ),
            }
        )

    output_df = pd.DataFrame(rows, columns=OUTPUT_COLUMNS)
    output_df.to_csv(output_path, index=False)

    print(
        "Done. "
        f"chunks={chunk_idx}, rows={total_rows}, "
        f"groups_seen={total_groups_seen}, unique_tracks={len(output_df)}, "
        f"output={output_path}"
    )
    return 0


def main() -> None:
    args = parse_args()
    raise SystemExit(run(args))


if __name__ == "__main__":
    main()
