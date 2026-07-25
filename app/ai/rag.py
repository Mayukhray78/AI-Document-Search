from app.ai.embeddings import EmbeddingModel
from app.ai.vector_store import VectorStore
from app.ai.llm import LLMService


class RAGService:

    def __init__(self):
        self._embedding_model = None
        self._vector_store = None
        self._llm = None

    @property
    def embedding_model(self):
        if self._embedding_model is None:
            self._embedding_model = EmbeddingModel()

        return self._embedding_model

    @property
    def vector_store(self):
        if self._vector_store is None:
            self._vector_store = VectorStore()

        return self._vector_store

    @property
    def llm(self):
        if self._llm is None:
            self._llm = LLMService()

        return self._llm

    def retrieve(self, question: str, top_k: int = 5) -> list[str]:
        query_vector = self.embedding_model.generate_embeddings(
            [question]
        )[0]

        response = self.vector_store.client.query_points(
            collection_name="documents",
            query=query_vector.tolist(),
            limit=top_k,
            with_payload=True,
        )

        return [
            point.payload["text"]
            for point in response.points
            if point.payload and "text" in point.payload
        ]

    def answer(self, question: str) -> dict:
        chunks = self.retrieve(question)

        if not chunks:
            return {
                "question": question,
                "answer": "I could not find relevant information in the uploaded documents.",
                "retrieved_chunks": [],
            }

        answer = self.llm.generate_answer(
            question=question,
            context=chunks,
        )

        return {
            "question": question,
            "answer": answer,
            "retrieved_chunks": chunks,
        }