import json
import os
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

try:
    import psycopg2
    from psycopg2.extras import Json
except ImportError:  # pragma: no cover
    psycopg2 = None
    Json = None


def _utcnow() -> datetime:
    return datetime.utcnow()


@dataclass
class PersistenceConfig:
    host: str = os.environ.get("MMSS_DB_HOST", "127.0.0.1")
    port: int = int(os.environ.get("MMSS_DB_PORT", "5432"))
    dbname: str = os.environ.get("MMSS_DB_NAME", "mmss-db")
    user: str = os.environ.get("MMSS_DB_USER", "mind_user")
    password: str = os.environ.get("MMSS_DB_PASSWORD", "mindfreak")
    schema: str = os.environ.get("MMSS_DB_SCHEMA", "mmss_app")


class AIPersistence:
    def __init__(self, config: Optional[PersistenceConfig] = None):
        self.config = config or PersistenceConfig()
        self.available = psycopg2 is not None
        self.error: Optional[str] = None
        if self.available:
            try:
                self._init_schema()
            except Exception as exc:  # pragma: no cover
                self.available = False
                self.error = str(exc)

    def record_interaction(
        self,
        session_type: str,
        source_route: str,
        prompt_text: str,
        response_text: str,
        model_name: str,
        provider: str,
        project_name: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
        file_path: Optional[str] = None,
    ) -> None:
        if not self.available:
            return

        metadata = metadata or {}
        prompt_artifact_id = str(uuid.uuid4())
        response_artifact_id = str(uuid.uuid4())
        with self._connect() as conn:
            with conn.cursor() as cur:
                session_id = self._create_session(cur, session_type, source_route, project_name, metadata)
                prompt_message_id = self._insert_message(
                    cur,
                    session_id=session_id,
                    role="user",
                    content=prompt_text,
                    provider=provider,
                    model_name=model_name,
                    metadata=metadata,
                )
                response_message_id = self._insert_message(
                    cur,
                    session_id=session_id,
                    role="assistant",
                    content=response_text,
                    provider=provider,
                    model_name=model_name,
                    metadata=metadata,
                )
                self._insert_artifact(
                    cur,
                    artifact_id=prompt_artifact_id,
                    session_id=session_id,
                    message_id=prompt_message_id,
                    artifact_type="prompt",
                    title=f"{session_type} prompt",
                    content=prompt_text,
                    source_route=source_route,
                    model_name=model_name,
                    provider=provider,
                    file_path=file_path,
                    metadata=metadata,
                )
                self._insert_artifact(
                    cur,
                    artifact_id=response_artifact_id,
                    session_id=session_id,
                    message_id=response_message_id,
                    artifact_type="response",
                    title=f"{session_type} response",
                    content=response_text,
                    source_route=source_route,
                    model_name=model_name,
                    provider=provider,
                    file_path=file_path,
                    metadata=metadata,
                )
                self._insert_document_with_chunks(
                    cur,
                    session_id=session_id,
                    artifact_id=prompt_artifact_id,
                    document_type="prompt",
                    title=f"{session_type} prompt",
                    content=prompt_text,
                    metadata=metadata,
                )
                self._insert_document_with_chunks(
                    cur,
                    session_id=session_id,
                    artifact_id=response_artifact_id,
                    document_type="response",
                    title=f"{session_type} response",
                    content=response_text,
                    metadata=metadata,
                )
            conn.commit()

    def record_artifact(
        self,
        session_type: str,
        source_route: str,
        artifact_type: str,
        title: str,
        content: str,
        content_format: str,
        project_name: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
        file_path: Optional[str] = None,
    ) -> None:
        if not self.available:
            return

        metadata = {**(metadata or {}), "content_format": content_format}
        artifact_id = str(uuid.uuid4())
        with self._connect() as conn:
            with conn.cursor() as cur:
                session_id = self._create_session(cur, session_type, source_route, project_name, metadata)
                self._insert_artifact(
                    cur,
                    artifact_id=artifact_id,
                    session_id=session_id,
                    message_id=None,
                    artifact_type=artifact_type,
                    title=title,
                    content=content,
                    source_route=source_route,
                    model_name=metadata.get("model_name"),
                    provider=metadata.get("provider"),
                    file_path=file_path,
                    metadata=metadata,
                )
                self._insert_document_with_chunks(
                    cur,
                    session_id=session_id,
                    artifact_id=artifact_id,
                    document_type=artifact_type,
                    title=title,
                    content=content,
                    metadata=metadata,
                )
            conn.commit()

    def _connect(self):
        if not psycopg2:
            raise RuntimeError("psycopg2 is not installed.")
        return psycopg2.connect(
            host=self.config.host,
            port=self.config.port,
            dbname=self.config.dbname,
            user=self.config.user,
            password=self.config.password,
        )

    def _init_schema(self) -> None:
        schema = self._schema_name()
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    CREATE EXTENSION IF NOT EXISTS vector;
                    CREATE SCHEMA IF NOT EXISTS {schema};

                    CREATE TABLE IF NOT EXISTS {schema}.ai_sessions (
                        id UUID PRIMARY KEY,
                        session_type TEXT NOT NULL,
                        source_route TEXT NOT NULL,
                        project_name TEXT,
                        metadata JSONB NOT NULL DEFAULT '{{}}'::jsonb,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    );

                    CREATE TABLE IF NOT EXISTS {schema}.ai_messages (
                        id UUID PRIMARY KEY,
                        session_id UUID NOT NULL REFERENCES {schema}.ai_sessions(id) ON DELETE CASCADE,
                        role TEXT NOT NULL,
                        content TEXT NOT NULL,
                        provider TEXT,
                        model_name TEXT,
                        metadata JSONB NOT NULL DEFAULT '{{}}'::jsonb,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    );

                    CREATE TABLE IF NOT EXISTS {schema}.ai_artifacts (
                        id UUID PRIMARY KEY,
                        session_id UUID NOT NULL REFERENCES {schema}.ai_sessions(id) ON DELETE CASCADE,
                        message_id UUID REFERENCES {schema}.ai_messages(id) ON DELETE SET NULL,
                        artifact_type TEXT NOT NULL,
                        title TEXT NOT NULL,
                        content TEXT NOT NULL,
                        source_route TEXT NOT NULL,
                        provider TEXT,
                        model_name TEXT,
                        file_path TEXT,
                        metadata JSONB NOT NULL DEFAULT '{{}}'::jsonb,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    );

                    CREATE TABLE IF NOT EXISTS {schema}.rag_documents (
                        id UUID PRIMARY KEY,
                        session_id UUID REFERENCES {schema}.ai_sessions(id) ON DELETE CASCADE,
                        artifact_id UUID REFERENCES {schema}.ai_artifacts(id) ON DELETE CASCADE,
                        document_type TEXT NOT NULL,
                        title TEXT NOT NULL,
                        content TEXT NOT NULL,
                        metadata JSONB NOT NULL DEFAULT '{{}}'::jsonb,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    );

                    CREATE TABLE IF NOT EXISTS {schema}.rag_chunks (
                        id UUID PRIMARY KEY,
                        document_id UUID NOT NULL REFERENCES {schema}.rag_documents(id) ON DELETE CASCADE,
                        chunk_index INTEGER NOT NULL,
                        chunk_text TEXT NOT NULL,
                        embedding_model TEXT,
                        embedding DOUBLE PRECISION[],
                        embedding_vector vector,
                        metadata JSONB NOT NULL DEFAULT '{{}}'::jsonb,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    );

                    CREATE TABLE IF NOT EXISTS {schema}.vectorization_jobs (
                        id UUID PRIMARY KEY,
                        status TEXT NOT NULL,
                        embedding_model TEXT NOT NULL,
                        total_chunks INTEGER NOT NULL DEFAULT 0,
                        processed_chunks INTEGER NOT NULL DEFAULT 0,
                        error TEXT,
                        metadata JSONB NOT NULL DEFAULT '{{}}'::jsonb,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    );

                    CREATE INDEX IF NOT EXISTS idx_ai_sessions_type ON {schema}.ai_sessions(session_type, created_at DESC);
                    CREATE INDEX IF NOT EXISTS idx_ai_messages_session ON {schema}.ai_messages(session_id, created_at);
                    CREATE INDEX IF NOT EXISTS idx_ai_artifacts_session ON {schema}.ai_artifacts(session_id, created_at);
                    CREATE INDEX IF NOT EXISTS idx_rag_documents_session ON {schema}.rag_documents(session_id, created_at);
                    CREATE INDEX IF NOT EXISTS idx_rag_chunks_document ON {schema}.rag_chunks(document_id, chunk_index);
                    CREATE INDEX IF NOT EXISTS idx_vectorization_jobs_status ON {schema}.vectorization_jobs(status, updated_at DESC);
                    """
                )
                cur.execute(f"ALTER TABLE {schema}.rag_chunks ADD COLUMN IF NOT EXISTS embedding_vector vector;")
            conn.commit()

    def get_vectorization_overview(self, embedding_model: str) -> dict[str, Any]:
        if not self.available:
            return {"total_chunks": 0, "embedded_chunks": 0, "pending_chunks": 0}
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    SELECT
                        COUNT(*) AS total_chunks,
                        COUNT(*) FILTER (WHERE embedding_vector IS NOT NULL AND embedding_model = %s) AS embedded_chunks,
                        COUNT(*) FILTER (WHERE embedding_vector IS NULL) AS pending_chunks
                    FROM {self._schema_name()}.rag_chunks
                    """,
                    (embedding_model,),
                )
                total_chunks, embedded_chunks, pending_chunks = cur.fetchone()
        return {
            "total_chunks": total_chunks or 0,
            "embedded_chunks": embedded_chunks or 0,
            "pending_chunks": pending_chunks or 0,
        }

    def create_vectorization_job(self, embedding_model: str, metadata: Optional[dict[str, Any]] = None) -> str:
        if not self.available:
            raise RuntimeError("PostgreSQL persistence is unavailable.")
        job_id = str(uuid.uuid4())
        overview = self.get_vectorization_overview(embedding_model)
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    INSERT INTO {self._schema_name()}.vectorization_jobs
                    (id, status, embedding_model, total_chunks, processed_chunks, metadata, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        job_id,
                        "pending",
                        embedding_model,
                        overview["pending_chunks"],
                        0,
                        self._json(metadata or {}),
                        _utcnow(),
                        _utcnow(),
                    ),
                )
            conn.commit()
        return job_id

    def get_vectorization_job(self, job_id: str) -> Optional[dict[str, Any]]:
        if not self.available:
            return None
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    SELECT id, status, embedding_model, total_chunks, processed_chunks, error, metadata, created_at, updated_at
                    FROM {self._schema_name()}.vectorization_jobs
                    WHERE id = %s
                    """,
                    (job_id,),
                )
                row = cur.fetchone()
        if not row:
            return None
        return {
            "id": row[0],
            "status": row[1],
            "embedding_model": row[2],
            "total_chunks": row[3],
            "processed_chunks": row[4],
            "error": row[5],
            "metadata": row[6],
            "created_at": row[7].isoformat() if row[7] else None,
            "updated_at": row[8].isoformat() if row[8] else None,
        }

    def mark_vectorization_job_running(self, job_id: str) -> None:
        self._update_vectorization_job(job_id, status="running")

    def increment_vectorization_job_progress(self, job_id: str, processed_increment: int = 1) -> None:
        if not self.available:
            return
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    UPDATE {self._schema_name()}.vectorization_jobs
                    SET processed_chunks = processed_chunks + %s, updated_at = %s
                    WHERE id = %s
                    """,
                    (processed_increment, _utcnow(), job_id),
                )
            conn.commit()

    def complete_vectorization_job(self, job_id: str) -> None:
        self._update_vectorization_job(job_id, status="completed")

    def fail_vectorization_job(self, job_id: str, error_message: str) -> None:
        self._update_vectorization_job(job_id, status="failed", error=error_message)

    def fetch_chunks_for_vectorization(self, embedding_model: str, limit: Optional[int] = None) -> list[dict[str, Any]]:
        if not self.available:
            return []
        sql = f"""
            SELECT id, chunk_text
            FROM {self._schema_name()}.rag_chunks
            WHERE embedding_vector IS NULL OR embedding_model IS DISTINCT FROM %s
            ORDER BY created_at ASC
        """
        params: list[Any] = [embedding_model]
        if limit is not None:
            sql += " LIMIT %s"
            params.append(limit)

        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, tuple(params))
                rows = cur.fetchall()
        return [{"id": row[0], "chunk_text": row[1]} for row in rows]

    def save_chunk_embedding(self, chunk_id: str, embedding_model: str, embedding: list[float]) -> None:
        if not self.available:
            return
        vector_literal = "[" + ",".join(str(float(x)) for x in embedding) + "]"
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    UPDATE {self._schema_name()}.rag_chunks
                    SET embedding_model = %s,
                        embedding = %s,
                        embedding_vector = %s::vector
                    WHERE id = %s
                    """,
                    (embedding_model, embedding, vector_literal, chunk_id),
                )
            conn.commit()

    def search_similar_chunks(self, embedding: list[float], embedding_model: str, limit: int = 5) -> list[dict[str, Any]]:
        if not self.available:
            return []
        vector_literal = "[" + ",".join(str(float(x)) for x in embedding) + "]"
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    SELECT
                        c.id,
                        c.chunk_text,
                        c.metadata,
                        d.title,
                        1 - (c.embedding_vector <=> %s::vector) AS similarity
                    FROM {self._schema_name()}.rag_chunks c
                    JOIN {self._schema_name()}.rag_documents d ON d.id = c.document_id
                    WHERE c.embedding_vector IS NOT NULL
                      AND c.embedding_model = %s
                    ORDER BY c.embedding_vector <=> %s::vector
                    LIMIT %s
                    """,
                    (vector_literal, embedding_model, vector_literal, limit),
                )
                rows = cur.fetchall()
        return [
            {
                "id": row[0],
                "chunk_text": row[1],
                "metadata": row[2],
                "document_title": row[3],
                "similarity": float(row[4]) if row[4] is not None else None,
            }
            for row in rows
        ]

    def _create_session(self, cur, session_type: str, source_route: str, project_name: Optional[str], metadata: dict[str, Any]) -> str:
        session_id = str(uuid.uuid4())
        cur.execute(
            f"""
            INSERT INTO {self._schema_name()}.ai_sessions (id, session_type, source_route, project_name, metadata, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (session_id, session_type, source_route, project_name, self._json(metadata), _utcnow()),
        )
        return session_id

    def _insert_message(
        self,
        cur,
        session_id: str,
        role: str,
        content: str,
        provider: Optional[str],
        model_name: Optional[str],
        metadata: dict[str, Any],
    ) -> str:
        message_id = str(uuid.uuid4())
        cur.execute(
            f"""
            INSERT INTO {self._schema_name()}.ai_messages (id, session_id, role, content, provider, model_name, metadata, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (message_id, session_id, role, content, provider, model_name, self._json(metadata), _utcnow()),
        )
        return message_id

    def _insert_artifact(
        self,
        cur,
        artifact_id: str,
        session_id: str,
        message_id: Optional[str],
        artifact_type: str,
        title: str,
        content: str,
        source_route: str,
        model_name: Optional[str],
        provider: Optional[str],
        file_path: Optional[str],
        metadata: dict[str, Any],
    ) -> None:
        cur.execute(
            f"""
            INSERT INTO {self._schema_name()}.ai_artifacts (
                id, session_id, message_id, artifact_type, title, content, source_route,
                provider, model_name, file_path, metadata, created_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                artifact_id,
                session_id,
                message_id,
                artifact_type,
                title,
                content,
                source_route,
                provider,
                model_name,
                file_path,
                self._json(metadata),
                _utcnow(),
            ),
        )

    def _insert_document_with_chunks(
        self,
        cur,
        session_id: str,
        artifact_id: str,
        document_type: str,
        title: str,
        content: str,
        metadata: dict[str, Any],
    ) -> None:
        document_id = str(uuid.uuid4())
        cur.execute(
            f"""
            INSERT INTO {self._schema_name()}.rag_documents (id, session_id, artifact_id, document_type, title, content, metadata, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (document_id, session_id, artifact_id, document_type, title, content, self._json(metadata), _utcnow()),
        )

        for chunk_index, chunk_text in enumerate(self._chunk_text(content)):
            cur.execute(
                f"""
                INSERT INTO {self._schema_name()}.rag_chunks (id, document_id, chunk_index, chunk_text, embedding_model, embedding, metadata, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    str(uuid.uuid4()),
                    document_id,
                    chunk_index,
                    chunk_text,
                    metadata.get("embedding_model"),
                    None,
                    self._json({"source_title": title, **metadata}),
                    _utcnow(),
                ),
            )

    def _chunk_text(self, content: str, chunk_size: int = 1200, overlap: int = 150) -> list[str]:
        normalized = (content or "").strip()
        if not normalized:
            return []

        chunks: list[str] = []
        start = 0
        while start < len(normalized):
            end = min(len(normalized), start + chunk_size)
            chunks.append(normalized[start:end])
            if end >= len(normalized):
                break
            start = max(0, end - overlap)
        return chunks

    def _json(self, value: dict[str, Any]):
        if Json is not None:
            return Json(value)
        return json.dumps(value, ensure_ascii=False)

    def _update_vectorization_job(self, job_id: str, status: str, error: Optional[str] = None) -> None:
        if not self.available:
            return
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    UPDATE {self._schema_name()}.vectorization_jobs
                    SET status = %s, error = %s, updated_at = %s
                    WHERE id = %s
                    """,
                    (status, error, _utcnow(), job_id),
                )
            conn.commit()

    def _schema_name(self) -> str:
        schema = self.config.schema.strip()
        if not schema.replace("_", "").isalnum():
            raise ValueError(f"Invalid PostgreSQL schema name: {schema}")
        return schema
