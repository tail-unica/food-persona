import re

import numpy as np
from nltk.translate.bleu_score import SmoothingFunction, sentence_bleu


def calculate_avg_bleu(references_list, candidates_list):
    scores = []
    # Smoothing method 1 gestisce bene le frasi brevi o senza n-grammi sovrapposti
    smoothie = SmoothingFunction().method1

    # Imposta i pesi per BLEU-1 (guaeda solo le parole singole)
    weights_setting = (1.0, 0, 0, 0)

    # guarda le parole singole e le coppie di parole
    # weights_setting = (0.5, 0.5, 0, 0)

    for ref, cand in zip(references_list, candidates_list):
        # Converti in stringa e minuscolo
        ref_str = str(ref).lower()
        cand_str = str(cand).lower()

        # Rimuovi punteggiatura (tieni solo lettere e numeri)
        ref_clean = re.sub(r"[^\w\s]", "", ref_str)
        cand_clean = re.sub(r"[^\w\s]", "", cand_str)

        # Tokenizza
        ref_tokens = ref_clean.split()
        cand_tokens = cand_clean.split()

        # Se una delle due è vuota dopo la pulizia, salta
        if not ref_tokens or not cand_tokens:
            scores.append(0.0)
            continue

        # Calcolo BLEU
        score = sentence_bleu(
            [ref_tokens],
            cand_tokens,
            smoothing_function=smoothie,
            weights=weights_setting,
        )
        scores.append(score)

    return np.mean(scores)
