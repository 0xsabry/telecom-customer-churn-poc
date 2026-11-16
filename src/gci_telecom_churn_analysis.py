from pathlib import Path
import json
import math

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont


BASE = Path(__file__).resolve().parent.parent
OUT = BASE / "data_outputs"
CHARTS = BASE / "charts"
OUT.mkdir(parents=True, exist_ok=True)
CHARTS.mkdir(parents=True, exist_ok=True)


COLORS = {
    "teal": "#0F766E",
    "slate": "#334155",
    "light": "#E2E8F0",
    "red": "#DC2626",
    "amber": "#D97706",
    "blue": "#2563EB",
    "ink": "#111827",
    "muted": "#64748B",
    "bg": "#F8FAFC",
}


def font(size, bold=False):
    names = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibrib.ttf" if bold else "C:/Windows/Fonts/calibri.ttf",
    ]
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            pass
    return ImageFont.load_default()


def draw_bar_chart(path, title, labels, values, ylabel="", colors=None, percent=True, baseline=None):
    w, h = 1200, 680
    im = Image.new("RGB", (w, h), "white")
    d = ImageDraw.Draw(im)
    d.text((70, 36), title, fill=COLORS["ink"], font=font(34, True))
    left, top, right, bottom = 115, 145, 1110, 560
    d.line((left, bottom, right, bottom), fill="#CBD5E1", width=2)
    d.line((left, top, left, bottom), fill="#CBD5E1", width=2)
    maxv = max(values + ([baseline] if baseline else [])) * 1.2
    if maxv == 0:
        maxv = 1
    n = len(values)
    gap = 24
    bw = (right - left - gap * (n + 1)) / n
    colors = colors or [COLORS["teal"]] * n
    for i, (lab, val) in enumerate(zip(labels, values)):
        x0 = left + gap + i * (bw + gap)
        x1 = x0 + bw
        y0 = bottom - (val / maxv) * (bottom - top)
        d.rounded_rectangle((x0, y0, x1, bottom), radius=8, fill=colors[i])
        txt = f"{val:.1%}" if percent else f"{val:,.1f}"
        tw = d.textbbox((0, 0), txt, font=font(22, True))[2]
        d.text((x0 + bw / 2 - tw / 2, y0 - 34), txt, fill=COLORS["ink"], font=font(22, True))
        lab_lines = str(lab).split("\\n")
        for j, line in enumerate(lab_lines):
            tw = d.textbbox((0, 0), line, font=font(18))[2]
            d.text((x0 + bw / 2 - tw / 2, bottom + 18 + j * 22), line, fill=COLORS["slate"], font=font(18))
    if baseline is not None:
        yb = bottom - (baseline / maxv) * (bottom - top)
        d.line((left, yb, right, yb), fill=COLORS["ink"], width=3)
        d.text((right - 210, yb - 30), f"Avg {baseline:.1%}", fill=COLORS["ink"], font=font(20, True))
    if ylabel:
        d.text((32, top - 6), ylabel, fill=COLORS["muted"], font=font(18))
    im.save(path)


def draw_line_chart(path, title, labels, values, ylabel="", percent=True):
    w, h = 1200, 680
    im = Image.new("RGB", (w, h), "white")
    d = ImageDraw.Draw(im)
    d.text((70, 36), title, fill=COLORS["ink"], font=font(34, True))
    left, top, right, bottom = 120, 145, 1110, 560
    d.line((left, bottom, right, bottom), fill="#CBD5E1", width=2)
    d.line((left, top, left, bottom), fill="#CBD5E1", width=2)
    maxv = max(values) * 1.18
    minv = min(values) * 0.94
    if maxv == minv:
        maxv += 1
    pts = []
    for i, val in enumerate(values):
        x = left + i * (right - left) / (len(values) - 1)
        y = bottom - (val - minv) / (maxv - minv) * (bottom - top)
        pts.append((x, y))
    d.line(pts, fill=COLORS["red"], width=7, joint="curve")
    for (x, y), lab, val in zip(pts, labels, values):
        d.ellipse((x - 9, y - 9, x + 9, y + 9), fill=COLORS["red"])
        txt = f"{val:.1%}" if percent else f"{val:,.1f}"
        tw = d.textbbox((0, 0), txt, font=font(20, True))[2]
        d.text((x - tw / 2, y - 42), txt, fill=COLORS["ink"], font=font(20, True))
        tw = d.textbbox((0, 0), str(lab), font=font(18))[2]
        d.text((x - tw / 2, bottom + 18), str(lab), fill=COLORS["slate"], font=font(18))
    if ylabel:
        d.text((32, top - 6), ylabel, fill=COLORS["muted"], font=font(18))
    im.save(path)


