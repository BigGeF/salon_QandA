import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import openai
import requests
from bs4 import BeautifulSoup
import asyncio
import aiohttp
from content_store import content_store
from urllib.parse import urljoin, urlparse
import time

# Load environment variables
load_dotenv()

# Check API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("⚠️ Warning: OPENAI_API_KEY environment variable not found")
    print("📝 Please set your OpenAI API key:")
    print("   export OPENAI_API_KEY='sk-your-api-key-here'")
    print("   or add to .env file: OPENAI_API_KEY=sk-your-api-key-here")

# Create FastAPI application
app = FastAPI(
    title="AI Salon Q&A Assistant", 
    description="Advanced AI-powered Q&A system for beauty salon websites", 
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY
else:
    openai.api_key = None

# Data models
class ChatRequest(BaseModel):
    messages: list

class ScrapeRequest(BaseModel):
    url: str

class QueryRequest(BaseModel):
    query: str
    url: str = None

class TextContentRequest(BaseModel):
    content: str

def extract_links(soup, base_url):
    """Extract all internal links from the page"""
    links = set()
    domain = urlparse(base_url).netloc
    
    for link in soup.find_all('a', href=True):
        href = link['href']
        # Convert relative URLs to absolute
        full_url = urljoin(base_url, href)
        parsed_url = urlparse(full_url)
        
        # Only include links from the same domain
        if parsed_url.netloc == domain:
            # Remove fragments and query parameters for cleaner URLs
            clean_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
            if clean_url != base_url and clean_url.endswith(('/', '.html', '.htm')) or '/' in parsed_url.path:
                links.add(clean_url)
    
    return links

def scrape_single_page(url, headers):
    """Scrape content from a single page"""
    try:
        print(f"  📄 Scraping: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract text content - keep more content
        for script in soup(["script", "style"]):
            script.decompose()
        
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        cleaned_content = '\n'.join(line for line in lines if line and len(line) > 3)
        
        return cleaned_content, soup
    except Exception as e:
        print(f"  ❌ Failed to scrape {url}: {str(e)}")
        return None, None

# API routes
@app.get("/")
async def root():
    return {
        "message": "AI Salon Q&A Assistant API",
        "version": "2.0.0",
        "features": [
            "Advanced content chunking",
            "Persistent storage",
            "Intelligent Q&A",
            "Multi-endpoint API"
        ]
    }

@app.get("/health")
async def health_check():
    stats = content_store.get_storage_stats()
    return {
        "status": "healthy",
        "message": "Service running normally",
        "api_key_configured": bool(OPENAI_API_KEY),
        "storage_stats": stats
    }

@app.post("/scrape-website")
async def scrape_website(req: ScrapeRequest):
    """
    Scrape website content with multi-page analysis
    """
    try:
        # Validate URL
        if not req.url.startswith(('http://', 'https://')):
            raise HTTPException(status_code=400, detail="Invalid URL format")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        print(f"🌐 Starting multi-page analysis of: {req.url}")
        
        # Step 1: Scrape the main page
        main_content, main_soup = scrape_single_page(req.url, headers)
        if not main_content:
            raise HTTPException(status_code=400, detail="Failed to scrape main page")
        
        all_content = [f"=== MAIN PAGE: {req.url} ===\n{main_content}"]
        
        # Step 2: Find all internal links
        internal_links = extract_links(main_soup, req.url)
        print(f"🔗 Found {len(internal_links)} internal links")
        
        # Step 3: Scrape internal pages (limit to prevent overload)
        max_pages = 10  # Limit to prevent excessive scraping
        scraped_pages = 1
        
        for link in list(internal_links)[:max_pages-1]:  # -1 because we already scraped main page
            if scraped_pages >= max_pages:
                break
                
            content, _ = scrape_single_page(link, headers)
            if content and len(content) > 100:  # Only include substantial content
                all_content.append(f"=== PAGE: {link} ===\n{content}")
                scraped_pages += 1
                time.sleep(1)  # Be respectful to the server
        
        # Step 4: Combine all content
        combined_content = "\n\n".join(all_content)
        
        if len(combined_content) < 100:
            raise HTTPException(
                status_code=400, 
                detail="Website content too short or could not be extracted properly"
            )
        
        # Store content using advanced storage system
        storage_result = content_store.store_content(req.url, combined_content)
        
        print(f"✅ Successfully analyzed {scraped_pages} pages from {req.url}")
        print(f"📊 Total content length: {storage_result['content_length']} characters")
        print(f"🧩 Created {storage_result['chunks_created']} chunks")
        
        return {
            "message": f"Successfully analyzed {scraped_pages} pages from {req.url}",
            "url": req.url,
            "pages_analyzed": scraped_pages,
            "internal_links_found": len(internal_links),
            "content_length": storage_result['content_length'],
            "chunks_created": storage_result['chunks_created'],
            "timestamp": storage_result['timestamp']
        }
        
    except requests.RequestException as e:
        print(f"❌ Network error scraping {req.url}: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to fetch website: {str(e)}")
    except Exception as e:
        print(f"❌ Error scraping {req.url}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Scraping error: {str(e)}")

@app.post("/add-text")
async def add_text_content(req: TextContentRequest):
    """
    Add text content directly to the vector database
    """
    try:
        # Validate content
        if not req.content.strip():
            raise HTTPException(status_code=400, detail="Content cannot be empty")
        
        if len(req.content.strip()) < 10:
            raise HTTPException(status_code=400, detail="Content too short (minimum 10 characters)")
        
        # Store content using the content store system
        # Use a special URL identifier for manually added text
        text_url = f"manual_text_{int(time.time())}"
        storage_result = content_store.store_content(text_url, req.content.strip())
        
        print(f"✅ Successfully stored manual text content")
        print(f"📊 Content length: {storage_result['content_length']} characters")
        print(f"🧩 Created {storage_result['chunks_created']} chunks")
        
        return {
            "message": "Text content successfully added to database",
            "content_length": storage_result['content_length'],
            "chunks_created": storage_result['chunks_created'],
            "timestamp": storage_result['timestamp']
        }
        
    except Exception as e:
        print(f"❌ Error storing text content: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to store text content: {str(e)}")

@app.get("/scraping-status")
async def get_scraping_status():
    """Get current scraping status and storage statistics"""
    stats = content_store.get_storage_stats()
    
    if stats["total_urls"] == 0:
        return {
            "has_content": False,
            "message": "No content has been scraped yet"
        }
    
    # Get most recent content info
    latest_content = content_store.get_content()
    
    return {
        "has_content": True,
        "content_length": latest_content["content_length"] if latest_content else 0,
        "chunks_count": latest_content["chunks_count"] if latest_content else 0,
        "last_scraped_url": latest_content["url"] if latest_content else None,
        "last_scraped_at": latest_content["scraped_at"] if latest_content else None,
        "storage_stats": stats
    }

@app.post("/chat")
async def chat_api(req: ChatRequest):
    """
    Enhanced AI chat interface with intelligent content retrieval
    """
    if not openai.api_key:
        raise HTTPException(
            status_code=500, 
            detail="OpenAI API key not configured. Please set OPENAI_API_KEY environment variable."
        )
    
    try:
        # Get the user's latest message
        user_message = ""
        if req.messages and req.messages[-1]["role"] == "user":
            user_message = req.messages[-1]["content"]
        
        # Get relevant content for context
        context_content = content_store.get_all_content_for_context(max_length=3000)
        
        # Prepare messages with enhanced context
        messages = req.messages.copy()
        if context_content:
            # Create a more sophisticated system prompt
            system_prompt = f"""You are a helpful assistant specializing in beauty salon services and information. 
            
Use the following website content to answer questions about the salon's services, prices, location, hours, staff, and policies. 
If the user asks about something not covered in the website content, politely let them know that information isn't available on the website.

Website Content:
{context_content}

Please provide helpful, accurate, and friendly responses based on this information."""
            
            context_message = {
                "role": "system", 
                "content": system_prompt
            }
            messages.insert(0, context_message)
        else:
            # No content available
            no_content_message = {
                "role": "system",
                "content": "You are a helpful assistant. However, no website content has been scraped yet. Please ask the user to provide a salon website URL first so you can help them with specific information about that salon."
            }
            messages.insert(0, no_content_message)
        
        print(f"🤖 Processing chat request with {len(messages)} messages")
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
            max_tokens=512,
            presence_penalty=0.1,
            frequency_penalty=0.1
        )
        
        answer = response.choices[0].message["content"].strip()
        
        print(f"✅ Generated AI response ({len(answer)} characters)")
        
        return {"answer": answer}
        
    except openai.error.RateLimitError:
        raise HTTPException(status_code=429, detail="OpenAI API rate limit exceeded. Please try again later.")
    except openai.error.InvalidRequestError as e:
        raise HTTPException(status_code=400, detail=f"Invalid request to OpenAI API: {str(e)}")
    except Exception as e:
        print(f"❌ OpenAI API error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")

@app.post("/query")
async def intelligent_query(req: QueryRequest):
    """
    Intelligent query endpoint using relevant chunk retrieval
    """
    if not openai.api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    
    try:
        # Get relevant chunks for the query
        relevant_chunks = content_store.get_relevant_chunks(req.query, req.url, max_chunks=3)
        
        if not relevant_chunks:
            return {
                "answer": "I don't have any relevant information to answer your question. Please make sure a website has been scraped first.",
                "chunks_used": 0
            }
        
        # Combine relevant chunks
        context = "\n\n".join([chunk["content"] for chunk in relevant_chunks])
        
        # Create focused prompt
        prompt = f"""Based on the following information from a beauty salon website, please answer the user's question.

Website Information:
{context}

User Question: {req.query}

Please provide a helpful and accurate answer based only on the information provided above."""

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that answers questions about beauty salon services based on provided website content."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=400
        )
        
        answer = response.choices[0].message["content"].strip()
        
        return {
            "answer": answer,
            "chunks_used": len(relevant_chunks),
            "query": req.query
        }
        
    except Exception as e:
        print(f"❌ Query processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Query processing error: {str(e)}")

