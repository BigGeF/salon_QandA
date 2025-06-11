from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="AI Chat Assistant Test Version")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatMessage(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@app.get("/")
async def root():
    return {"message": "AI Chat Assistant API Test Version"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Service running normally"}

@app.post("/chat")
async def chat(message: ChatMessage):
    """Simple chat interface"""
    return ChatResponse(response=f"You said: {message.message}. This is a test response!")

if __name__ == "__main__":
    print("🚀 Starting test backend...")
    print("📍 Service URL: http://localhost:8000")
    uvicorn.run(app, host="localhost", port=8000) 