def _binary_score_inputs(y, scores):
    y = np.asarray(y)
    scores = np.asarray(scores, dtype=float)
    if y.ndim != 1 or scores.ndim != 1:
        raise ValueError("y and scores must be one-dimensional")
    if len(y) != len(scores) or len(y) == 0:
        raise ValueError("y and scores must have the same non-zero length")
    if not np.isin(y, (0, 1)).all():
        raise ValueError("y must contain only binary labels 0 and 1")
    if not np.isfinite(scores).all():
        raise ValueError("scores must contain only finite values")
    if not np.any(y == 1) or not np.any(y == 0):
        raise ValueError("y must contain at least one sample from each class")
    return y, scores


def auc_score(y, scores):
    """Return binary ROC-AUC, assigning tied scores their average rank."""
    y, scores = _binary_score_inputs(y, scores)
    order = np.argsort(scores, kind="mergesort")
    sorted_scores = scores[order]
    ranks = np.empty(len(scores), dtype=float)

    start = 0
    while start < len(scores):
        end = start + 1
        while end < len(scores) and sorted_scores[end] == sorted_scores[start]:
            end += 1
        # The sorted slice occupies one-based ranks start+1 through end.
        ranks[order[start:end]] = (start + 1 + end) / 2
        start = end

    n_pos = int(np.sum(y == 1))
    n_neg = len(y) - n_pos
    return float(
        (ranks[y == 1].sum() - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg)
    )


def average_precision(y, scores):
    """Return binary average precision, evaluating precision at score thresholds."""
    y, scores = _binary_score_inputs(y, scores)
    order = np.argsort(-scores, kind="mergesort")
    sorted_scores = scores[order]
    y_sorted = y[order]
    cumulative_true_positives = np.cumsum(y_sorted == 1)

    # Include only the last item at each distinct score threshold, so tied
    # examples are considered together rather than in arbitrary array order.
    threshold_ends = np.r_[
        np.flatnonzero(sorted_scores[:-1] != sorted_scores[1:]), len(scores) - 1
    ]
    true_positives = cumulative_true_positives[threshold_ends]
    predicted_positives = threshold_ends + 1
    precision = true_positives / predicted_positives
    recall = true_positives / np.sum(y == 1)
    recall_increments = np.diff(np.r_[0.0, recall])
    return float(np.sum(recall_increments * precision))


def prepare_features(train_df, test_df, target):
    xtr = train_df.drop(columns=[target, "Customer_ID"])
    xte = test_df.drop(columns=[target, "Customer_ID"])
    cat_cols = xtr.select_dtypes(include=["object"]).columns.tolist()
    num_cols = [c for c in xtr.columns if c not in cat_cols]
    med = xtr[num_cols].median(numeric_only=True)
    xtr_num = xtr[num_cols].fillna(med).astype(float)
    xte_num = xte[num_cols].fillna(med).astype(float)
    mu = xtr_num.mean()
    sig = xtr_num.std().replace(0, 1)
    xtr_num = (xtr_num - mu) / sig
    xte_num = (xte_num - mu) / sig

    train_parts = [xtr_num.reset_index(drop=True)]
    test_parts = [xte_num.reset_index(drop=True)]
    dummy_feature_names = list(num_cols)
    for col in cat_cols:
        top_values = xtr[col].fillna("__MISSING__").value_counts().head(25).index.tolist()
        for val in top_values:
            name = f"{col}={val}"
            train_parts.append((xtr[col].fillna("__MISSING__").astype(str).eq(str(val))).astype(float).reset_index(drop=True).to_frame(name))
            test_parts.append((xte[col].fillna("__MISSING__").astype(str).eq(str(val))).astype(float).reset_index(drop=True).to_frame(name))
            dummy_feature_names.append(name)
    X_train = pd.concat(train_parts, axis=1).to_numpy(dtype=float)
    X_test = pd.concat(test_parts, axis=1).to_numpy(dtype=float)
    return X_train, X_test, dummy_feature_names


def fit_logistic(X, y, lr=0.08, reg=0.015, epochs=450):
    y = y.astype(float)
    Xb = np.c_[np.ones(X.shape[0]), X]
    w = np.zeros(Xb.shape[1])
    pos_weight = (len(y) - y.sum()) / max(1, y.sum())
    weights = np.where(y == 1, pos_weight, 1.0)
    weights = weights / weights.mean()
    for _ in range(epochs):
        z = np.clip(Xb @ w, -35, 35)
        p = 1 / (1 + np.exp(-z))
        grad = (Xb.T @ ((p - y) * weights)) / len(y)
        grad[1:] += reg * w[1:]
        w -= lr * grad
    return w


def predict_logistic(X, w):
    Xb = np.c_[np.ones(X.shape[0]), X]
    z = np.clip(Xb @ w, -35, 35)
    return 1 / (1 + np.exp(-z))


