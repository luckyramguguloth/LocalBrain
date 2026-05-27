from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from neo4j import GraphDatabase
import asyncpg
import redis.asyncio as redis
import uuid
from typing import List, Dict, Any
from .config import settings
from .logger import get_logger

logger = get_logger("databases")

class ThreeStoreManager:
    """Manages secure on-premise connections and writes to PostgreSQL, Qdrant, Neo4j, and Redis."""
    
    def __init__(self):
        # 1. Vector Store (Qdrant)
        self.qdrant = QdrantClient(url=settings.QDRANT_URL)
        
        # 2. Graph Store (Neo4j)
        self.neo4j = GraphDatabase.driver(
            settings.NEO4J_URI, 
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )
        
        # 3. Cache Layer (Redis)
        self.redis = redis.from_url(settings.REDIS_URL)
        
        self.pg_pool = None

    async def connect(self):
        logger.info("Initializing connection pool to PostgreSQL...")
        self.pg_pool = await asyncpg.create_pool(settings.POSTGRES_DSN)
        logger.info("Connected to PostgreSQL. Bootstrapping schemas...")
        await self.init_db_schemas()
        logger.info("Successfully completed database connection & bootstrapping stages.")

    async def disconnect(self):
        logger.info("Closing database connections gracefully...")
        self.neo4j.close()
        if self.pg_pool:
            await self.pg_pool.close()
        await self.redis.close()
        logger.info("Database pools closed.")

    async def init_db_schemas(self):
        """Creates PostgreSQL tables and sets up Qdrant collections on startup."""
        # 1. PostgreSQL Document Logs Table
        async with self.pg_pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id UUID PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    source VARCHAR(50) NOT NULL,
                    content TEXT NOT NULL,
                    file_size INTEGER DEFAULT 0,
                    file_type VARCHAR(20) DEFAULT 'txt',
                    permissions TEXT[] DEFAULT ARRAY['admin', 'engineering'],
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
        # 2. Qdrant Vector Collection
        try:
            # We check if collection exists, if not, create it
            collections = self.qdrant.get_collections().collections
            names = [c.name for c in collections]
            if "enterprise_memory" not in names:
                logger.info("Qdrant collection 'enterprise_memory' not found. Creating collection...")
                self.qdrant.create_collection(
                    collection_name="enterprise_memory",
                    vectors_config=VectorParams(size=1024, distance=Distance.COSINE),
                )
                logger.info("Successfully created Qdrant vector collection.")
        except Exception as e:
            logger.warning(f"Could not create Qdrant collection (Qdrant offline?): {e}")

    async def insert_document(self, doc_id: str, title: str, source: str, content: str, file_size: int, file_type: str, permissions: List[str] = None) -> bool:
        """Inserts document metadata into PostgreSQL."""
        if not permissions:
            permissions = ["admin", "engineering"]
        try:
            logger.info(f"Metadata write: Inserting document '{title}' ({file_type}, {file_size} bytes) with ID {doc_id} to Postgres...")
            async with self.pg_pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO documents (id, title, source, content, file_size, file_type, permissions)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                    ON CONFLICT (id) DO UPDATE 
                    SET title = $2, source = $3, content = $4, file_size = $5, file_type = $6, permissions = $7;
                    """,
                    uuid.UUID(doc_id), title, source, content, file_size, file_type, permissions
                )
            logger.info("Successfully wrote document metadata to PostgreSQL.")
            return True
        except Exception as e:
            logger.error(f"PostgreSQL Write Error for doc_id {doc_id}: {e}")
            return False

    def insert_vector_chunks(self, doc_id: str, title: str, source: str, chunks: List[str], embeddings: List[List[float]], permissions: List[str] = None, uploaded_at: str = None):
        """Saves text chunks, their semantic embeddings, permissions, and upload timestamp to Qdrant."""
        import datetime
        if not permissions:
            permissions = ["admin", "engineering"]
        if not uploaded_at:
            uploaded_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            points = []
            for idx, (chunk, emb) in enumerate(zip(chunks, embeddings)):
                point_id = str(uuid.uuid5(uuid.UUID(doc_id), f"chunk_{idx}"))
                points.append(
                    PointStruct(
                        id=point_id,
                        vector=emb,
                        payload={
                            "doc_id": doc_id,
                            "title": title,
                            "source": source,
                            "chunk_index": idx,
                            "content": chunk,
                            "permissions": permissions,
                            "uploaded_at": uploaded_at
                        }
                    )
                )
            logger.info(f"Vector write: Upserting {len(points)} chunks for document '{title}' into Qdrant...")
            self.qdrant.upsert(
                collection_name="enterprise_memory",
                points=points
            )
            logger.info(f"Successfully upserted vectors to Qdrant for document ID {doc_id}.")
            return True
        except Exception as e:
            logger.error(f"Qdrant Write Error for doc_id {doc_id}: {e}")
            return False

    def insert_graph_nodes_and_edges(self, doc_id: str, doc_title: str, concepts: List[str], entities: List[str], relationships: List[Dict[str, Any]]):
        """Maps documents, conceptual topics, and physical entities in Neo4j."""
        try:
            with self.neo4j.session() as session:
                # 1. Merge Document node
                session.run(
                    """
                    MERGE (d:Document {id: $doc_id})
                    ON CREATE SET d.title = $doc_title, d.created_at = timestamp()
                    ON MATCH SET d.title = $doc_title
                    """,
                    doc_id=doc_id, doc_title=doc_title
                )
                
                # 2. Merge Concept nodes and link to Document
                for concept in concepts:
                    session.run(
                        """
                        MERGE (c:Concept {name: $name})
                        WITH c
                        MATCH (d:Document {id: $doc_id})
                        MERGE (d)-[:MENTIONS]->(c)
                        """,
                        name=concept, doc_id=doc_id
                    )

                # 3. Merge Entity nodes and link to Document
                for entity in entities:
                    session.run(
                        """
                        MERGE (e:Entity {name: $name})
                        WITH e
                        MATCH (d:Document {id: $doc_id})
                        MERGE (d)-[:MENTIONS]->(e)
                        """,
                        name=entity, doc_id=doc_id
                    )

                logger.info(f"Graph write: Merging nodes and {len(relationships)} relationships in Neo4j for document '{doc_title}'...")
                # 4. Connect relationships
                for rel in relationships:
                    src = rel["source"]
                    tgt = rel["target"]
                    rtype = rel["type"]
                    
                    # Sanitize relationship label
                    rtype_clean = "".join([c for c in rtype if c.isalnum() or c == '_']).upper()
                    if not rtype_clean:
                        rtype_clean = "RELATED_TO"
                    
                    # Merge nodes and create relationship
                    query = f"""
                    MERGE (a:Concept {{name: $src}})
                    MERGE (b:Concept {{name: $tgt}})
                    MERGE (a)-[:{rtype_clean}]->(b)
                    """
                    session.run(query, src=src, tgt=tgt)
                logger.info(f"Successfully mapped concept graph in Neo4j for document ID {doc_id}.")
            return True
        except Exception as e:
            logger.error(f"Neo4j Graph Write Error for doc_id {doc_id}: {e}")
            return False

    def get_graph_data(self) -> Dict[str, Any]:
        """Queries Neo4j to compile all concept nodes and relations for WebGL rendering."""
        try:
            with self.neo4j.session() as session:
                # Return all documents, concepts, entities, and their interconnections
                result = session.run(
                    """
                    MATCH (n)
                    OPTIONAL MATCH (n)-[r]->(m)
                    RETURN n, r, m LIMIT 200
                    """
                )
                
                nodes = {}
                links = []
                
                for record in result:
                    n = record["n"]
                    r = record["r"]
                    m = record["m"]
                    
                    if n:
                        n_id = n.element_id
                        n_label = list(n.labels)[0] if n.labels else "Node"
                        n_name = n.get("name") or n.get("title") or "Node"
                        nodes[n_id] = {
                            "id": n_id,
                            "label": n_name,
                            "group": n_label,
                            "val": 10 if n_label == "Document" else 5
                        }
                    
                    if m:
                        m_id = m.element_id
                        m_label = list(m.labels)[0] if m.labels else "Node"
                        m_name = m.get("name") or m.get("title") or "Node"
                        nodes[m_id] = {
                            "id": m_id,
                            "label": m_name,
                            "group": m_label,
                            "val": 10 if m_label == "Document" else 5
                        }
                        
                    if r and n and m:
                        links.append({
                            "source": n.element_id,
                            "target": m.element_id,
                            "type": r.type
                        })
                        
                return {"nodes": list(nodes.values()), "links": links}
        except Exception as e:
            # Fallback if Neo4j is not connected (runs in local UI demo)
            return {"nodes": [], "links": []}

    def search_vectors(self, query_emb: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        """Queries Qdrant vector database for highly relevant semantic text chunks."""
        try:
            response = self.qdrant.query_points(
                collection_name="enterprise_memory",
                query=query_emb,
                limit=limit
            )
            search_result = response.points
            return [
                {
                    "content": hit.payload.get("content"),
                    "title": hit.payload.get("title"),
                    "source": hit.payload.get("source"),
                    "permissions": hit.payload.get("permissions", ["admin", "engineering"]),
                    "uploaded_at": hit.payload.get("uploaded_at", "2026-05-23 21:00:00"),
                    "score": hit.score
                } for hit in search_result
            ]
        except Exception as e:
            logger.error(f"Qdrant Vector Search Error: {e}")
            return []

db = ThreeStoreManager()
