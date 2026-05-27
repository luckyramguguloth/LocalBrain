import asyncio
from core_api.databases import db

async def init_postgres():
    print("Initializing PostgreSQL tables...")
    await db.connect()
    async with db.pg_pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id UUID PRIMARY KEY,
                source VARCHAR(50),
                content TEXT,
                permissions TEXT[],
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
    print("PostgreSQL ready.")

def init_qdrant():
    print("Initializing Qdrant Vector Collection...")
    from qdrant_client.http.models import Distance, VectorParams
    try:
        db.qdrant.create_collection(
            collection_name="enterprise_memory",
            vectors_config=VectorParams(size=1024, distance=Distance.COSINE),
        )
        print("Qdrant ready.")
    except Exception as e:
        print(f"Qdrant collection may already exist: {e}")

async def main():
    await init_postgres()
    init_qdrant()
    await db.disconnect()
    print("Database initialization complete.")

if __name__ == "__main__":
    asyncio.run(main())
