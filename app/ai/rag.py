from qdrant_client.models import (
    FieldCondition,
    Filter,
    MatchValue,
)

from app.ai.embeddings import EmbeddingModel
from app.ai.llm import LLMService
from app.ai.vector_store import VectorStore


embedding_model = EmbeddingModel()
vector_store = VectorStore()
llm = LLMService()


class RAGService:

    def retrieve(
        self,
        question: str,
        user_id: int,
        top_k: int = 5,
    ) -> list[str]:

        query_vector = embedding_model.generate_embeddings(
            [question]
        )[0]

        user_filter = Filter(
            must=[
                FieldCondition(
                    key="user_id",
                    match=MatchValue(value=user_id),
                )
            ]
        )

        response = vector_store.client.query_points(
            collection_name="documents",
            query=query_vector.tolist(),
            query_filter=user_filter,
            limit=top_k,
            with_payload=True,
        )

        chunks = []

        for point in response.points:
            if point.payload and "text" in point.payload:
                chunks.append(point.payload["text"])

        return chunks

    def answer(
        self,
        question: str,
        user_id: int,
    ) -> dict:

        chunks = self.retrieve(
            question=question,
            user_id=user_id,
        )

        answer = llm.generate_answer(
            question=question,
            context=chunks,
        )

        return {
            "question": question,
            "answer": answer,
            "retrieved_chunks": chunks,
        }