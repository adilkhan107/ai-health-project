#!/usr/bin/env python3
"""
Hackathon-ready advanced model training
Save as: model/model_training_hackathon.py

Example:
python model/model_training_hackathon.py --data_path dataset/health_dataset.csv --target diagnosis --out_dir model --use_text False --fast
"""
import os, json, argparse, warnings
from pathlib import Path
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, StratifiedKFold, RandomizedSearchCV, LeaveOneOut
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, StackingClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_auc_score
from imblearn.over_sampling import RandomOverSampler
from imblearn.pipeline import Pipeline as ImbPipeline

# try optional boosters
try:
    from xgboost import XGBClassifier
except Exception:
    XGBClassifier = None
try:
    from lightgbm import LGBMClassifier
except Exception:
    LGBMClassifier = None

RND = 42

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--data_path", required=True)
    p.add_argument("--target", required=True)
    p.add_argument("--out_dir", default="model")
    p.add_argument("--use_text", type=lambda x: x.lower()=='true', default=False)
    p.add_argument("--test_size", type=float, default=0.2)
    p.add_argument("--cv_folds", type=int, default=2)
    p.add_argument("--n_iter", type=int, default=8)
    p.add_argument("--fast", action="store_true", help="Faster small models for hackathon")
    return p.parse_args()

def auto_detect_columns(df, target):
    num = df.select_dtypes(include=[np.number]).columns.tolist()
    if target in num: num.remove(target)
    cat = df.select_dtypes(include=["object","category","bool"]).columns.tolist()
    if target in cat: cat.remove(target)
    # treat long text-like categorical as text candidates
    text_cand = [c for c in cat if df[c].dropna().astype(str).map(len).mean() > 25]
    cat_final = [c for c in cat if c not in text_cand]
    return num, cat_final, text_cand

def save_json(obj, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)

def plot_confusion(cm, labels, path):
    plt.figure(figsize=(6,5))
    sns.heatmap(cm, annot=True, fmt="d", xticklabels=labels, yticklabels=labels, cmap="Blues")
    plt.xlabel("Predicted"); plt.ylabel("True"); plt.title("Confusion Matrix")
    plt.tight_layout(); plt.savefig(path); plt.close()

