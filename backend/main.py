from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
from typing import List, Dict
import time

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
app = FastAPI(title="AI Beauty Salon Assistant", description="AI Assistant with Website RAG", version="1.0.0")

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

# Global storage for scraped content
website_content = {
    "url": "",
    "pages": [],
    "content": "",
    "scraped_at": None
}

# Data models
class ChatMessage(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

class ScrapeRequest(BaseModel):
    url: str

class ScrapeResponse(BaseModel):
    success: bool
    pages_scraped: int
    total_content_length: int
    message: str

class QuestionRequest(BaseModel):
    question: str

class QuestionResponse(BaseModel):
    answer: str
    sources: List[str] = []

# Utility functions
def clean_text(text: str) -> str:
    """Clean and normalize text content"""
    # Remove extra whitespace and normalize
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text

def extract_text_from_html(html: str) -> str:
    """Extract clean text from HTML"""
    soup = BeautifulSoup(html, 'html.parser')
    
    # Remove script and style elements
    for script in soup(["script", "style", "nav", "footer", "header"]):
        script.decompose()
    
    # Get text and clean it
    text = soup.get_text()
    return clean_text(text)

def scrape_page(url: str, max_pages: int = 10) -> Dict:
    """Scrape a website and extract content"""
    scraped_pages = []
    visited_urls = set()
    to_visit = [url]
    base_domain = urlparse(url).netloc
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    while to_visit and len(scraped_pages) < max_pages:
        current_url = to_visit.pop(0)
        
        if current_url in visited_urls:
            continue
            
        visited_urls.add(current_url)
        
        try:
            response = requests.get(current_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Extract text content
            text_content = extract_text_from_html(response.text)
            
            if len(text_content) > 100:  # Only keep pages with substantial content
                scraped_pages.append({
                    "url": current_url,
                    "title": BeautifulSoup(response.text, 'html.parser').title.string if BeautifulSoup(response.text, 'html.parser').title else "No Title",
                    "content": text_content[:5000]  # Limit content length
                })
            
            # Find more links on the same domain
            if len(scraped_pages) < max_pages:
                soup = BeautifulSoup(response.text, 'html.parser')
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    full_url = urljoin(current_url, href)
                    
                    # Only follow links on the same domain
                    if urlparse(full_url).netloc == base_domain and full_url not in visited_urls:
                        to_visit.append(full_url)
            
            time.sleep(0.5)  # Be respectful to the server
            
        except Exception as e:
            print(f"Error scraping {current_url}: {str(e)}")
            continue
    
    return {
        "pages": scraped_pages,
        "total_pages": len(scraped_pages)
    }

def find_relevant_content(question: str, content: str, max_length: int = 3000) -> str:
    """Find the most relevant content for the question"""
    # Simple keyword-based relevance (in a real implementation, you'd use embeddings)
    question_words = set(question.lower().split())
    
    # Split content into chunks
    chunks = content.split('\n\n')
    scored_chunks = []
    
    for chunk in chunks:
        if len(chunk) < 50:  # Skip very short chunks
            continue
            
        chunk_words = set(chunk.lower().split())
        relevance_score = len(question_words.intersection(chunk_words))
        
        if relevance_score > 0:
            scored_chunks.append((relevance_score, chunk))
    
    # Sort by relevance and combine top chunks
    scored_chunks.sort(reverse=True, key=lambda x: x[0])
    
    relevant_content = ""
    for score, chunk in scored_chunks:
        if len(relevant_content) + len(chunk) < max_length:
            relevant_content += chunk + "\n\n"
        else:
            break
    
    return relevant_content if relevant_content else content[:max_length]

# API routes
@app.get("/")
async def root():
    return {"message": "AI Beauty Salon Assistant API with RAG"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "message": "Service running normally", 
        "api_key_configured": bool(api_key),
        "website_loaded": bool(website_content["content"])
    }

@app.post("/scrape-website", response_model=ScrapeResponse)
async def scrape_website(request: ScrapeRequest):
    """Scrape a website and store its content for RAG"""
    try:
        print(f"🕷️ Starting to scrape: {request.url}")
        
        # Scrape the website
        result = scrape_page(request.url, max_pages=10)
        
        if not result["pages"]:
            raise HTTPException(status_code=400, detail="No content could be extracted from the website")
        
        # Store the content globally
        all_content = ""
        for page in result["pages"]:
            all_content += f"Page: {page['title']}\nURL: {page['url']}\nContent: {page['content']}\n\n"
        
        website_content.update({
            "url": request.url,
            "pages": result["pages"],
            "content": all_content,
            "scraped_at": time.time()
        })
        
        print(f"✅ Successfully scraped {result['total_pages']} pages")
        
        return ScrapeResponse(
            success=True,
            pages_scraped=result["total_pages"],
            total_content_length=len(all_content),
            message=f"Successfully scraped {result['total_pages']} pages from {request.url}"
        )
        
    except Exception as e:
        print(f"❌ Error scraping website: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to scrape website: {str(e)}")

@app.post("/ask-question", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """Answer questions using RAG with scraped website content"""
    if not openai_client:
        raise HTTPException(
            status_code=500, 
            detail="OpenAI API key not configured. Please set OPENAI_API_KEY environment variable."
        )
    
    if not website_content["content"]:
        raise HTTPException(
            status_code=400,
            detail="No website content available. Please scrape a website first."
        )
    
    try:
        # Find relevant content for the question
        relevant_content = find_relevant_content(request.question, website_content["content"])
        
        # Create context-aware prompt
        system_prompt = f"""You are a helpful AI assistant for a beauty salon. You have access to information from the salon's website: {website_content['url']}

Use the following website content to answer questions about the salon's services, prices, booking information, and other details. If the information is not available in the provided content, say so clearly.

Website Content:
{relevant_content}

Instructions:
- Answer questions based on the website content provided
- Be helpful and informative
- If specific information isn't available, suggest contacting the salon directly
- Focus on beauty salon services, treatments, prices, and booking information
- Keep responses concise but comprehensive"""

        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.question}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content.strip()
        
        # Extract source URLs
        sources = [page["url"] for page in website_content["pages"][:3]]  # Top 3 sources
        
        return QuestionResponse(
            answer=ai_response,
            sources=sources
        )
        
    except Exception as e:
        print(f"❌ Error generating answer: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    """Fallback chat endpoint for general conversation"""
    if not openai_client:
        raise HTTPException(
            status_code=500, 
            detail="OpenAI API key not configured. Please set OPENAI_API_KEY environment variable."
        )
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a friendly and helpful AI assistant for a beauty salon. Please respond in English."},
                {"role": "user", "content": message.message}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content.strip()
        return ChatResponse(response=ai_response)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")

@app.get("/website-status")
async def website_status():
    """Get current website scraping status"""
    return {
        "website_loaded": bool(website_content["content"]),
        "url": website_content["url"],
        "pages_count": len(website_content["pages"]),
        "content_length": len(website_content["content"]),
        "scraped_at": website_content["scraped_at"]
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting AI Beauty Salon Assistant backend...")
    print("📍 Service URL: http://localhost:8000")
    print("📚 API docs: http://localhost:8000/docs")
    if api_key:
        print("✅ OpenAI API key configured")
    else:
        print("❌ OpenAI API key not configured")
    uvicorn.run(app, host="localhost", port=8000) 