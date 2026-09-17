import re
from collections import Counter
from typing import List, Tuple

STOPWORDS = {
    "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your",
    "yours", "yourself", "yourselves", "he", "him", "his", "himself", "she",
    "her", "hers", "herself", "it", "its", "itself", "they", "them", "their",
    "theirs", "themselves", "what", "which", "who", "whom", "this", "that",
    "these", "those", "am", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an",
    "the", "and", "but", "if", "or", "because", "as", "until", "while", "of",
    "at", "by", "for", "with", "about", "against", "between", "into", "through",
    "during", "before", "after", "above", "below", "to", "from", "up", "down",
    "in", "out", "on", "off", "over", "under", "again", "further", "then",
    "once", "here", "there", "when", "where", "why", "how", "all", "any",
    "both", "each", "few", "more", "most", "other", "some", "such", "no",
    "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s",
    "t", "can", "will", "just", "don", "should", "now", "d", "ll", "m", "o",
    "re", "ve", "y", "ain", "aren", "couldn", "didn", "doesn", "hadn", "hasn",
    "haven", "isn", "ma", "mightn", "mustn", "needn", "shan", "shouldn",
    "wasn", "weren", "won", "wouldn", "like", "get", "also", "would", "around"
}

def tokenize_and_clean(texts: List[str]) -> List[str]:
    """Combines texts, converts to lowercase, extracts words and strips common stopwords."""
    combined = " ".join(texts).lower()
    words = re.findall(r"[a-z]+", combined)
    return [w for w in words if w not in STOPWORDS and len(w) > 2]

def count_bigrams(tokens: List[str]) -> Counter:
    """Computes frequencies of two-word sequences (bigrams)."""
    if len(tokens) < 2:
        return Counter()
    bigrams = [f"{tokens[i]} {tokens[i+1]}" for i in range(len(tokens) - 1)]
    return Counter(bigrams)

def extract_key_phrase(text: str) -> str:
    """Extracts a succinct representative snippet from a response string."""
    sentences = re.split(r"[.!?]", text)
    valid_sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
    if valid_sentences:
        first = valid_sentences[0]
        # Keep up to first 12 words
        words = first.split()
        return " ".join(words[:12])
    return text[:60]
