"""Tests for Phase 3 leakage-safe preprocessing, input validation, model training, and persistence."""

from __future__ import annotations

import json

import joblib
import numpy as np
import pytest
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from secom_project import DATA_RAW_DIR, MODELS_DIR
from secom_project.modeling import RANDOM_SEED, SecomTrainingPreprocessor, build_phase3_models
from secom_project.validation import build_train_val_test_splits, prepare_chronological_dataset


def test_preprocessor_ignores_target_and_test_data() -> None:
    sensors_df, labels_df, y_binary = prepare_chronological_dataset(DATA_RAW_DIR)
    plan = build_train_val_test_splits(labels_df)

    X_train = sensors_df.iloc[plan.train_indices]
    y_train = y_binary.iloc[plan.train_indices].to_numpy()
    X_test = sensors_df.iloc[plan.test_indices].copy()

    p1 = SecomTrainingPreprocessor(0.50, True, 0.99, False).fit(X_train, y_train)
    p2 = SecomTrainingPreprocessor(0.50, True, 0.99, False).fit(X_train, 1 - y_train)
    assert p1.kept_features_ == p2.kept_features_
    assert p1.medians_ == p2.medians_

    col0 = p1.kept_features_[0]
    X_test_mod = X_test.copy()
    X_test_mod[col0] = np.nan
    Xt = p1.transform(X_test_mod)
    assert np.allclose(Xt[:, 0], p1.medians_[col0])
    assert not np.isnan(Xt).any()
    assert not np.isinf(Xt).any()


def test_prediction_input_validation_rejects_bad_inputs() -> None:
    sensors_df, labels_df, _ = prepare_chronological_dataset(DATA_RAW_DIR)
    plan = build_train_val_test_splits(labels_df)
    X_train = sensors_df.iloc[plan.train_indices]
    prep = SecomTrainingPreprocessor(0.50, True, 0.99, False).fit(X_train)

    with pytest.raises(ValueError, match="cannot be empty"):
        prep.transform(X_train.iloc[0:0])

    with pytest.raises(ValueError, match="missing"):
        prep.transform(X_train.drop(columns=[prep.kept_features_[0]]))

    bad_str = X_train.iloc[:5].copy()
    bad_str[prep.kept_features_[0]] = "bad_value"
    with pytest.raises(ValueError, match="non-numeric"):
        prep.transform(bad_str)

    with pytest.raises(ValueError, match="must be 2D"):
        prep.transform(np.zeros((10,)))


def test_phase3_models_train_and_predict() -> None:
    sensors_df, labels_df, y_binary = prepare_chronological_dataset(DATA_RAW_DIR)
    plan = build_train_val_test_splits(labels_df)
    X_tr = sensors_df.iloc[plan.train_indices]
    y_tr = y_binary.iloc[plan.train_indices].to_numpy()
    X_va = sensors_df.iloc[plan.val_indices]

    models = build_phase3_models()
    assert set(models.keys()) == {
        "Dummy_Majority",
        "LogisticRegression",
        "RandomForest",
        "HistGradientBoosting",
    }
    for name, pipe in models.items():
        pipe.fit(X_tr, y_tr)
        probs = pipe.predict_proba(X_va)[:, 1]
        preds = pipe.predict(X_va)
        assert probs.shape == (len(X_va),)
        assert np.all((probs >= 0.0) & (probs <= 1.0))
        assert set(np.unique(preds)).issubset({0, 1})


def test_pipeline_reproducibility_with_fixed_seed() -> None:
    sensors_df, labels_df, y_binary = prepare_chronological_dataset(DATA_RAW_DIR)
    plan = build_train_val_test_splits(labels_df)
    X_tr = sensors_df.iloc[plan.train_indices]
    y_tr = y_binary.iloc[plan.train_indices].to_numpy()
    X_va = sensors_df.iloc[plan.val_indices]

    def make_pipe() -> Pipeline:
        return Pipeline(
            [
                ("prep", SecomTrainingPreprocessor(0.50, True, 0.99, False)),
                ("scaler", StandardScaler()),
                (
                    "clf",
                    LogisticRegression(
                        C=0.05,
                        l1_ratio=0.0,
                        solver="liblinear",
                        class_weight="balanced",
                        max_iter=2000,
                        random_state=RANDOM_SEED,
                    ),
                ),
            ]
        )

    m1 = make_pipe().fit(X_tr, y_tr)
    m2 = make_pipe().fit(X_tr, y_tr)
    np.testing.assert_allclose(m1.predict_proba(X_va), m2.predict_proba(X_va))


def test_saved_model_artifacts_and_predictions() -> None:
    meta_path = MODELS_DIR / "model_metadata.json"
    model_path = MODELS_DIR / "selected_model.joblib"
    assert meta_path.exists()
    assert model_path.exists()

    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    assert meta["trained_on_holdout"] is False
    assert meta["random_seed"] == RANDOM_SEED

    sensors_df, labels_df, _ = prepare_chronological_dataset(DATA_RAW_DIR)
    plan = build_train_val_test_splits(labels_df)
    X_test = sensors_df.iloc[plan.test_indices]

    loaded_model = joblib.load(model_path)
    probs = loaded_model.predict_proba(X_test)[:, 1]
    assert probs.shape == (len(X_test),)
    assert np.all((probs >= 0.0) & (probs <= 1.0))
