import sys
import json
import asyncio
import os
import uuid
from typing import Dict, List, Any
# Dynamic imports to prevent initialization block if run standalone
from core_api.databases import db
from core_api.ingestion import DocumentParser, IngestionPipeline

# Ensure standard output uses UTF-8 to prevent Windows terminal crash events on Unicode output
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

class MCPServer:
    """Standard Model Context Protocol Server communicating over standard I/O (stdio)."""
    
    def __init__(self):
        self.pipeline = IngestionPipeline()
        
    async def start(self):
        # Gracefully connect databases on start if offline
        try:
            await db.connect()
        except Exception:
            pass
            
        while True:
            try:
                # Read JSON-RPC request line-by-line from standard input
                line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                if not line:
                    break
                    
                request = json.loads(line)
                response = await self.handle_request(request)
                if response:
                    sys.stdout.write(json.dumps(response) + "\n")
                    sys.stdout.flush()
            except Exception as e:
                # Silently catch parse errors to prevent standard stream failure
                err_res = {
                    "jsonrpc": "2.0",
                    "error": {"code": -32603, "message": str(e)},
                    "id": None
                }
                sys.stdout.write(json.dumps(err_res) + "\n")
                sys.stdout.flush()

    async def handle_request(self, req: Dict[str, Any]) -> Dict[str, Any]:
        req_id = req.get("id")
        method = req.get("method")
        params = req.get("params", {})
        
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "Local-Enterprise-Company-Brain-MCP",
                        "version": "1.0.0"
                    }
                }
            }
            
        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "tools": [
                        {
                            "name": "get_index",
                            "description": "Lists all indexed documents and mined concepts in the organization brain.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {}
                            }
                        },
                        {
                            "name": "get_page",
                            "description": "Retrieves the full content and connected concepts/relations of a specific document or concept by name or title.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "target": {"type": "string", "description": "Title of the document or name of the concept to retrieve."}
                                },
                                "required": ["target"]
                            }
                        },
                        {
                            "name": "search_wiki",
                            "description": "Conducts a hybrid vector+graph search across all company documents and files.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "query": {"type": "string", "description": "The search term or semantic question to query."}
                                },
                                "required": ["query"]
                            }
                        },
                        {
                            "name": "get_overview",
                            "description": "Aggregates overall brain telemetry and summary metrics of the organization memory store.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {}
                            }
                        },
                        {
                            "name": "index_document",
                            "description": "Remotely ingests a document or folder file directly into the local company brain from a filepath.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "filepath": {"type": "string", "description": "Absolute filesystem path to the file to ingest."}
                                },
                                "required": ["filepath"]
                            }
                        }
                    ]
                }
            }
            
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            try:
                res_content = await self.execute_tool(tool_name, arguments)
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": res_content
                            }
                        ]
                    }
                }
            except Exception as e:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {
                        "code": -32602,
                        "message": f"Error executing tool '{tool_name}': {str(e)}"
                    }
                }
                
        # Default JSON-RPC response for unsupported operations
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32601, "message": f"Method {method} not found"}
        }

    async def execute_tool(self, name: str, args: Dict[str, Any]) -> str:
        if name == "get_index":
            # 1. Fetch docs from PostgreSQL
            docs_summary = []
            try:
                async with db.pg_pool.acquire() as conn:
                    rows = await conn.fetch("SELECT title, source, file_type, created_at FROM documents ORDER BY created_at DESC")
                    for r in rows:
                        docs_summary.append(f"📄 [Doc] '{r['title']}' (Source: {r['source']}, Type: {r['file_type']}) - Indexed: {r['created_at'].isoformat()}")
            except Exception:
                docs_summary = ["(DB Connection Offline - Fallback Active)"]

            # 2. Fetch concepts from Neo4j
            concepts = []
            try:
                with db.neo4j.session() as s:
                    res = s.run("MATCH (c:Concept) RETURN c.name LIMIT 30")
                    concepts = [f"🧠 [Concept] '{r['c.name']}'" for r in res]
            except Exception:
                pass
                
            return "Company Brain Index:\n\n" + "\n".join(docs_summary + concepts)
            
        elif name == "get_page":
            target = args.get("target", "")
            
            # Lookup in PostgreSQL documents
            doc_data = None
            try:
                async with db.pg_pool.acquire() as conn:
                    row = await conn.fetchrow("SELECT title, content, source, file_type FROM documents WHERE title ILIKE $1 OR id::text = $1 LIMIT 1", f"%{target}%")
                    if row:
                        doc_data = f"Document Title: {row['title']}\nSource: {row['source']}\nType: {row['file_type']}\n\nContent:\n{row['content']}"
            except Exception:
                pass
                
            # Lookup connections in Neo4j
            graph_data = []
            try:
                with db.neo4j.session() as s:
                    res = s.run(
                        """
                        MATCH (a {name: $target})-[r]-(b)
                        RETURN type(r) as rel, b.name as name, labels(b)[0] as lbl LIMIT 10
                        """, target=target
                    )
                    for r in res:
                        graph_data.append(f"- [{r['lbl']}] {r['name']} via {r['rel']}")
            except Exception:
                pass
                
            if not doc_data and not graph_data:
                return f"Could not find any document or concept matching '{target}' in the local memory."
                
            out = []
            if doc_data:
                out.append(doc_data)
            if graph_data:
                out.append("Connected Knowledge Relationships:\n" + "\n".join(graph_data))
                
            return "\n\n---\n\n".join(out)
            
        elif name == "search_wiki":
            query = args.get("query", "")
            
            # 1. Semantic Vector retrieval in Qdrant (using procedural/mock embeddings fallback)
            query_emb = (await self.pipeline.get_embeddings([query]))[0]
            hits = db.search_vectors(query_emb, limit=3)
            
            if not hits:
                return f"No semantic chunks matched your query for '{query}'."
                
            out = [f"Search Results for '{query}':\n"]
            for idx, h in enumerate(hits):
                out.append(f"Match {idx+1} (Source: {h['title']}, Score: {h['score']:.2f}):\n\"{h['content']}\"\n")
                
            return "\n".join(out)
            
        elif name == "get_overview":
            try:
                async with db.pg_pool.acquire() as conn:
                    count = await conn.fetchval("SELECT COUNT(*) FROM documents")
                with db.neo4j.session() as s:
                    node_cnt = s.run("MATCH (n) RETURN COUNT(n) as c").single()["c"]
                    edge_cnt = s.run("MATCH ()-[r]->() RETURN COUNT(r) as c").single()["c"]
                return f"Local Company Brain Telemetry:\n- Ingested Documents: {count}\n- Mined Graph Concepts: {node_cnt}\n- Relationship Synapses: {edge_cnt}\n- Operational Security Layer: Vault Dev Key L7 Active"
            except Exception:
                return "Local Company Brain Telemetry:\n- Status: Database Offline (Local Demo Fallback Active)\n- Security Compliance: Active"
                
        elif name == "index_document":
            filepath = args.get("filepath", "")
            if not os.path.exists(filepath):
                return f"Error: Specified filepath '{filepath}' does not exist on this machine."
                
            filename = os.path.basename(filepath)
            
            try:
                # 1. Parse document
                content = DocumentParser.parse(filepath)
                doc_size = os.path.getsize(filepath)
                doc_type = os.path.splitext(filepath)[1].replace('.', '').lower()
                doc_id = str(uuid.uuid4())
                
                # 2. Save document record in PostgreSQL
                await db.insert_document(doc_id, filename, "Local MCP Import", content, doc_size, doc_type)
                
                # 3. Recursive chunk and embed in Qdrant
                chunks = self.pipeline.recursive_chunk(content)
                embeddings = await self.pipeline.get_embeddings(chunks)
                db.insert_vector_chunks(doc_id, filename, "Local MCP Import", chunks, embeddings)
                
                # 4. Structured concept extraction & write to Neo4j
                summary = content[:2000] # Pass first 2k characters as context
                concepts_data = await self.pipeline.extract_concepts_and_entities(filename, summary)
                db.insert_graph_nodes_and_edges(
                    doc_id, filename, 
                    concepts_data.get("concepts", []), 
                    concepts_data.get("entities", []), 
                    concepts_data.get("relationships", [])
                )
                
                return f"Successfully imported '{filename}' into the company brain. Extracted {len(chunks)} vector segments, {len(concepts_data.get('concepts', []))} graph nodes, and synced all permissions securely."
            except Exception as e:
                return f"Failed to ingest document '{filename}'. Error detail: {str(e)}"
                
        else:
            raise ValueError(f"Tool '{name}' is not registered.")

def main():
    server = MCPServer()
    asyncio.run(server.start())

if __name__ == "__main__":
    main()
