from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("⚠️  Warning: OPENAI_API_KEY environment variable not found")
    print("📝 Please set your OpenAI API key:")
    print("   export OPENAI_API_KEY='sk-your-api-key-here'")
    print("   or add to .env file: OPENAI_API_KEY=sk-your-api-key-here")

# Create FastAPI application
app = FastAPI(title="AI Chat Assistant", description="Simple AI Chat API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
if api_key:
    openai_client = openai.OpenAI(api_key=api_key)
else:
    openai_client = None

# Data models
class ChatMessage(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

# API routes
@app.get("/")
async def root():
    return {"message": "AI Chat Assistant API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Service running normally", "api_key_configured": bool(api_key)}

@app.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    """AI chat interface"""
    if not openai_client:
        raise HTTPException(
            status_code=500, 
            detail="OpenAI API key not configured. Please set OPENAI_API_KEY environment variable."
        )
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a friendly and helpful AI assistant. Please respond in English."},
                {"role": "user", "content": message.message}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content.strip()
        return ChatResponse(response=ai_response)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting AI chat backend...")
    print("📍 Service URL: http://localhost:8000")
    print("📚 API docs: http://localhost:8000/docs")
    if api_key:
        print("✅ OpenAI API key configured")
    else:
        print("❌ OpenAI API key not configured")
    uvicorn.run(app, host="localhost", port=8000) 