@app.delete("/reset")
async def reset_content():
    """Clear all stored content"""
    try:
        content_store.clear_content()
        print("🗑️ All content cleared")
        return {"message": "All content cleared successfully"}
    except Exception as e:
        print(f"❌ Error clearing content: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error clearing content: {str(e)}")

@app.get("/storage-stats")
async def get_storage_statistics():
    """Get detailed storage statistics"""
    return content_store.get_storage_stats()

@app.get("/content/{url:path}")
async def get_content_by_url(url: str):
    """Get stored content for a specific URL"""
    # Decode URL
    import urllib.parse
    decoded_url = urllib.parse.unquote(url)
    
    content_data = content_store.get_content(decoded_url)
    if not content_data:
        raise HTTPException(status_code=404, detail="Content not found for this URL")
    
    # Return content without the full text for API efficiency
    return {
        "url": content_data["url"],
        "content_length": content_data["content_length"],
        "chunks_count": content_data["chunks_count"],
        "scraped_at": content_data["scraped_at"],
        "last_accessed": content_data["last_accessed"]
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting AI Salon Q&A backend...")
    print("📍 Service URL: http://localhost:8000")
    print("📚 API docs: http://localhost:8000/docs")
    print("🔧 Features: Advanced chunking, persistent storage, intelligent Q&A")
    if OPENAI_API_KEY:
        print("✅ OpenAI API key configured")
    else:
        print("❌ OpenAI API key not configured")
    uvicorn.run(app, host="localhost", port=8000) 