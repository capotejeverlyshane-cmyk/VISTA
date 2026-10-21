import json
import os
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils.preprocess import clean_text

logger = logging.getLogger(__name__)

DEFAULT_ARTICLES_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "articles.json"
)

# In-memory cache: (path, mtime) -> (articles, vectorizer, tfidf_matrix)
_ARTICLES_CACHE = {
    "path": None,
    "mtime": None,
    "articles": [],
    "vectorizer": None,
    "tfidf_matrix": None,
}


def load_articles(path=None):
    if path is None:
        path = DEFAULT_ARTICLES_PATH
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        logger.warning("Failed to load articles from %s: %s", path, exc)
        return []


def _get_article_index(path=None):
    if path is None:
        path = DEFAULT_ARTICLES_PATH

    if not os.path.exists(path):
        return [], None, None

    try:
        current_mtime = os.path.getmtime(path)
    except OSError:
        current_mtime = 0

    if (
        _ARTICLES_CACHE["path"] == path
        and _ARTICLES_CACHE["mtime"] == current_mtime
        and _ARTICLES_CACHE["vectorizer"] is not None
    ):
        return (
            _ARTICLES_CACHE["articles"],
            _ARTICLES_CACHE["vectorizer"],
            _ARTICLES_CACHE["tfidf_matrix"],
        )

    articles = load_articles(path)
    if not articles:
        return [], None, None

    corpus = [
        clean_text(f"{article.get('title', '')} {article.get('content', '')}")
        for article in articles
    ]

    try:
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(corpus)
    except Exception as exc:
        logger.warning("Failed to build TF-IDF index for articles: %s", exc)
        return articles, None, None

    _ARTICLES_CACHE["path"] = path
    _ARTICLES_CACHE["mtime"] = current_mtime
    _ARTICLES_CACHE["articles"] = articles
    _ARTICLES_CACHE["vectorizer"] = vectorizer
    _ARTICLES_CACHE["tfidf_matrix"] = tfidf_matrix

    return articles, vectorizer, tfidf_matrix


def search_related_articles(query, top_k=3, path=None):
    articles, vectorizer, tfidf_matrix = _get_article_index(path)
    if not articles or vectorizer is None or tfidf_matrix is None:
        return []

    cleaned_q = clean_text(query)
    if not cleaned_q.strip():
        return []

    try:
        query_vec = vectorizer.transform([cleaned_q])
        similarities = cosine_similarity(query_vec, tfidf_matrix).flatten()
    except Exception as exc:
        logger.warning("Article similarity calculation failed: %s", exc)
        return []

    ranked_indices = similarities.argsort()[::-1][:top_k]
    results = []
    for idx in ranked_indices:
        results.append(
            {
                "title": articles[idx].get("title", ""),
                "department": articles[idx].get("department", "General"),
                "url": articles[idx].get("url", ""),
                "score": float(similarities[idx]),
            }
        )
    return results