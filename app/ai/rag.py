from app.ai.embeddings import EmbeddingModel
from app.ai.llm import LLMService
from app.ai.vector_store import VectorStore


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

    def retrieve(
        self,
        question: str,
        user_id: int,
        top_k: int = 5,
    ) -> list[str]:
        query_vector = (
            self.embedding_model
            .generate_embeddings([question])[0]
        )

        return self.vector_store.search(
            query_vector=query_vector,
            user_id=user_id,
            top_k=top_k,
        )

    def answer(
        self,
        question: str,
        user_id: int,
    ) -> dict:
        chunks = self.retrieve(
            question=question,
            user_id=user_id,
        )

        if not chunks:
            return {
                "question": question,
                "answer": (
                    "I could not find relevant information "
                    "in the uploaded documents."
                ),
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