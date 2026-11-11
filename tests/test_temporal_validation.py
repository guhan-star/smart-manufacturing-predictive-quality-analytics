"""Tests for Phase 3 chronological 3-way splitting and repeated-timestamp group integrity."""

from __future__ import annotations

from secom_project import DATA_RAW_DIR
from secom_project.validation import build_train_val_test_splits, prepare_chronological_dataset


def test_chronological_order_and_target_mapping() -> None:
    sensors_df, labels_df, y_binary = prepare_chronological_dataset(DATA_RAW_DIR)
    assert len(sensors_df) == len(labels_df) == len(y_binary) == 1567
    assert bool(labels_df["timestamp"].is_monotonic_increasing) is True
    assert int((y_binary == 0).sum()) == 1463
    assert int((y_binary == 1).sum()) == 104
    assert ((labels_df["target_label"] == 1).astype(int) == y_binary).all()


def test_train_val_test_split_and_timestamp_group_integrity() -> None:
    _, labels_df, y_binary = prepare_chronological_dataset(DATA_RAW_DIR)
    plan = build_train_val_test_splits(labels_df)

    # Disjoint complete partition
    all_idx = np.concatenate([plan.train_indices, plan.val_indices, plan.test_indices]) if False else (
        list(plan.train_indices) + list(plan.val_indices) + list(plan.test_indices)
    )
    assert len(all_idx) == 1567
    assert len(set(all_idx)) == 1567

    tr_ts = labels_df.iloc[plan.train_indices]["timestamp"]
    va_ts = labels_df.iloc[plan.val_indices]["timestamp"]
    te_ts = labels_df.iloc[plan.test_indices]["timestamp"]
    assert tr_ts.max() < va_ts.min()
    assert va_ts.max() < te_ts.min()

    tr_grp = set(labels_df.iloc[plan.train_indices]["timestamp_group_id"])
    va_grp = set(labels_df.iloc[plan.val_indices]["timestamp_group_id"])
    te_grp = set(labels_df.iloc[plan.test_indices]["timestamp_group_id"])
    assert tr_grp.isdisjoint(va_grp)
    assert va_grp.isdisjoint(te_grp)
    assert tr_grp.isdisjoint(te_grp)

    assert int(y_binary.iloc[plan.train_indices].sum()) > 0
    assert int(y_binary.iloc[plan.val_indices].sum()) > 0
    assert int(y_binary.iloc[plan.test_indices].sum()) > 0
