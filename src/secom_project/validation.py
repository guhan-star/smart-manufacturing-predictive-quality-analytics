"""Phase 3 — Timestamp-group-safe chronological splitting and expanding-window validation."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from secom_project import DATA_RAW_DIR, MODELS_DIR
from secom_project.data_validation import load_and_parse_raw_secom


@dataclass(frozen=True)
class ExpandingFold:
    """Single chronological expanding-window CV fold with strict timestamp-group separation."""

    fold_id: int
    train_indices: np.ndarray
    val_indices: np.ndarray
    train_start: str
    train_end: str
    val_start: str
    val_end: str
    train_rows: int
    train_fails: int
    train_passes: int
    val_rows: int
    val_fails: int
    val_passes: int


@dataclass(frozen=True)
class ChronologicalSplitPlan:
    """Complete chronological split plan separating pre-holdout expanding CV from untouched final holdout."""

    pre_holdout_indices: np.ndarray
    holdout_indices: np.ndarray
    expanding_folds: tuple[ExpandingFold, ...]
    holdout_start: str
    holdout_end: str
    pre_holdout_start: str
    pre_holdout_end: str
    pre_holdout_rows: int
    pre_holdout_fails: int
    pre_holdout_passes: int
    holdout_rows: int
    holdout_fails: int
    holdout_passes: int

    def to_metadata_dict(self) -> dict:
        """Return JSON-serializable split boundary and class-balance metadata."""
        return {
            "strategy": "Timestamp-group-safe chronological expanding-window CV + untouched October 2008 holdout",
            "pre_holdout": {
                "start_timestamp": self.pre_holdout_start,
                "end_timestamp": self.pre_holdout_end,
                "rows": self.pre_holdout_rows,
                "passes_minus1": self.pre_holdout_passes,
                "fails_1": self.pre_holdout_fails,
                "fail_rate_pct": round(self.pre_holdout_fails / self.pre_holdout_rows * 100.0, 4),
            },
            "final_holdout": {
                "start_timestamp": self.holdout_start,
                "end_timestamp": self.holdout_end,
                "rows": self.holdout_rows,
                "passes_minus1": self.holdout_passes,
                "fails_1": self.holdout_fails,
                "fail_rate_pct": round(self.holdout_fails / self.holdout_rows * 100.0, 4),
            },
            "expanding_folds": [
                {
                    "fold_id": f.fold_id,
                    "train_start": f.train_start,
                    "train_end": f.train_end,
                    "val_start": f.val_start,
                    "val_end": f.val_end,
                    "train_rows": f.train_rows,
                    "train_passes": f.train_passes,
                    "train_fails": f.train_fails,
                    "train_fail_rate_pct": round(f.train_fails / f.train_rows * 100.0, 4),
                    "val_rows": f.val_rows,
                    "val_passes": f.val_passes,
                    "val_fails": f.val_fails,
                    "val_fail_rate_pct": round(f.val_fails / f.val_rows * 100.0, 4),
                }
                for f in self.expanding_folds
            ],
        }


def prepare_chronological_dataset(
    raw_dir: Path = DATA_RAW_DIR,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series]:
    """Load raw SECOM tables, sort stably by timestamp, and return (sensors_df, labels_df, y_binary)."""
    sensors_df, labels_df = load_and_parse_raw_secom(raw_dir)
    work_labels = labels_df.copy()
    work_labels["_orig_idx"] = np.arange(len(work_labels))

    if not work_labels["timestamp"].is_monotonic_increasing:
        work_labels = work_labels.sort_values(["timestamp", "_orig_idx"], kind="mergesort")
        sensors_df = sensors_df.iloc[work_labels["_orig_idx"].to_numpy()].reset_index(drop=True)
        work_labels = work_labels.reset_index(drop=True)

    work_labels["timestamp_group_id"] = (
        work_labels["timestamp"].ne(work_labels["timestamp"].shift()).cumsum() - 1
    )
    y_binary = (work_labels["target_label"] == 1).astype(int)
    work_labels = work_labels.drop(columns=["_orig_idx"])
    return sensors_df, work_labels, y_binary


@dataclass(frozen=True)
class TrainValTestSplit:
    """Three-way chronological Train / Validation / Test split with intact timestamp groups."""

    train_indices: np.ndarray
    val_indices: np.ndarray
    test_indices: np.ndarray
    train_start: str
    train_end: str
    val_start: str
    val_end: str
    test_start: str
    test_end: str
    train_rows: int
    train_fails: int
    train_passes: int
    val_rows: int
    val_fails: int
    val_passes: int
    test_rows: int
    test_fails: int
    test_passes: int

    def to_metadata_dict(self) -> dict:
        """Return JSON-serializable split boundaries and Pass/Fail counts."""
        return {
            "strategy": "Timestamp-group-intact chronological 3-way split (Train -> Validation -> Held-out Test)",
            "train": {
                "start_timestamp": self.train_start,
                "end_timestamp": self.train_end,
                "rows": self.train_rows,
                "passes_minus1": self.train_passes,
                "fails_1": self.train_fails,
                "fail_rate_pct": round(self.train_fails / self.train_rows * 100.0, 4),
            },
            "validation": {
                "start_timestamp": self.val_start,
                "end_timestamp": self.val_end,
                "rows": self.val_rows,
                "passes_minus1": self.val_passes,
                "fails_1": self.val_fails,
                "fail_rate_pct": round(self.val_fails / self.val_rows * 100.0, 4),
            },
            "test": {
                "start_timestamp": self.test_start,
                "end_timestamp": self.test_end,
                "rows": self.test_rows,
                "passes_minus1": self.test_passes,
                "fails_1": self.test_fails,
                "fail_rate_pct": round(self.test_fails / self.test_rows * 100.0, 4),
            },
        }


def build_train_val_test_splits(
    labels_df: pd.DataFrame,
    pre_test_train_frac: float = 0.60,
    test_cutoff: str = "2008-10-01 00:00:00",
) -> TrainValTestSplit:
    """Create a chronological Train / Validation / Test split keeping identical timestamps together."""
    cutoff_ts = pd.Timestamp(test_cutoff)
    ts = labels_df["timestamp"]

    pre_idx = np.where((ts < cutoff_ts).to_numpy())[0]
    test_idx = np.where((ts >= cutoff_ts).to_numpy())[0]
    if len(pre_idx) == 0 or len(test_idx) == 0:
        raise ValueError("Pre-test and test partitions must both be non-empty.")

    pre_df = labels_df.iloc[pre_idx].copy()
    grp_summary = (
        pre_df.groupby("timestamp_group_id", sort=True)
        .agg(n=("target_label", "size"))
        .reset_index()
    )
    grp_summary["cum_n"] = grp_summary["n"].cumsum()
    target_n = int(round(len(pre_idx) * pre_test_train_frac))
    train_end_pos = int(grp_summary.loc[grp_summary["cum_n"] >= target_n, "cum_n"].iloc[0])

    train_idx = pre_idx[:train_end_pos]
    val_idx = pre_idx[train_end_pos:]

    # Enforce strict chronological and timestamp-group integrity
    for a_name, a_idx, b_name, b_idx in [
        ("train", train_idx, "validation", val_idx),
        ("validation", val_idx, "test", test_idx),
    ]:
        if set(labels_df["timestamp_group_id"].iloc[a_idx]) & set(
            labels_df["timestamp_group_id"].iloc[b_idx]
        ):
            raise ValueError(f"Repeated timestamp group split across {a_name} and {b_name}.")
        if ts.iloc[a_idx].max() >= ts.iloc[b_idx].min():
            raise ValueError(f"Chronological violation between {a_name} and {b_name}.")

    y_bin = (labels_df["target_label"] == 1).to_numpy()

    return TrainValTestSplit(
        train_indices=train_idx,
        val_indices=val_idx,
        test_indices=test_idx,
        train_start=str(ts.iloc[train_idx].min()),
        train_end=str(ts.iloc[train_idx].max()),
        val_start=str(ts.iloc[val_idx].min()),
        val_end=str(ts.iloc[val_idx].max()),
        test_start=str(ts.iloc[test_idx].min()),
        test_end=str(ts.iloc[test_idx].max()),
        train_rows=int(len(train_idx)),
        train_fails=int(y_bin[train_idx].sum()),
        train_passes=int((~y_bin[train_idx]).sum()),
        val_rows=int(len(val_idx)),
        val_fails=int(y_bin[val_idx].sum()),
        val_passes=int((~y_bin[val_idx]).sum()),
        test_rows=int(len(test_idx)),
        test_fails=int(y_bin[test_idx].sum()),
        test_passes=int((~y_bin[test_idx]).sum()),
    )


def build_chronological_splits(
    labels_df: pd.DataFrame,
    holdout_cutoff: str = "2008-10-01 00:00:00",
    expanding_fractions: tuple[float, ...] = (0.40, 0.60, 0.80, 1.00),
) -> ChronologicalSplitPlan:
    """Create timestamp-group-intact expanding CV folds and untouched final chronological holdout."""
    cutoff_ts = pd.Timestamp(holdout_cutoff)
    ts = labels_df["timestamp"]

    pre_mask = (ts < cutoff_ts).to_numpy()
    holdout_mask = (ts >= cutoff_ts).to_numpy()

    pre_idx = np.where(pre_mask)[0]
    holdout_idx = np.where(holdout_mask)[0]

    if len(pre_idx) == 0 or len(holdout_idx) == 0:
        raise ValueError("Both pre-holdout and final holdout splits must be non-empty.")

    pre_ts = set(ts.iloc[pre_idx])
    holdout_ts = set(ts.iloc[holdout_idx])
    if pre_ts & holdout_ts:
        raise ValueError("Shared timestamp found across pre-holdout and holdout boundary.")
    if ts.iloc[pre_idx].max() >= ts.iloc[holdout_idx].min():
        raise ValueError("Chronological violation between pre-holdout and holdout.")

    # Build group-respecting boundaries within pre_idx
    pre_df = labels_df.iloc[pre_idx].copy()
    pre_df["_pos"] = pre_idx
    grp_summary = (
        pre_df.groupby("timestamp_group_id", sort=True)
        .agg(
            n=("target_label", "size"),
            last_pos=("_pos", "max"),
            ts=("timestamp", "first"),
        )
        .reset_index()
    )
    grp_summary["cum_n"] = grp_summary["n"].cumsum()

    total_pre = len(pre_idx)
    cut_positions = [0]
    for frac in expanding_fractions[:-1]:
        target_n = int(round(total_pre * frac))
        hit = grp_summary.loc[grp_summary["cum_n"] >= target_n].iloc[0]
        # Slice position in pre_idx is cum_n
        cut_positions.append(int(hit["cum_n"]))
    cut_positions.append(total_pre)

    # Deduplicate monotonic cuts if tiny dataset
    if len(set(cut_positions)) != len(cut_positions):
        raise ValueError(f"Degenerate expanding-window cuts: {cut_positions}")

    folds: list[ExpandingFold] = []
    for fold_num in range(1, len(cut_positions) - 1):
        tr_end = cut_positions[fold_num]
        va_end = cut_positions[fold_num + 1]
        tr_idx = pre_idx[:tr_end]
        va_idx = pre_idx[tr_end:va_end]

        tr_ts = ts.iloc[tr_idx]
        va_ts = ts.iloc[va_idx]
        if set(tr_ts) & set(va_ts):
            raise ValueError(f"Fold {fold_num} splits a repeated timestamp group!")
        if tr_ts.max() >= va_ts.min():
            raise ValueError(f"Fold {fold_num} violates strict chronological ordering!")

        tr_y = (labels_df["target_label"].iloc[tr_idx] == 1).to_numpy()
        va_y = (labels_df["target_label"].iloc[va_idx] == 1).to_numpy()

        folds.append(
            ExpandingFold(
                fold_id=fold_num,
                train_indices=tr_idx,
                val_indices=va_idx,
                train_start=str(tr_ts.min()),
                train_end=str(tr_ts.max()),
                val_start=str(va_ts.min()),
                val_end=str(va_ts.max()),
                train_rows=int(len(tr_idx)),
                train_fails=int(tr_y.sum()),
                train_passes=int((~tr_y).sum()),
                val_rows=int(len(va_idx)),
                val_fails=int(va_y.sum()),
                val_passes=int((~va_y).sum()),
            )
        )

    pre_y = (labels_df["target_label"].iloc[pre_idx] == 1).to_numpy()
    hold_y = (labels_df["target_label"].iloc[holdout_idx] == 1).to_numpy()

    return ChronologicalSplitPlan(
        pre_holdout_indices=pre_idx,
        holdout_indices=holdout_idx,
        expanding_folds=tuple(folds),
        holdout_start=str(ts.iloc[holdout_idx].min()),
        holdout_end=str(ts.iloc[holdout_idx].max()),
        pre_holdout_start=str(ts.iloc[pre_idx].min()),
        pre_holdout_end=str(ts.iloc[pre_idx].max()),
        pre_holdout_rows=int(len(pre_idx)),
        pre_holdout_fails=int(pre_y.sum()),
        pre_holdout_passes=int((~pre_y).sum()),
        holdout_rows=int(len(holdout_idx)),
        holdout_fails=int(hold_y.sum()),
        holdout_passes=int((~hold_y).sum()),
    )


def main() -> None:
    _, labels_df, _ = prepare_chronological_dataset()
    plan = build_chronological_splits(labels_df)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    meta = plan.to_metadata_dict()
    (MODELS_DIR / "split_boundaries.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
