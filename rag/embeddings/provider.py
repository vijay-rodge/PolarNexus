from typing import List, Union
import numpy as np
from config.settings import settings

class EmbeddingProvider:
    _model = None

    @classmethod
    def get_model(cls):
        if cls._model is None:
            provider = settings.EMBEDDING_PROVIDER.lower()
            if provider == "sentence-transformers":
                try:
                    from sentence_transformers import SentenceTransformer
                    cls._model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
                except Exception as e:
                    print(f"Warning: SentenceTransformer load error: {e}. Falling back to deterministic embedding.")
                    cls._model = "fallback"
            else:
                cls._model = "fallback"
        return cls._model

    @classmethod
    def embed_documents(cls, texts: List[str]) -> List[List[float]]:
        model = cls.get_model()
        if model != "fallback":
            try:
                embeddings = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
                return embeddings.tolist()
            except Exception:
                pass
        return [cls._fallback_embed(t) for t in texts]

    @classmethod
    def embed_query(cls, text: str) -> List[float]:
        return cls.embed_documents([text])[0]

    @staticmethod
    def _fallback_embed(text: str, dim: int = 384) -> List[float]:
        np.random.seed(abs(hash(text)) % (2**31 - 1))
        vec = np.random.normal(0, 1, dim)
        norm = np.linalg.norm(vec)
        return (vec / (norm if norm > 0 else 1.0)).tolist()
