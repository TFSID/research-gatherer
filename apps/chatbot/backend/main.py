from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Dict, Any
import motor.motor_asyncio
from bson import ObjectId
import os
import httpx
import json

app = FastAPI(title="Research Chatbot API", version="1.0.0")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB setup
MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongodb:27017")
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
db = client.chatbot_db

# Pydantic Models
class Message(BaseModel):
    role: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ChatSession(BaseModel):
    session_id: Optional[str] = None
    title: str = "New Chat"
    messages: List[Message] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ConfigItem(BaseModel):
    api_base: str = "http://research-gatherer:8000"
    api_key: str = ""
    model_name: str = "research-assistant"
    stream_enabled: bool = True
    byok_enabled: bool = False
    byok_url: str = "https://api.openai.com/v1"
    byok_key: str = ""
    byok_model: str = "gpt-4o"

# Helper function
def serialize_doc(doc):
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc

# Health Check
@app.get("/health")
async def health_check():
    try:
        await client.admin.command('ping')
        return {
            "status": "healthy",
            "mongodb": "connected",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "mongodb": "disconnected",
            "error": str(e)
        }

# Session Management Endpoints
@app.get("/api/sessions")
async def get_all_sessions():
    """Get all chat sessions"""
    sessions = []
    async for session in db.sessions.find().sort("updated_at", -1):
        sessions.append(serialize_doc(session))
    return {"sessions": sessions, "count": len(sessions)}

@app.post("/api/sessions")
async def create_session(session: ChatSession):
    """Create a new chat session"""
    session_dict = session.dict(exclude={"session_id"})
    result = await db.sessions.insert_one(session_dict)
    return {
        "session_id": str(result.inserted_id),
        "status": "created"
    }

@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """Get a specific chat session"""
    try:
        session = await db.sessions.find_one({"_id": ObjectId(session_id)})
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return serialize_doc(session)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid session ID: {str(e)}")

@app.put("/api/sessions/{session_id}")
async def update_session(session_id: str, session: ChatSession):
    """Update a chat session"""
    try:
        session_dict = session.dict(exclude={"session_id"})
        session_dict["updated_at"] = datetime.utcnow()
        
        result = await db.sessions.update_one(
            {"_id": ObjectId(session_id)},
            {"$set": session_dict}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {"status": "updated", "session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a chat session"""
    try:
        result = await db.sessions.delete_one({"_id": ObjectId(session_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"status": "deleted", "session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/sessions/{session_id}/messages")
async def add_message(session_id: str, message: Message):
    """Add a message to a session"""
    try:
        result = await db.sessions.update_one(
            {"_id": ObjectId(session_id)},
            {
                "$push": {"messages": message.dict()},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {"status": "message_added"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Config Management Endpoints
@app.get("/api/config")
async def get_config():
    """Get current configuration"""
    config = await db.config.find_one({"_id": "default"})
    if not config:
        # Create default config
        default_config = ConfigItem().dict()
        default_config["_id"] = "default"
        await db.config.insert_one(default_config)
        return default_config
    return config

@app.put("/api/config")
async def update_config(config: ConfigItem):
    """Update configuration"""
    config_dict = config.dict()
    config_dict["_id"] = "default"
    config_dict["updated_at"] = datetime.utcnow()
    
    await db.config.update_one(
        {"_id": "default"},
        {"$set": config_dict},
        upsert=True
    )
    
    return {"status": "updated"}

# Proxy endpoint untuk research-gatherer API
@app.post("/api/proxy/chat")
async def proxy_chat(payload: Dict[str, Any]):
    """Proxy request to research-gatherer API"""
    config = await db.config.find_one({"_id": "default"})
    if not config:
        raise HTTPException(status_code=500, detail="Configuration not found")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            headers = {"Content-Type": "application/json"}
            if config.get("api_key"):
                headers["X-API-Key"] = config["api_key"]
            
            url = f"{config['api_base']}/v1/chat/completions"
            response = await client.post(url, json=payload, headers=headers)
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Research API error: {response.text}"
                )
            
            return response.json()
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Failed to connect to research API: {str(e)}")

# Statistics endpoint
@app.get("/api/stats")
async def get_statistics():
    """Get database statistics"""
    session_count = await db.sessions.count_documents({})
    total_messages = await db.sessions.aggregate([
        {"$project": {"message_count": {"$size": "$messages"}}},
        {"$group": {"_id": None, "total": {"$sum": "$message_count"}}}
    ]).to_list(1)
    
    return {
        "total_sessions": session_count,
        "total_messages": total_messages[0]["total"] if total_messages else 0,
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)