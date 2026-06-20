"""
NLP Preprocessing Module
==========================
Text cleaning, tokenization, stopword removal, and lemmatization using NLTK.
Also implements taxonomy-based skill extraction (exact + fuzzy multi-word
matching) and a TF-IDF vectorizer wrapper for downstream similarity scoring.
"""

import re
import string
import ssl

import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

from sklearn.feature_extraction.text import TfidfVectorizer

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from skills_taxonomy import ALL_SKILLS

# Some machines (often due to corporate networks or local cert-store issues) hit
# SSL_CERTIFICATE_VERIFY_FAILED when NLTK tries to download its data. This is a
# narrow, commonly-recommended workaround: skip verification only for this
# one-time language-data download, not for any other network activity.
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# Ensure required NLTK resources are present (no-op if already downloaded)
for resource in ["punkt", "punkt_tab", "stopwords", "wordnet", "omw-1.4"]:
    try:
        nltk.data.find(resource)
    except LookupError:
        try:
            nltk.download(resource, quiet=True)
        except Exception:
            pass

STOPWORDS = set(stopwords.words("english"))
LEMMATIZER = WordNetLemmatizer()

# Build a lowercase lookup of every skill phrase -> canonical taxonomy name.
# Multi-word skills (e.g. "Machine Learning") are matched as phrases, not
# bag-of-words, to avoid false positives like matching "Learning" alone.
_SKILL_LOOKUP = {skill.lower(): skill for skill in ALL_SKILLS}
# Sort longest-first so multi-word skills are matched before their substrings
# (e.g. match "Natural Language Processing" before generic "Processing").
_SKILL_PHRASES_SORTED = sorted(_SKILL_LOOKUP.keys(), key=len, reverse=True)


def clean_text(text):
    """Lowercase, strip punctuation/extra whitespace, normalize separators."""
    text = text.lower()
    text = re.sub(r"[\r\n\t]+", " ", text)
    text = re.sub(r"[^a-z0-9\s\+\#\./-]", " ", text)  # keep tokens like c++, c#, .net
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize_and_lemmatize(text, remove_stopwords=True):
    """Tokenize cleaned text, optionally remove stopwords, then lemmatize."""
    tokens = word_tokenize(text)
    tokens = [t for t in tokens if t not in string.punctuation]
    if remove_stopwords:
        tokens = [t for t in tokens if t not in STOPWORDS]
    lemmas = [LEMMATIZER.lemmatize(t) for t in tokens]
    return lemmas


def extract_skills_from_text(raw_text):
    """
    Taxonomy-based skill extraction via phrase matching on the *original*
    (lightly normalized) text, since skills like 'Machine Learning' or
    'scikit-learn' need exact phrase boundaries rather than token bags.

    Returns a sorted list of canonical skill names found in the text.
    """
    normalized = " " + re.sub(r"\s+", " ", raw_text.lower()) + " "
    # Normalize common separators so 'Scikit-Learn', 'scikit learn' etc. all match
    normalized_loose = normalized.replace("-", " ").replace("/", " ")

    found = set()
    for phrase in _SKILL_PHRASES_SORTED:
        phrase_loose = phrase.replace("-", " ").replace("/", " ")
        pattern = r"(?<![a-z0-9])" + re.escape(phrase_loose) + r"(?![a-z0-9])"
        if re.search(pattern, normalized_loose):
            found.add(_SKILL_LOOKUP[phrase])

    return sorted(found)


def preprocess_corpus(text_list):
    """Apply clean_text + tokenize_and_lemmatize to a list of documents."""
    return [" ".join(tokenize_and_lemmatize(clean_text(t))) for t in text_list]


class SkillAwareTfidfVectorizer:
    """
    Thin wrapper around scikit-learn's TfidfVectorizer that:
    1. Preprocesses text with our cleaning/lemmatization pipeline
    2. Fits on a corpus of documents (resumes + job descriptions combined,
       so candidate and job vectors live in the same vector space)
    """

    def __init__(self, max_features=2000, ngram_range=(1, 2)):
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            ngram_range=ngram_range,
            sublinear_tf=True,
        )
        self._fitted = False

    def fit(self, raw_documents):
        processed = preprocess_corpus(raw_documents)
        self.vectorizer.fit(processed)
        self._fitted = True
        return self

    def transform(self, raw_documents):
        if not self._fitted:
            raise RuntimeError("Vectorizer must be fit before transform.")
        processed = preprocess_corpus(raw_documents)
        return self.vectorizer.transform(processed)

    def fit_transform(self, raw_documents):
        self.fit(raw_documents)
        return self.transform(raw_documents)


if __name__ == "__main__":
    sample = (
        "Experienced Data Scientist skilled in Python, scikit-learn, and Machine "
        "Learning. Strong background in Natural Language Processing and SQL. "
        "Familiar with TensorFlow and AWS deployment pipelines."
    )
    print("Cleaned:", clean_text(sample))
    print("Lemmas:", tokenize_and_lemmatize(clean_text(sample))[:15])
    print("Extracted skills:", extract_skills_from_text(sample))
