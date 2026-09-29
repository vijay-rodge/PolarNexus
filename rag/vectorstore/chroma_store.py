import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np
from config.settings import settings
from rag.embeddings.provider import EmbeddingProvider

class PolarVectorStore:
    _client = None
    _collection = None

    @classmethod
    def get_collection(cls):
        if cls._collection is None:
            try:
                import chromadb
                persist_path = Path(settings.CHROMA_PERSIST_DIRECTORY)
                persist_path.mkdir(parents=True, exist_ok=True)
                cls._client = chromadb.PersistentClient(path=str(persist_path))
                cls._collection = cls._client.get_or_create_collection(
                    name=settings.CHROMA_COLLECTION_NAME,
                    metadata={"description": "NCPOR & NPDC Polar Science Knowledge Base"}
                )
            except Exception as e:
                print(f"Warning: ChromaDB initialization fallback ({e}). Using file-backed vector index.")
                cls._collection = "fallback"
        return cls._collection

    @classmethod
    def index_chunks(cls, chunks: List[Dict[str, Any]]) -> int:
        if not chunks:
            return 0
        collection = cls.get_collection()
        texts = [c["content"] for c in chunks]
        embeddings = EmbeddingProvider.embed_documents(texts)
        ids = [c["chunk_id"] for c in chunks]
        metadatas = [
            {
                "chunk_id": c["chunk_id"],
                "document_id": c["document_id"],
                "source_name": c["source_name"],
                "source_url": c["source_url"],
                "page": int(c.get("page", 1)),
                "section": c.get("section", "General"),
                "expedition": c.get("expedition", "General"),
                "station": c.get("station", "All"),
                "research_area": c.get("research_area", "Polar Science")
            }
            for c in chunks
        ]

        if collection != "fallback":
            try:
                collection.upsert(
                    ids=ids,
                    embeddings=embeddings,
                    documents=texts,
                    metadatas=metadatas
                )
                return len(ids)
            except Exception as e:
                print(f"Error upserting to ChromaDB: {e}")

        fallback_file = Path(settings.VECTORSTORE_DIR) / "fallback_index.json"
        existing = []
        if fallback_file.exists():
            try:
                with open(fallback_file, "r", encoding="utf-8") as f:
                    existing = json.load(f)
            except Exception:
                existing = []
        existing_ids = {e["chunk_id"] for e in existing}
        for chunk, emb, meta in zip(chunks, embeddings, metadatas):
            if chunk["chunk_id"] not in existing_ids:
                existing.append({
                    "chunk_id": chunk["chunk_id"],
                    "content": chunk["content"],
                    "embedding": emb,
                    "metadata": meta
                })
        with open(fallback_file, "w", encoding="utf-8") as f:
            json.dump(existing, f)
        return len(chunks)

    @classmethod
    def similarity_search(
        cls, 
        query: str, 
        top_k: int = 4, 
        station_filter: Optional[str] = None,
        expedition_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        query_emb = EmbeddingProvider.embed_query(query)
        collection = cls.get_collection()

        where_clause = {}
        if station_filter and station_filter != "All":
            where_clause["station"] = station_filter
        if expedition_filter and expedition_filter != "General":
            where_clause["expedition"] = expedition_filter

        if collection != "fallback":
            try:
                kwargs = {
                    "query_embeddings": [query_emb],
                    "n_results": top_k
                }
                if where_clause:
                    kwargs["where"] = where_clause

                results = collection.query(**kwargs)
                docs = []
                if results and "documents" in results and results["documents"]:
                    doc_list = results["documents"][0]
                    meta_list = results["metadatas"][0] if "metadatas" in results else [{}] * len(doc_list)
                    distances = results["distances"][0] if "distances" in results else [0.0] * len(doc_list)

                    for content, meta, dist in zip(doc_list, meta_list, distances):
                        score = round(max(0.0, 1.0 - (dist / 2.0)), 3)
                        docs.append({
                            "content": content,
                            "metadata": meta,
                            "relevance_score": score
                        })
                return docs
            except Exception as e:
                print(f"ChromaDB search query failed: {e}")

        fallback_file = Path(settings.VECTORSTORE_DIR) / "fallback_index.json"
        if not fallback_file.exists():
            return []
        try:
            with open(fallback_file, "r", encoding="utf-8") as f:
                records = json.load(f)
        except Exception:
            return []

        scored = []
        q_vec = np.array(query_emb)
        for r in records:
            meta = r.get("metadata", {})
            if station_filter and station_filter != "All" and meta.get("station") != station_filter:
                continue
            r_vec = np.array(r["embedding"])
            norm_prod = (np.linalg.norm(q_vec) * np.linalg.norm(r_vec))
            sim = float(np.dot(q_vec, r_vec) / norm_prod) if norm_prod > 0 else 0.0
            scored.append({
                "content": r["content"],
                "metadata": meta,
                "relevance_score": round(sim, 3)
            })
        scored.sort(key=lambda x: x["relevance_score"], reverse=True)
        return scored[:top_k]