def main():
    args = parse_args()
    out = Path(args.out_dir); out.mkdir(parents=True, exist_ok=True)

    print("[*] Loading:", args.data_path)
    df = pd.read_csv(args.data_path)
    target_col = next((col for col in df.columns if col.lower() == args.target.lower()), None)
    if target_col is None:
        raise SystemExit(f"Target {args.target} not in columns: {df.columns.tolist()}")
    args.target = target_col  # Use the actual column name

    numeric_cols, cat_cols, text_cols = auto_detect_columns(df, args.target)
    print("[*] Numeric:", numeric_cols)
    print("[*] Categorical:", cat_cols)
    print("[*] Text candidates:", text_cols)

    # Prepare X, y
    X = df.drop(columns=[args.target]).copy()
    # Remove ID columns (like Patient_ID) as they are not predictive features
    id_cols = [col for col in X.columns if col.lower().endswith('_id') or col.lower() == 'id']
    X = X.drop(columns=id_cols, errors='ignore')
    y_raw = df[args.target].astype(str).fillna("nan_missing")
    le_target = LabelEncoder(); y = le_target.fit_transform(y_raw)
    classes = list(le_target.classes_)
    print("[*] Classes:", classes)

    # Label-encode categorical short columns
    cat_encoders = {}
    for c in cat_cols:
        X[c] = X[c].astype(str).fillna("nan_missing")
        le = LabelEncoder()
        X[c] = le.fit_transform(X[c])
        cat_encoders[c] = le

    use_text = args.use_text and len(text_cols) > 0
    if use_text:
        text_col = text_cols[0]  # using first text column by default
        from sklearn.feature_extraction.text import TfidfVectorizer
        tfidf_max = 300 if args.fast else 1000
        tfidf = TfidfVectorizer(max_features=tfidf_max, ngram_range=(1,2))
        print("[*] TF-IDF on:", text_col, "max_features:", tfidf_max)
    else:
        tfidf = None

    # Preprocessing for numeric (scale) — cat already encoded
    num_pipeline = Pipeline([("imputer", SimpleImputer(strategy="median")), ("scale", StandardScaler())])
    transformers = []
    if numeric_cols:
        transformers.append(("num", num_pipeline, numeric_cols))
    if cat_cols:
        transformers.append(("cat", "passthrough", cat_cols))
    preproc = ColumnTransformer(transformers=transformers, remainder="drop")

    # Train/test split
    stratify_param = y if len(np.unique(y)) > 1 and min(np.bincount(y)) >= 2 else None
    X_train_df, X_test_df, y_train, y_test = train_test_split(X, y, test_size=args.test_size,
                                                              stratify=stratify_param, random_state=RND)
    # If text: fit tfidf and concat
    if use_text:
        tfidf.fit(X_train_df[text_col].fillna("nan_missing").astype(str))
        X_train_tfidf = tfidf.transform(X_train_df[text_col].fillna("nan_missing").astype(str))
        X_test_tfidf = tfidf.transform(X_test_df[text_col].fillna("nan_missing").astype(str))
        X_train_df = X_train_df.drop(columns=[text_col]); X_test_df = X_test_df.drop(columns=[text_col])

    # Fit preprocessor
    X_train_proc = preproc.fit_transform(X_train_df)
    X_test_proc = preproc.transform(X_test_df)
    # convert to DataFrame for easy concat
    feat_cols = (numeric_cols + cat_cols)
    X_train_proc = pd.DataFrame(X_train_proc, columns=feat_cols)
    X_test_proc = pd.DataFrame(X_test_proc, columns=feat_cols)

    if use_text:
        tf_cols = [f"tfidf_{i}" for i in range(X_train_tfidf.shape[1])]
        X_train_tfidf_df = pd.DataFrame.sparse.from_spmatrix(X_train_tfidf, columns=tf_cols)
        X_test_tfidf_df = pd.DataFrame.sparse.from_spmatrix(X_test_tfidf, columns=tf_cols)
        X_train_final = pd.concat([X_train_proc.reset_index(drop=True), X_train_tfidf_df.reset_index(drop=True)], axis=1)
        X_test_final = pd.concat([X_test_proc.reset_index(drop=True), X_test_tfidf_df.reset_index(drop=True)], axis=1)
    else:
        X_train_final = X_train_proc; X_test_final = X_test_proc

    print("[*] Final feature shapes:", X_train_final.shape, X_test_final.shape)

    # RandomOverSampler + model candidates
    smote = RandomOverSampler(random_state=RND)

    candidates = {}
    if XGBClassifier is not None:
        candidates["xgb"] = XGBClassifier(use_label_encoder=False, eval_metric="mlogloss", random_state=RND, n_jobs=-1)
    if LGBMClassifier is not None:
        candidates["lgbm"] = LGBMClassifier(random_state=RND, n_jobs=-1)
    candidates["rf"] = RandomForestClassifier(random_state=RND, n_jobs=-1)

    print("[*] Candidates:", list(candidates.keys()))
    # Param grids (light)
    param_grid = {
        "xgb": {"clf__n_estimators":[100,200] if not args.fast else [50], "clf__max_depth":[3,6],"clf__learning_rate":[0.01,0.1]},
        "lgbm": {"clf__n_estimators":[100,200] if not args.fast else [50], "clf__num_leaves":[31,60],"clf__learning_rate":[0.01,0.1]},
        "rf": {"clf__n_estimators":[100,200] if not args.fast else [50], "clf__max_depth":[None,10,20]}
    }

    best_estimators = {}
    min_class_count = min(np.bincount(y_train))
    if min_class_count < 2:
        cv = LeaveOneOut()
    else:
        cv = StratifiedKFold(n_splits=min(args.cv_folds, min_class_count), shuffle=True, random_state=RND)
    for name, base in candidates.items():
        print(f"[*] Tuning {name} ...")
        pipe = ImbPipeline([("smote", smote), ("clf", base)])
        params = param_grid.get(name, {})
        if params:
            search = RandomizedSearchCV(pipe, params, n_iter=min(args.n_iter,6), cv=cv, scoring="roc_auc", n_jobs=-1, random_state=RND, verbose=0)
            try:
                search.fit(X_train_final, y_train)
                best = search.best_estimator_
                print(f"[+] {name} best cv score: {search.best_score_:.4f}")
            except Exception as e:
                print("[!] search failed:", e); pipe.fit(X_train_final, y_train); best = pipe
        else:
            pipe.fit(X_train_final, y_train); best = pipe
        best_estimators[name] = best

    # Build stacking with base classifiers only (no internal SMOTE)
    stack_list = []
    for k, p in best_estimators.items():
        clf = p.named_steps["clf"]
        stack_list.append((k, clf))
    meta = LogisticRegression(max_iter=500)
    stacking = StackingClassifier(estimators=stack_list, final_estimator=meta, cv=cv, n_jobs=-1, passthrough=False)
    final_pipe = ImbPipeline([("smote", smote), ("stack", stacking)])

    print("[*] Fitting final stacking pipeline ...")
    final_pipe.fit(X_train_final, y_train)

    # Evaluate
    y_pred = final_pipe.predict(X_test_final)
    y_prob = None
    if hasattr(final_pipe, "predict_proba"):
        try: y_prob = final_pipe.predict_proba(X_test_final)
        except: y_prob = None

    acc = accuracy_score(y_test, y_pred)
    print(f"[+] Test Accuracy: {acc:.4f}")
    roc = None
    try:
        if y_prob is not None:
            roc = roc_auc_score(y_test, y_prob, multi_class="ovo")
            print(f"[+] ROC AUC (ovo): {roc:.4f}")
    except Exception:
        roc = None

    crep = classification_report(y_test, y_pred, output_dict=True)
    print("[*] Classification report (sample):")
    print(classification_report(y_test, y_pred))

    # Save artifacts
    artifacts = {
        "feature_columns": list(X_train_final.columns),
        "numeric_cols": numeric_cols, "categorical_cols": cat_cols,
        "text_cols": text_cols if use_text else [],
        "target_classes": list(le_target.classes_)
    }
    save_json(artifacts, out/"training_artifacts_info.json")

    joblib.dump({
        "pipeline": final_pipe,
        "preprocessor": preproc,
        "tfidf": tfidf if use_text else None,
        "cat_encoders": cat_encoders,
        "target_encoder": le_target,
        "feature_columns": list(X_train_final.columns)
    }, out/"final_pipeline.joblib")

    metrics = {"accuracy": acc, "roc_auc": roc, "classification_report": crep}
    save_json(metrics, out/"metrics.json")

    cm = confusion_matrix(y_test, y_pred)
    plot_confusion(cm, labels=list(le_target.classes_), path=out/"confusion_matrix.png")

    print("[+] Saved artifacts to:", out.resolve())
    print("[*] Done. Use final_pipeline.joblib for inference (joblib.load and pipeline.predict)")

if __name__ == "__main__":
    main()