import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils.preprocess import clean_text

def load_articles(path="data/articles.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def search_related_articles(query, top_k=3, path="data/articles.json"):
    articles = load_articles(path)
    corpus = [clean_text(article["title"] + " " + article["content"]) for article in articles]
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(corpus)
    query_vec = vectorizer.transform([clean_text(query)])
    similarities = cosine_similarity(query_vec, tfidf_matrix).flatten()

    ranked_indices = similarities.argsort()[::-1][:top_k]
    results = []
    for idx in ranked_indices:
        results.append({
            "title": articles[idx]["title"],
            "department": articles[idx]["department"],
            "url": articles[idx].get("url", ""),
            "score": float(similarities[idx])
        })
    return results