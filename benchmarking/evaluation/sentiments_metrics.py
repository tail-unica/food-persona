# Funzione per calcolare il sentiment score normalizzato (-1 a 1)
def calculate_sentiment(texts, sentiment_pipeline, batch_size=32):
    scores = []

    # Convertiamo solo in stringa per evitare errori se ci sono NaN o numeri.
    cleaned_texts = [str(t) for t in texts]

    try:
        # truncation=True è OBBLIGATORIO per i modelli BERT.
        results = sentiment_pipeline(
            cleaned_texts, batch_size=batch_size, truncation=True, max_length=512
        )

        for res in results:
            score = res["score"]
            label = res["label"]

            # Mappa POSITIVE -> +score, NEGATIVE -> -score
            # Note: some models use "LABEL_0"/"LABEL_1" instead of NEGATIVE/POSITIVE.
            # This check handles both standard cases.
            if label == "NEGATIVE" or label == "LABEL_0":
                final_score = -score
            else:
                final_score = score
            scores.append(final_score)

    except Exception as e:
        print(f"Error in sentiment calculation: {e}")
        # In case of error on a batch, return 0 (neutral) for that batch
        return [0.0] * len(texts)

    return scores
