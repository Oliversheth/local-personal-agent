from chromadb import Client
import chromadb
from typing import List, Optional
import os
import json
from datetime import datetime

# Initialize ChromaDB client
client = Client()

# Create or get collection
try:
    collection = client.get_collection("memory")
except ValueError:
    # Collection doesn't exist, create it
    collection = client.create_collection("memory")

def embed_and_store(id: str, text: str, metadata: Optional[dict] = None) -> bool:
    """
    Store text with embedding in the vector database
    """
    try:
        # Add timestamp to metadata
        if metadata is None:
            metadata = {}
        metadata["timestamp"] = datetime.now().isoformat()
        
        collection.add(
            documents=[text],
            ids=[id],
            metadatas=[metadata]
        )
        return True
    except Exception as e:
        print(f"Error storing in memory: {str(e)}")
        return False

def retrieve_context(query: str, n_results: int = 5) -> str:
    """
    Retrieve relevant context from memory based on query
    """
    try:
        results = collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        # Extract documents from results
        documents = results.get("documents", [[]])
        if documents and documents[0]:
            return "\n".join(documents[0])
        return ""
    except Exception as e:
        print(f"Error retrieving context: {str(e)}")
        return ""

def store_conversation(conversation_id: str, messages: List[dict]) -> bool:
    """
    Store a conversation in memory
    """
    try:
        # Convert messages to text
        conversation_text = "\n".join([
            f"{msg['role']}: {msg['content']}" 
            for msg in messages
        ])
        
        metadata = {
            "type": "conversation",
            "conversation_id": conversation_id,
            "message_count": len(messages)
        }
        
        return embed_and_store(
            id=f"conversation_{conversation_id}",
            text=conversation_text,
            metadata=metadata
        )
    except Exception as e:
        print(f"Error storing conversation: {str(e)}")
        return False

def store_screenshot_analysis(screenshot_id: str, analysis: str, ocr_text: str = "") -> bool:
    """
    Store screenshot analysis in memory
    """
    try:
        # Combine analysis and OCR text
        full_text = f"Screenshot Analysis: {analysis}"
        if ocr_text:
            full_text += f"\nOCR Text: {ocr_text}"
        
        metadata = {
            "type": "screenshot_analysis",
            "screenshot_id": screenshot_id,
            "has_ocr": bool(ocr_text)
        }
        
        return embed_and_store(
            id=f"screenshot_{screenshot_id}",
            text=full_text,
            metadata=metadata
        )
    except Exception as e:
        print(f"Error storing screenshot analysis: {str(e)}")
        return False

def store_automation_action(action_id: str, action_type: str, details: dict) -> bool:
    """
    Store automation action in memory
    """
    try:
        # Create text description of the action
        action_text = f"Automation Action: {action_type}\nDetails: {json.dumps(details, indent=2)}"
        
        metadata = {
            "type": "automation_action",
            "action_type": action_type,
            "action_id": action_id
        }
        
        return embed_and_store(
            id=f"action_{action_id}",
            text=action_text,
            metadata=metadata
        )
    except Exception as e:
        print(f"Error storing automation action: {str(e)}")
        return False

def search_by_type(content_type: str, query: str = "", n_results: int = 10) -> List[dict]:
    """
    Search for specific types of content
    """
    try:
        if query:
            results = collection.query(
                query_texts=[query],
                n_results=n_results,
                where={"type": content_type}
            )
        else:
            # Get all results of a specific type
            results = collection.get(
                where={"type": content_type}
            )
        
        # Format results
        formatted_results = []
        documents = results.get("documents", [])
        metadatas = results.get("metadatas", [])
        ids = results.get("ids", [])
        
        for i, doc in enumerate(documents):
            formatted_results.append({
                "id": ids[i] if i < len(ids) else f"unknown_{i}",
                "content": doc,
                "metadata": metadatas[i] if i < len(metadatas) else {}
            })
        
        return formatted_results
    except Exception as e:
        print(f"Error searching by type: {str(e)}")
        return []

def clear_old_entries(days_old: int = 30) -> bool:
    """
    Clear entries older than specified days
    """
    try:
        # This is a simple implementation - in a real app you'd want more sophisticated cleanup
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        # Get all entries
        all_entries = collection.get()
        
        # Find old entries
        old_ids = []
        for i, metadata in enumerate(all_entries.get("metadatas", [])):
            if metadata and "timestamp" in metadata:
                entry_date = datetime.fromisoformat(metadata["timestamp"])
                if entry_date < cutoff_date:
                    old_ids.append(all_entries["ids"][i])
        
        # Delete old entries
        if old_ids:
            collection.delete(ids=old_ids)
            print(f"Deleted {len(old_ids)} old entries")
        
        return True
    except Exception as e:
        print(f"Error clearing old entries: {str(e)}")
        return False

def get_memory_stats() -> dict:
    """
    Get statistics about stored memory
    """
    try:
        all_entries = collection.get()
        total_count = len(all_entries.get("ids", []))
        
        # Count by type
        type_counts = {}
        for metadata in all_entries.get("metadatas", []):
            if metadata and "type" in metadata:
                content_type = metadata["type"]
                type_counts[content_type] = type_counts.get(content_type, 0) + 1
        
        return {
            "total_entries": total_count,
            "by_type": type_counts,
            "collection_name": collection.name
        }
    except Exception as e:
        print(f"Error getting memory stats: {str(e)}")
        return {"error": str(e)}