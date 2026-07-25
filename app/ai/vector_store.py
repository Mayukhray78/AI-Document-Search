import logging
import os

from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    FilterSelector,
    MatchValue,
    PointStruct,
    VectorParams,
)
from upstash_vector import Index


load_dotenv()

logger = logging.getLogger(__name__)

COLLECTION_NAME = "documents"
EMBEDDING_SIZE = 384

VECTOR_STORE_PROVIDER = os.getenv(
    "VECTOR_STORE_PROVIDER",
    "qdrant",
).lower()

QDRANT_URL = os.getenv(
    "QDRANT_URL",
    "http://localhost:6333",
)

UPSTASH_VECTOR_REST_URL = os.getenv(
    "UPSTASH_VECTOR_REST_URL"
)

UPSTASH_VECTOR_REST_TOKEN = os.getenv(
    "UPSTASH_VECTOR_REST_TOKEN"
)


class VectorStore:

    def __init__(self):
        if VECTOR_STORE_PROVIDER == "upstash":
            self._initialize_upstash()
        elif VECTOR_STORE_PROVIDER == "qdrant":
            self._initialize_qdrant()
        else:
            raise ValueError(
                "VECTOR_STORE_PROVIDER must be "
                "'qdrant' or 'upstash'"
            )

    def _initialize_upstash(self) -> None:
        if not UPSTASH_VECTOR_REST_URL:
            raise RuntimeError(
                "UPSTASH_VECTOR_REST_URL is not configured"
            )

        if not UPSTASH_VECTOR_REST_TOKEN:
            raise RuntimeError(
                "UPSTASH_VECTOR_REST_TOKEN is not configured"
            )

        self.client = Index(
            url=UPSTASH_VECTOR_REST_URL,
            token=UPSTASH_VECTOR_REST_TOKEN,
        )

        logger.info(
            "Upstash Vector client initialized"
        )

    def _initialize_qdrant(self) -> None:
        self.client = QdrantClient(
            url=QDRANT_URL,
        )

        collections = (
            self.client
            .get_collections()
            .collections
        )

        existing_collections = [
            collection.name
            for collection in collections
        ]

        if COLLECTION_NAME not in existing_collections:
            self.client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=EMBEDDING_SIZE,
                    distance=Distance.COSINE,
                ),
            )

            logger.info(
                "Created Qdrant collection: "
                "collection=%s vector_size=%s",
                COLLECTION_NAME,
                EMBEDDING_SIZE,
            )

    def store_embeddings(
        self,
        chunks: list[str],
        embeddings,
        document_id: int,
        user_id: int,
    ) -> None:
        if VECTOR_STORE_PROVIDER == "upstash":
            self._store_in_upstash(
                chunks=chunks,
                embeddings=embeddings,
                document_id=document_id,
                user_id=user_id,
            )
        else:
            self._store_in_qdrant(
                chunks=chunks,
                embeddings=embeddings,
                document_id=document_id,
                user_id=user_id,
            )

    def _store_in_upstash(
        self,
        chunks: list[str],
        embeddings,
        document_id: int,
        user_id: int,
    ) -> None:
        vectors = []

        for index, (chunk, embedding) in enumerate(
            zip(chunks, embeddings)
        ):
            vectors.append(
                {
                    "id": f"{document_id}-{index}",
                    "vector": embedding.tolist(),
                    "metadata": {
                        "document_id": document_id,
                        "user_id": user_id,
                        "chunk_index": index,
                        "text": chunk,
                    },
                }
            )

        if not vectors:
            logger.warning(
                "No embeddings supplied: "
                "document_id=%s user_id=%s",
                document_id,
                user_id,
            )
            return

        self.client.upsert(
            vectors=vectors
        )

        logger.info(
            "Stored Upstash embeddings: "
            "document_id=%s user_id=%s chunks=%s",
            document_id,
            user_id,
            len(vectors),
        )

    def _store_in_qdrant(
        self,
        chunks: list[str],
        embeddings,
        document_id: int,
        user_id: int,
    ) -> None:
        points = []

        for index, (chunk, embedding) in enumerate(
            zip(chunks, embeddings)
        ):
            points.append(
                PointStruct(
                    id=(document_id * 100000) + index,
                    vector=embedding.tolist(),
                    payload={
                        "document_id": document_id,
                        "user_id": user_id,
                        "chunk_index": index,
                        "text": chunk,
                    },
                )
            )

        if not points:
            logger.warning(
                "No embeddings supplied: "
                "document_id=%s user_id=%s",
                document_id,
                user_id,
            )
            return

        self.client.upsert(
            collection_name=COLLECTION_NAME,
            points=points,
            wait=True,
        )

        logger.info(
            "Stored Qdrant embeddings: "
            "document_id=%s user_id=%s chunks=%s",
            document_id,
            user_id,
            len(points),
        )

    def search(
        self,
        query_vector,
        user_id: int,
        top_k: int = 5,
    ) -> list[str]:
        vector = (
            query_vector.tolist()
            if hasattr(query_vector, "tolist")
            else query_vector
        )

        if VECTOR_STORE_PROVIDER == "upstash":
            results = self.client.query(
                vector=vector,
                top_k=top_k,
                include_vectors=False,
                include_metadata=True,
                filter=f"user_id = {user_id}",
            )

            return [
                result.metadata["text"]
                for result in results
                if result.metadata
                and "text" in result.metadata
            ]

        user_filter = Filter(
            must=[
                FieldCondition(
                    key="user_id",
                    match=MatchValue(
                        value=user_id
                    ),
                )
            ]
        )

        response = self.client.query_points(
            collection_name=COLLECTION_NAME,
            query=vector,
            query_filter=user_filter,
            limit=top_k,
            with_payload=True,
        )

        return [
            point.payload["text"]
            for point in response.points
            if point.payload
            and "text" in point.payload
        ]

    def delete_document(
        self,
        document_id: int,
        user_id: int,
    ) -> None:
        if VECTOR_STORE_PROVIDER == "upstash":
            self.client.delete(
                filter=(
                    f"document_id = {document_id} "
                    f"AND user_id = {user_id}"
                )
            )
        else:
            document_filter = Filter(
                must=[
                    FieldCondition(
                        key="document_id",
                        match=MatchValue(
                            value=document_id
                        ),
                    ),
                    FieldCondition(
                        key="user_id",
                        match=MatchValue(
                            value=user_id
                        ),
                    ),
                ]
            )

            self.client.delete(
                collection_name=COLLECTION_NAME,
                points_selector=FilterSelector(
                    filter=document_filter
                ),
                wait=True,
            )

        logger.info(
            "Deleted document embeddings: "
            "provider=%s document_id=%s user_id=%s",
            VECTOR_STORE_PROVIDER,
            document_id,
            user_id,
        )