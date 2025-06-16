import json
import os
from datetime import datetime
from typing import List, Dict, Optional
import re

class ContentStore:
    """
    Advanced content storage system with chunking and persistence
    """
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.storage_file = os.path.join(data_dir, "scraped_content.json")
        self.chunk_size = 1000
        self.chunk_overlap = 200
        self._ensure_data_dir()
        
    def _ensure_data_dir(self):
        """Ensure data directory exists"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
    def _split_text_into_chunks(self, text: str, url: str) -> List[Dict]:
        """
        Split text into overlapping chunks with metadata
        """
        if not text or len(text) < self.chunk_size:
            return [{
                "content": text,
                "chunk_id": 0,
                "start_pos": 0,
                "end_pos": len(text),
                "url": url,
                "timestamp": datetime.now().isoformat()
            }]
        
        chunks = []
        chunk_id = 0
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # If this isn't the last chunk, try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings within the last 200 characters
                search_start = max(start + self.chunk_size - 200, start)
                sentence_end = self._find_sentence_boundary(text, search_start, end)
                if sentence_end > start:
                    end = sentence_end
            
            chunk_content = text[start:end].strip()
            
            if chunk_content:  # Only add non-empty chunks
                chunks.append({
                    "content": chunk_content,
                    "chunk_id": chunk_id,
                    "start_pos": start,
                    "end_pos": end,
                    "url": url,
                    "timestamp": datetime.now().isoformat()
                })
                chunk_id += 1
            
            # Move start position with overlap
            start = end - self.chunk_overlap
            if start >= len(text):
                break
                
        return chunks
    
    def _find_sentence_boundary(self, text: str, start: int, end: int) -> int:
        """
        Find the best sentence boundary within the given range
        """
        # Look for sentence endings (., !, ?)
        sentence_endings = ['.', '!', '?']
        best_pos = end
        
        for i in range(end - 1, start - 1, -1):
            if text[i] in sentence_endings:
                # Make sure it's not an abbreviation or decimal
                if i + 1 < len(text) and text[i + 1].isspace():
                    return i + 1
                    
        # If no sentence boundary found, look for paragraph breaks
        for i in range(end - 1, start - 1, -1):
            if text[i] == '\n' and i + 1 < len(text) and text[i + 1] == '\n':
                return i + 1
                
        return end
    
    def store_content(self, url: str, content: str) -> Dict:
        """
        Store scraped content with chunking and metadata
        """
        # Create chunks
        chunks = self._split_text_into_chunks(content, url)
        
        # Load existing data
        data = self._load_data()
        
        # Store new content
        data[url] = {
            "url": url,
            "original_content": content,
            "content_length": len(content),
            "chunks": chunks,
            "chunks_count": len(chunks),
            "scraped_at": datetime.now().isoformat(),
            "last_accessed": datetime.now().isoformat()
        }
        
        # Save to file
        self._save_data(data)
        
        return {
            "url": url,
            "content_length": len(content),
            "chunks_created": len(chunks),
            "timestamp": data[url]["scraped_at"]
        }
    
    def get_content(self, url: Optional[str] = None) -> Optional[Dict]:
        """
        Retrieve stored content by URL or get the most recent
        """
        data = self._load_data()
        
        if not data:
            return None
            
        if url and url in data:
            # Update last accessed time
            data[url]["last_accessed"] = datetime.now().isoformat()
            self._save_data(data)
            return data[url]
        elif not url:
            # Return most recently scraped content
            latest_url = max(data.keys(), key=lambda k: data[k]["scraped_at"])
            data[latest_url]["last_accessed"] = datetime.now().isoformat()
            self._save_data(data)
            return data[latest_url]
            
        return None
    
    def get_relevant_chunks(self, query: str, url: Optional[str] = None, max_chunks: int = 3) -> List[Dict]:
        """
        Get most relevant chunks for a query (simple keyword matching)
        In a production system, this would use vector embeddings
        """
        content_data = self.get_content(url)
        if not content_data:
            return []
            
        chunks = content_data["chunks"]
        query_words = set(query.lower().split())
        
        # Score chunks based on keyword overlap
        scored_chunks = []
        for chunk in chunks:
            chunk_words = set(chunk["content"].lower().split())
            score = len(query_words.intersection(chunk_words))
            if score > 0:
                scored_chunks.append((score, chunk))
        
        # Sort by score and return top chunks
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        return [chunk for _, chunk in scored_chunks[:max_chunks]]
    
    def get_all_content_for_context(self, url: Optional[str] = None, max_length: int = 2000) -> str:
        """
        Get content formatted for AI context, respecting length limits
        """
        content_data = self.get_content(url)
        if not content_data:
            return ""
            
        # Try to use original content first
        original = content_data["original_content"]
        if len(original) <= max_length:
            return original
            
        # If too long, use chunks
        chunks = content_data["chunks"]
        context = ""
        for chunk in chunks:
            chunk_content = chunk["content"]
            if len(context) + len(chunk_content) + 10 <= max_length:  # +10 for separators
                context += chunk_content + "\n\n"
            else:
                break
                
        return context.strip()
    
    def clear_content(self, url: Optional[str] = None):
        """
        Clear stored content (specific URL or all)
        """
        if url:
            data = self._load_data()
            if url in data:
                del data[url]
                self._save_data(data)
        else:
            # Clear all content
            self._save_data({})
    
    def get_storage_stats(self) -> Dict:
        """
        Get statistics about stored content
        """
        data = self._load_data()
        
        if not data:
            return {
                "total_urls": 0,
                "total_content_length": 0,
                "total_chunks": 0,
                "urls": []
            }
            
        total_length = sum(item["content_length"] for item in data.values())
        total_chunks = sum(item["chunks_count"] for item in data.values())
        
        urls_info = []
        for url, info in data.items():
            urls_info.append({
                "url": url,
                "content_length": info["content_length"],
                "chunks_count": info["chunks_count"],
                "scraped_at": info["scraped_at"],
                "last_accessed": info["last_accessed"]
            })
        
        return {
            "total_urls": len(data),
            "total_content_length": total_length,
            "total_chunks": total_chunks,
            "urls": urls_info
        }
    
    def _load_data(self) -> Dict:
        """Load data from storage file"""
        if not os.path.exists(self.storage_file):
            return {}
            
        try:
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def _save_data(self, data: Dict):
        """Save data to storage file"""
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving data: {e}")

# Global instance
content_store = ContentStore() 