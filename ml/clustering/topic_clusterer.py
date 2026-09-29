from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

class ResearchTopicClusterer:
    @classmethod
    def cluster_texts(cls, texts: List[str], n_clusters: int = 4) -> Dict[str, Any]:
        if len(texts) < n_clusters:
            return {"error": "Not enough texts to form requested number of clusters"}

        vectorizer = TfidfVectorizer(max_features=200, stop_words='english')
        X = vectorizer.fit_transform(texts)

        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X)

        terms = vectorizer.get_feature_names_out()
        order_centroids = kmeans.cluster_centers_.argsort()[:, ::-1]

        cluster_summary = {}
        for i in range(n_clusters):
            top_words = [terms[ind] for ind in order_centroids[i, :5]]
            assigned_docs = [texts[idx] for idx, lbl in enumerate(labels) if lbl == i]
            cluster_summary[f"Cluster_{i+1}"] = {
                "top_keywords": top_words,
                "document_count": len(assigned_docs),
                "samples": assigned_docs[:2]
            }

        return {
            "n_clusters": n_clusters,
            "clusters": cluster_summary
        }
