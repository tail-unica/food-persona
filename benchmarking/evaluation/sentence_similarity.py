import pandas as pd
import torch
from sentence_transformers import SentenceTransformer, util


def calculate_avg_semantic_similarity(
    model: SentenceTransformer, series_a: pd.Series, series_b: pd.Series
):
    if series_a.empty or series_b.empty:
        return float("nan"), 0

    try:
        # converte le serie in liste di stringhe
        texts_a = series_a.astype(str).tolist()
        texts_b = series_b.astype(str).tolist()

        # codifica le frasi in vettori (embeddings) usando il modello
        embeddings_a = model.encode(texts_a, convert_to_tensor=True)
        embeddings_b = model.encode(texts_b, convert_to_tensor=True)

        # calcola la similarità coseno tra le coppie di embeddings
        # util.cos_sim è una funzione ottimizzata di PyTorch
        cosine_scores = util.cos_sim(embeddings_a, embeddings_b)

        # estrae solo la diagonale (le coppie corrispondenti A[i] vs B[i])
        paired_scores = torch.diag(cosine_scores)

        # return the mean and count
        mean_similarity = torch.mean(paired_scores).item()

        return mean_similarity, len(paired_scores)

    except Exception as e:
        print(f"Error during Semantic Similarity calculation: {e}")
        return float("nan"), 0
