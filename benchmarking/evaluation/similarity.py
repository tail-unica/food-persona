import difflib
import string


def check_similarity(gt_val, m_val, threshold=0.80):
    # Remove punctuation to compare only words
    translator = str.maketrans("", "", string.punctuation)

    s1_raw = str(gt_val).strip().lower()
    s2_raw = str(m_val).strip().lower()

    # Punctuation cleaning for token comparison
    s1 = s1_raw.translate(translator)
    s2 = s2_raw.translate(translator)

    if s1_raw == s2_raw:
        return True

    try:
        if abs(float(s1) - float(s2)) < 0.01:
            return True
    except ValueError:
        pass

    # TOKEN SET (Order independent)
    tokens1 = set(s1.split())
    tokens2 = set(s2.split())

    # Remove useless words
    if tokens1 and tokens1 == tokens2:
        return True

    # If all significant words from GT are present in the model's response
    if len(tokens1) > 0:
        if tokens1.issubset(tokens2):
            return True

    # JACCARD SIMILARITY (Partial overlap)
    # for long sentences that say almost the same thing
    intersection = tokens1.intersection(tokens2)
    union = tokens1.union(tokens2)
    if len(union) > 0:
        jaccard_score = len(intersection) / len(union)
        if jaccard_score >= 0.7:  # If they share 70% of words
            return True

    # FUZZY MATCH (For typos)
    # Remains useful for example for "Diabtes" vs "Diabetes"
    ratio = difflib.SequenceMatcher(None, s1_raw, s2_raw).ratio()
    if ratio >= threshold:
        return True

    return False
