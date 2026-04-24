import re
import string


def normalize_text(text):
    text = text.strip().lower()  # lowercase and remove spaces
    text = text.translate(str.maketrans("", "", string.punctuation))

    return text


def clean_text(text):
    if not text:
        return ""

    # remove HTML tags
    text = re.sub(r"<[^>]+>", " ", text)
    # remove non-ASCII characters
    text = re.sub(r"[^\x00-\x7F]+", " ", text)
    # remove extra spaces and newlines
    text = text.replace("\n", " ").replace("\r", " ")
    # replace double quotes with single quotes
    text = text.replace('"', "'")
    # remove multiple spaces
    text = " ".join(text.split())

    return text
