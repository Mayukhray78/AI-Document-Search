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


COLLECTION_NAME = "documents"
EMBEDDING_SIZE = 384


class VectorStore:

    def __init__(self):

        self.client = QdrantClient(
            host="localhost",
            port=6333,
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

    def store_embeddings(
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
            return

        self.client.upsert(
            collection_name=COLLECTION_NAME,
            points=points,
            wait=True,
        )

        print(
            f"Stored {len(points)} chunks "
            f"for document {document_id}."
        )

    def delete_document(
        self,
        document_id: int,
        user_id: int,
    ) -> None:

        document_filter = Filter(
            must=[
                FieldCondition(
                    key="document_id",
                    match=MatchValue(value=document_id),
                ),
                FieldCondition(
                    key="user_id",
                    match=MatchValue(value=user_id),
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

        print(
            f"Deleted Qdrant vectors for "
            f"document {document_id}."
        )