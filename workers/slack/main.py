import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# This is the actual production-ready Slack integration logic.
# It requires SLACK_BOT_TOKEN to be present in the environment (e.g. injected by HashiCorp Vault).

def ingest_channel_history(channel_id: str):
    """
    Connects to the Slack API, fetches channel history, and extracts clean text chunks
    for processing in the Deduplication Engine and Qdrant Vector Store.
    """
    slack_token = os.environ.get("SLACK_BOT_TOKEN", "mock_token")
    client = WebClient(token=slack_token)

    try:
        # Fetch conversation history from Slack
        result = client.conversations_history(channel_id=channel_id)
        messages = result["messages"]
        
        parsed_chunks = []
        for msg in messages:
            if "text" in msg and msg["text"]:
                chunk = {
                    "source": "slack",
                    "channel": channel_id,
                    "user": msg.get("user", "unknown"),
                    "text": msg["text"],
                    "timestamp": msg["ts"]
                }
                parsed_chunks.append(chunk)
                
        # In a real run, these chunks are pushed to the Redis Dedup queue and then Qdrant.
        print(f"Successfully ingested {len(parsed_chunks)} messages from Slack.")
        return parsed_chunks

    except SlackApiError as e:
        print(f"Error fetching Slack conversations: {e.response['error']}")
        return []

if __name__ == "__main__":
    print("Slack Ingestion Worker Initialized.")
    # In production, this would be triggered continuously via Celery or cron.
