import asyncio
import os
import chromadb
from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
sentence_model = SentenceTransformer(MODEL_NAME)


class ContextualVectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=os.getenv("db_path", "./chroma_db"))
        self.collection = self.client.get_or_create_collection(name="documents")

    def add_chunks(self, chunks: list[tuple[str, str, str]]) -> None:
        # chunk[0] = filename | chunk[1] = contextual summary | chunk[2] = chunk text
        offset = self.collection.count()
        ids = [str(offset + i) for i in range(len(chunks))]
        embeddings = sentence_model.encode([c[0] + c[1] + c[2] for c in chunks]).tolist()
        documents = [c[1] + "\n\n" + c[2] for c in chunks]
        metadatas = [{"file": c[0]} for c in chunks]
        self.collection.add(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)

    async def retrieve(self, text: str, n_results: int = 20) -> list[str]:
        embedding = await asyncio.get_event_loop().run_in_executor(
            None, lambda: sentence_model.encode([text]).tolist()
        )
        results = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self.collection.query(query_embeddings=embedding, n_results=n_results),
        )
        return results["documents"][0]
