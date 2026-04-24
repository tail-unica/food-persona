import pandas as pd

from evaluation.metrics import calculate_metrics
from evaluation.similarity import check_similarity


def evaluate_model_vs_gt(model_data, gt_data, q_type):
    correct = 0
    total = len(gt_data)
    correct_answer_count = 0
    answered_count = 0
    gt_unknown_count = 0
    correct_unknown_count = 0
    model_not_none_count = 0
    score_comparison_list = []
    gt_known_count = 0
    model_unknown_count = 0
    model_and_gt_answered_count = 0

    if total == 0:
        print("Attenzione: Ground Truth vuoto.")
        return 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, {}

    model_map = {}
    for item in model_data:
        user_key = item.get("user_id")
        if user_key is None:
            continue

        key = (user_key, item["questions"].strip().lower())

        if q_type == "FCQ":
            model_map[key] = str(item.get("score", "")).strip().lower()
        else:
            model_map[key] = str(item.get("answer", "")).strip().lower()

    # USER COVERAGE
    # User coverage for answers (checks how many users the model answered questions for compared to my file)
    gt_users = set(item["user_id"] for item in gt_data)
    model_users = set(
        item["user_id"] for item in model_data if item.get("user_id") is not None
    )

    user_coverage_percent = (
        len(gt_users.intersection(model_users)) / len(gt_users) * 100 if gt_users else 0
    )

    for gt_item in gt_data:
        user_key = gt_item.get("user_id")
        gt_question = gt_item["questions"].strip().lower()
        key = (user_key, gt_question)

        # GT value
        gt_val = (
            str(gt_item["score"]).strip().lower()
            if q_type == "FCQ"
            else str(gt_item["answer"]).strip().lower()
        )

        # model value (may be empty)
        model_val = model_map.get(key, "").strip().lower()

        if q_type == "FCQ":
            score_comparison_list.append(
                {
                    "true_str": str(gt_item["score"]).strip(),
                    "pred_str": str(model_val).strip(),
                    "category": gt_item.get("category", "Unknown"),
                }
            )

        is_correct = check_similarity(gt_val, model_val)

        # Accuracy (correct answers / total answers in my file)
        if is_correct:
            correct += 1

        # UNKNOWN IN GT
        if gt_val == "unknown":
            gt_unknown_count += 1
            if model_val == "unknown":
                correct_unknown_count += 1

        if gt_val not in ("unknown", "none", ""):
            gt_known_count += 1

        # MODEL ANSWERED (non-unknown)
        if model_val and model_val not in ("unknown", "none", ""):
            answered_count += 1
            if gt_val not in ("unknown", "none", ""):
                model_and_gt_answered_count += 1
            if is_correct:
                correct_answer_count += 1

        # MODEL NONE / EMPTY
        if model_val not in ("none", ""):
            model_not_none_count += 1

        # MODEL UNKNOWN
        if model_val == "unknown":
            model_unknown_count += 1

    # metrics for FCQ
    mae = mse = rmse = float("nan")
    metrics_scores = 0
    df_result = pd.DataFrame()

    if q_type == "FCQ" and score_comparison_list:
        df = pd.DataFrame(score_comparison_list)
        df["true"] = pd.to_numeric(df["true_str"], errors="coerce")
        df["pred"] = pd.to_numeric(df["pred_str"], errors="coerce")
        df = df.dropna(subset=["true", "pred"])

        if not df.empty:
            mae, mse, rmse, metrics_scores = calculate_metrics(df)

        df_result = df

    unknown_percent = (
        (correct_unknown_count / gt_unknown_count * 100) if gt_unknown_count else 0
    )
    correct_answer_percent = (
        (correct_answer_count / answered_count * 100) if answered_count else 0
    )  # percentage of correct answers among those actually given by the model
    gt_unknown_percent = gt_unknown_count / total * 100
    model_not_none_percent = model_not_none_count / total * 100
    gt_known_percet = gt_known_count / total * 100
    if gt_known_count:
        if q_type == "FCQ":
            metrics_scores_percent = metrics_scores / gt_known_count * 100
        else:
            metrics_scores_percent = model_and_gt_answered_count / gt_known_count * 100
    else:
        metrics_scores_percent = 0
    model_unknown_percent = model_unknown_count / total * 100
    correct_unknown_percent_relative = (
        (correct_unknown_count / model_unknown_count * 100)
        if model_unknown_count
        else 0
    )
    correct_answer_percent_relative_both_answered = (
        (correct_answer_count / model_and_gt_answered_count * 100)
        if model_and_gt_answered_count
        else 0
    )

    return (
        correct,
        total,
        unknown_percent,
        user_coverage_percent,
        correct_answer_percent,
        mse,
        mae,
        rmse,
        gt_unknown_percent,
        model_not_none_percent,
        metrics_scores_percent,  # scores used for metrics calculation, number of matching samples between gt and model (i.e., number and number)
        gt_known_percet,  # percentage of answers in gt that are not unknown or empty
        model_unknown_percent,  # percentage of model answers that are unknown
        correct_unknown_percent_relative,  # percentage of correct unknown answers relative to those given as unknown by the model
        correct_answer_percent_relative_both_answered,  # percentage of correct answers for questions answered by both model and gt
        df_result,
        gt_known_count,
    )