def main():
    client = pd.read_csv(BASE / "Client.csv")
    record = pd.read_csv(BASE / "Record.csv")
    df = record.merge(client, on="Customer_ID", how="inner")
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)

    train_mask = np.random.default_rng(42).random(len(df)) < 0.75
    train_df = df.loc[train_mask].copy()
    test_df = df.loc[~train_mask].copy()
    X_train, X_test, feature_names = prepare_features(train_df, test_df, "churn")
    y_train = train_df["churn"].to_numpy(dtype=int)
    y_test = test_df["churn"].to_numpy(dtype=int)
    w = fit_logistic(X_train, y_train)
    prob = predict_logistic(X_test, w)
    pred = (prob >= 0.5).astype(int)

    precision = float(((pred == 1) & (y_test == 1)).sum() / max(1, (pred == 1).sum()))
    recall = float(((pred == 1) & (y_test == 1)).sum() / max(1, (y_test == 1).sum()))
    accuracy = float((pred == y_test).mean())
    f1 = float(2 * precision * recall / max(1e-12, precision + recall))
    metrics = {
        "model_name": "L2-regularized Logistic Regression",
        "evaluation_metric": "ROC-AUC on 25% holdout test set",
        "roc_auc": auc_score(y_test, prob),
        "pr_auc": average_precision(y_test, prob),
        "accuracy_at_0_5_threshold": accuracy,
        "precision_at_0_5_threshold": precision,
        "recall_at_0_5_threshold": recall,
        "f1_at_0_5_threshold": f1,
        "test_rows": int(len(y_test)),
    }

    score_df = pd.DataFrame({
        "actual_churn": y_test,
        "predicted_churn_risk": prob,
        "rev_Mean": test_df["rev_Mean"].to_numpy(),
    }).sort_values("predicted_churn_risk", ascending=False).reset_index(drop=True)
    score_df["risk_decile"] = np.floor(np.arange(len(score_df)) / (len(score_df) / 10)).astype(int) + 1
    score_df["risk_decile"] = score_df["risk_decile"].clip(1, 10)
    gains = score_df.groupby("risk_decile").agg(
        customers=("actual_churn", "size"),
        churners=("actual_churn", "sum"),
        churn_rate=("actual_churn", "mean"),
        avg_score=("predicted_churn_risk", "mean"),
        avg_rev=("rev_Mean", "mean"),
    ).reset_index()

    churn_rate = float(df["churn"].mean())
    top20 = score_df.head(int(len(score_df) * 0.2))
    impact = {
        "baseline_churn_rate": churn_rate,
        "top20_churn_rate": float(top20["actual_churn"].mean()),
        "top20_capture_rate": float(top20["actual_churn"].sum() / max(1, score_df["actual_churn"].sum())),
        "top20_lift_vs_average": float(top20["actual_churn"].mean() / churn_rate),
        "top20_avg_monthly_revenue": float(top20["rev_Mean"].mean()),
        "full_base_monthly_revenue_at_risk": float((df["rev_Mean"] * df["churn"]).sum()),
        "full_base_churners": int(df["churn"].sum()),
        "campaign_targets_full_base": int(len(df) * 0.2),
        "assumed_offer_cost_per_target": 10.0,
        "assumed_save_rate": 0.15,
        "assumed_gross_margin": 0.55,
        "assumed_retained_months": 12,
    }
    expected_churners = impact["campaign_targets_full_base"] * impact["top20_churn_rate"]
    expected_saved = expected_churners * impact["assumed_save_rate"]
    gross_saved = expected_saved * impact["top20_avg_monthly_revenue"] * impact["assumed_retained_months"] * impact["assumed_gross_margin"]
    offer_cost = impact["campaign_targets_full_base"] * impact["assumed_offer_cost_per_target"]
    impact.update({
        "expected_churners_in_targets": float(expected_churners),
        "expected_saved_customers": float(expected_saved),
        "estimated_gross_margin_saved": float(gross_saved),
        "estimated_offer_cost": float(offer_cost),
        "estimated_net_margin_impact": float(gross_saved - offer_cost),
        "roi_multiple": float((gross_saved - offer_cost) / offer_cost),
    })

    summary = {
        "rows": int(len(df)),
        "columns": int(df.shape[1]),
        "churn_rate": churn_rate,
        "avg_monthly_revenue": float(df["rev_Mean"].mean()),
        "avg_monthly_revenue_churners": float(df.loc[df.churn.eq(1), "rev_Mean"].mean()),
        "avg_monthly_revenue_retained": float(df.loc[df.churn.eq(0), "rev_Mean"].mean()),
        "median_eqpdays_churners": float(df.loc[df.churn.eq(1), "eqpdays"].median()),
        "median_eqpdays_retained": float(df.loc[df.churn.eq(0), "eqpdays"].median()),
        "mean_drop_blk_churners": float(df.loc[df.churn.eq(1), "drop_blk_Mean"].mean()),
        "mean_drop_blk_retained": float(df.loc[df.churn.eq(0), "drop_blk_Mean"].mean()),
        "mean_custcare_churners": float(df.loc[df.churn.eq(1), "custcare_Mean"].mean()),
        "mean_custcare_retained": float(df.loc[df.churn.eq(0), "custcare_Mean"].mean()),
    }

    df["equipment_age_band"] = pd.cut(df["eqpdays"], [0, 90, 180, 365, 730, 3000], labels=["0-90", "91-180", "181-365", "366-730", "731+"], include_lowest=True)
    equip = df.groupby("equipment_age_band", observed=True).agg(customers=("churn", "size"), churn_rate=("churn", "mean"), avg_rev=("rev_Mean", "mean")).reset_index()
    service_band = pd.qcut(df["drop_blk_Mean"].rank(method="first"), 5, labels=["Very low", "Low", "Mid", "High", "Very high"])
    service = df.assign(service_issue_band=service_band).groupby("service_issue_band", observed=True).agg(customers=("churn", "size"), churn_rate=("churn", "mean"), avg_rev=("rev_Mean", "mean")).reset_index()
    usage_band = pd.qcut(df["mou_Mean"].rank(method="first"), 5, labels=["Very low", "Low", "Mid", "High", "Very high"])
    usage = df.assign(usage_band=usage_band).groupby("usage_band", observed=True).agg(customers=("churn", "size"), churn_rate=("churn", "mean"), avg_rev=("rev_Mean", "mean")).reset_index()
    rev_dec = df.assign(revenue_decile=pd.qcut(df["rev_Mean"].rank(method="first"), 10, labels=False) + 1).groupby("revenue_decile").agg(customers=("churn", "size"), churn_rate=("churn", "mean"), avg_rev=("rev_Mean", "mean")).reset_index()

    coef = pd.DataFrame({"feature": ["intercept"] + feature_names, "coefficient": w})
    coef["abs_coefficient"] = coef["coefficient"].abs()
    coef = coef.sort_values("abs_coefficient", ascending=False)

    draw_bar_chart(CHARTS / "churn_rate.png", "Customer base is nearly split between retained and churned", ["Retained", "Churned"], [1 - churn_rate, churn_rate], "Share of customers", [COLORS["teal"], COLORS["red"]])
    draw_line_chart(CHARTS / "equipment_age_churn.png", "Older equipment is a visible retention pressure point", equip["equipment_age_band"].astype(str).tolist(), equip["churn_rate"].tolist(), "Churn rate")
    draw_bar_chart(CHARTS / "service_issue_churn.png", "Dropped/blocked calls are confounded by usage volume", service["service_issue_band"].astype(str).tolist(), service["churn_rate"].tolist(), "Churn rate", [COLORS["red"], COLORS["slate"], COLORS["slate"], COLORS["teal"], COLORS["teal"]])
    draw_bar_chart(CHARTS / "usage_churn.png", "Lower current usage is an early churn warning signal", usage["usage_band"].astype(str).tolist(), usage["churn_rate"].tolist(), "Churn rate", [COLORS["red"], COLORS["red"], COLORS["slate"], COLORS["teal"], COLORS["teal"]])
    draw_bar_chart(CHARTS / "model_gain_deciles.png", "Model concentrates churn risk in the top deciles", gains["risk_decile"].astype(str).tolist(), gains["churn_rate"].tolist(), "Actual churn rate", [COLORS["red"] if i <= 2 else "#94A3B8" for i in gains["risk_decile"]], baseline=churn_rate)
    top_coef = coef[coef["feature"] != "intercept"].head(10).copy()
    draw_bar_chart(CHARTS / "feature_importance.png", "Top logistic model drivers by absolute coefficient", [f[:18] for f in top_coef["feature"].tolist()], top_coef["abs_coefficient"].tolist(), "Coefficient", [COLORS["blue"]] * len(top_coef), percent=False)

    summary_payload = {"summary": summary, "metrics": metrics, "impact": impact}
    with open(OUT / "analysis_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary_payload, f, indent=2)
    gains.to_csv(OUT / "model_gain_deciles.csv", index=False)
    equip.to_csv(OUT / "equipment_age_churn.csv", index=False)
    service.to_csv(OUT / "service_issue_churn.csv", index=False)
    usage.to_csv(OUT / "usage_churn.csv", index=False)
    rev_dec.to_csv(OUT / "revenue_decile_churn.csv", index=False)
    coef.to_csv(OUT / "logistic_coefficients.csv", index=False)
    score_df.head(5000).to_csv(OUT / "sample_scored_customers.csv", index=False)
    print(json.dumps(summary_payload, indent=2))


if __name__ == "__main__":
    main()
