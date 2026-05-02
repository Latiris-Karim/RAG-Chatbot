import asyncio
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

COLLECTION_NAME = "rag_documents"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
CHROMA_PATH = "./chroma_db"


class VectorDB:
    def __init__(self):
        ef = SentenceTransformerEmbeddingFunction(model_name=MODEL_NAME)
        client = chromadb.PersistentClient(path=CHROMA_PATH)
        self.collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=ef,
            metadata={"hnsw:space": "cosine"},
        )

    def ingest(self, chunks: list[tuple[str, str]]) -> None:
        ids = [str(i) for i in range(len(chunks))]
        documents = [f"{filename}: {text}" for text, filename in chunks]
        metadatas = [{"source": filename, "anchor": text[:100]} for text, filename in chunks]
        self.collection.upsert(documents=documents, metadatas=metadatas, ids=ids)

    async def query(self, text: str, n_results: int = 20) -> list[str]:
        results = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self.collection.query(query_texts=[text], n_results=n_results),
        )
        return results["documents"][0]
