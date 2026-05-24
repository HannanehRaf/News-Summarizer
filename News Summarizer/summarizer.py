import re
from collections import Counter


PERSIAN_STOP_WORDS = {
    "و","در","به","از","که","با","این","است","را","های","تا","آن",
    "کرد","شد","بر","برای","هم","روی","خود","دیگر","بود","می"
}

EN_STOP_WORDS = {
    "the","is","in","at","of","a","and","to","for","on","with",
    "as","by","an","be","this","that","it","are","was","were"
}

STOP_WORDS = PERSIAN_STOP_WORDS.union(EN_STOP_WORDS)


def split_sentences(text: str):
    sentences = re.split(r'[.!?؟]+', text)
    return [s.strip() for s in sentences if s.strip()]


def tokenize(text: str):
    words = re.findall(r'\w+', text.lower())
    return words


def summarize_text(text: str, max_sentences: int = 2):

    sentences = split_sentences(text)

    if len(sentences) <= max_sentences:
        return text

    words = tokenize(text)

    filtered_words = [w for w in words if w not in STOP_WORDS]

    word_freq = Counter(filtered_words)

    sentence_scores = {}

    for i, sentence in enumerate(sentences):

        sentence_words = tokenize(sentence)

        score = 0
        for word in sentence_words:
            if word in word_freq:
                score += word_freq[word]

        sentence_scores[i] = score

    ranked = sorted(sentence_scores, key=sentence_scores.get, reverse=True)

    top_indexes = sorted(ranked[:max_sentences])

    summary_sentences = [sentences[i] for i in top_indexes]

    return " / ".join(summary_sentences)
