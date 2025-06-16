# 🌟 Beauty Salon Q&A System

An AI-powered web application that analyzes beauty salon websites and provides intelligent Q&A functionality with multi-page content analysis and manual text input capabilities.

## ✨ Features

- **Multi-Page Website Analysis**: Automatically discovers and scrapes multiple pages from beauty salon websites
- **AI-Powered Q&A**: Ask questions about salon services, pricing, location, hours, and policies
- **Manual Text Input**: Add additional information directly to the knowledge base
- **Intelligent Content Processing**: Advanced chunking and vector storage for efficient retrieval
- **Real-time Processing**: Live status updates during website analysis
- **Responsive Design**: Modern web interface that works on desktop and mobile devices

## 🚀 Quick Start

### Prerequisites
- **Python**: 3.8 or higher
- **Node.js**: 14 or higher
- **npm**: 6 or higher
- **OpenAI API Key**: Required for AI functionality

### Installation

1. **Clone the repository**:
   ```bash
   git clone [repository-url]
   cd salon_QandA
   ```

2. **Set up Python environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up frontend dependencies**:
   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. **Configure environment variables**:
   ```bash
   cp env.example .env
   # Edit .env file and add your OpenAI API key:
   # OPENAI_API_KEY=sk-your-openai-api-key-here
   ```

### Running the Application

**Option 1: Use the Shell Script (Recommended)**
```bash
./start.sh
```

**Option 2: Manual Start**
1. **Start Backend** (Terminal 1):
   ```bash
   source venv/bin/activate
   cd backend
   python main.py
   ```

2. **Start Frontend** (Terminal 2):
   ```bash
   cd frontend
   npm start
   ```

3. **Access the Application**:
   - Main Application: http://localhost:3000
   - API Documentation: http://localhost:8000/docs

## 📖 How to Use

### Step 1: Website Analysis
- Enter a beauty salon's website URL in the input field
- The system will automatically discover and analyze multiple pages
- Wait for the "Successfully analyzed X pages" message

### Step 2: Manual Content Addition (Optional)
- Use the "Add Text Content" section to input additional information
- This is useful for adding missing details or supplementary information

### Step 3: Ask Questions
- Use the chat interface to ask questions about the salon
- Examples:
  - "What are your business hours?"
  - "What services do you offer?"
  - "How much does a Swedish massage cost?"
  - "Where are you located?"
  - "How can I make an appointment?"

## 🏗️ Project Structure

```
salon_QandA/
├── backend/                    # Python FastAPI backend
│   ├── main.py                # Main application with API endpoints
│   ├── content_store.py       # Content storage and chunking system
│   ├── data/                  # Data storage directory
│   │   └── scraped_content.json  # Stored website content and chunks
│   └── __pycache__/           # Python cache files
├── frontend/                   # React frontend application
│   ├── src/
│   │   ├── App.js             # Main React component
│   │   └── App.css            # Application styling
│   ├── public/
│   │   └── index.html         # HTML template
│   ├── package.json           # Frontend dependencies
│   └── node_modules/          # Node.js dependencies
├── venv/                      # Python virtual environment
├── .env                       # Environment variables (create from env.example)
├── env.example               # Environment variables template
├── requirements.txt          # Python dependencies
├── start.sh                  # System startup script
├── instructions.html         # Standalone user guide
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

## 🔧 API Endpoints

### Core Endpoints
- **GET** `/` - API health check and information
- **GET** `/health` - Detailed health status with storage statistics
- **POST** `/scrape-website` - Analyze website with multi-page discovery
- **POST** `/add-text` - Add manual text content to knowledge base
- **POST** `/chat` - AI-powered question answering
- **GET** `/scraping-status` - Get current content analysis status

### Utility Endpoints
- **GET** `/storage-stats` - Detailed storage statistics
- **GET** `/content/{url}` - Get stored content for specific URL
- **DELETE** `/reset` - Clear all stored content
- **POST** `/query` - Advanced query with chunk-based retrieval

## 🛠️ Technical Architecture

### Frontend Stack
- **React.js**: Modern component-based UI framework
- **CSS Grid**: Responsive layout system
- **Fetch API**: Backend communication
- **Real-time Updates**: Live status feedback during processing

### Backend Stack
- **FastAPI**: High-performance Python web framework
- **OpenAI API**: GPT-3.5-turbo for natural language processing
- **BeautifulSoup**: HTML parsing and content extraction
- **Custom Content Store**: Advanced chunking and persistence system

### Data Processing
- **Multi-page Discovery**: Automatic internal link detection
- **Content Chunking**: Intelligent text segmentation with overlap
- **Vector Storage**: Efficient content retrieval system
- **Semantic Search**: Keyword-based relevance scoring

### Key Features
- **Intelligent Link Discovery**: Finds and analyzes up to 10 pages per website
- **Content Deduplication**: Prevents duplicate content storage
- **Graceful Error Handling**: Robust error management and recovery
- **Rate Limiting**: Respectful server interaction with delays

## 💡 Usage Tips

### For Best Results
- **Complete URLs**: Always include `http://` or `https://`
- **Accessible Websites**: Ensure websites are publicly accessible
- **Specific Questions**: Ask detailed questions about services, prices, or policies
- **Multiple Sources**: Combine website analysis with manual text input

### Troubleshooting
- **Processing Failed**: Check URL format and website accessibility
- **Incomplete Answers**: Information might not be available on the website
- **Slow Processing**: Large websites take longer to analyze
- **Connection Issues**: Ensure both frontend and backend are running

## 📊 Analysis of App's Capabilities and Limitations

### Capabilities

#### ✅ Strengths
- **Comprehensive Content Analysis**: Multi-page website discovery and analysis
- **Intelligent Q&A**: Context-aware responses using OpenAI GPT-3.5-turbo
- **Flexible Input Methods**: Both automated website scraping and manual text input
- **Advanced Content Processing**: Intelligent chunking with sentence boundary detection
- **Real-time Feedback**: Live updates during processing with detailed statistics
- **Persistent Storage**: Content is saved and can be reused across sessions
- **Scalable Architecture**: Modular design supports easy feature additions
- **User-friendly Interface**: Clean, responsive design with step-by-step guidance

#### 🎯 Technical Achievements
- **Multi-page Discovery**: Automatically finds and analyzes internal website links
- **Content Deduplication**: Prevents storage of duplicate information
- **Semantic Search**: Keyword-based relevance scoring for accurate responses
- **Error Recovery**: Graceful handling of network issues and parsing errors
- **API Integration**: Seamless OpenAI API integration with proper error handling

### Limitations

#### ⚠️ Current Constraints
- **Website Accessibility**: Can only process publicly accessible websites
- **Content Dependency**: Answer quality depends entirely on available source content
- **Processing Time**: Large websites may take 30+ seconds to fully analyze
- **API Dependencies**: Requires stable internet connection for OpenAI API calls
- **Language Optimization**: Primarily optimized for English content
- **Page Limit**: Maximum of 10 pages per website to prevent server overload
- **No Authentication**: Currently lacks user accounts or session management
- **Limited File Types**: Only processes HTML content, not PDFs or documents

#### 🔒 Technical Limitations
- **Simple Keyword Matching**: Uses basic keyword overlap instead of advanced vector embeddings
- **No Caching**: Repeated requests re-process the same content
- **Single Domain**: Cannot analyze multiple websites simultaneously
- **No Real-time Updates**: Website changes require manual re-analysis
- **Memory Usage**: Large websites may consume significant memory during processing

## 🚀 Potential Future Improvements

### Short-term Enhancements (1-3 months)
- **Advanced Vector Embeddings**: Replace keyword matching with semantic vector search
- **Content Caching**: Implement intelligent caching to avoid re-processing
- **Enhanced Error Handling**: Better user feedback for various error scenarios
- **Mobile Optimization**: Improved responsive design for mobile devices
- **Batch Processing**: Allow analysis of multiple websites simultaneously

### Medium-term Features (3-6 months)
- **User Authentication**: Add user accounts with personal content libraries
- **Conversation History**: Save and retrieve previous chat sessions
- **Content Management**: Allow users to edit, delete, and organize stored content
- **Multi-language Support**: Expand language capabilities beyond English
- **Advanced Analytics**: Provide insights on content quality and user interactions

### Long-term Vision (6+ months)
- **Real-time Monitoring**: Automatic detection of website changes and updates
- **Integration APIs**: Connect with booking systems, CRM platforms, and social media
- **Machine Learning**: Custom models trained on beauty industry data
- **Mobile Applications**: Native iOS and Android apps
- **Enterprise Features**: Multi-tenant support, advanced security, and compliance
- **AI Training**: Fine-tuned models specifically for beauty salon interactions

### Technical Improvements
- **Performance Optimization**: Implement async processing and database optimization
- **Microservices Architecture**: Split into smaller, more manageable services
- **Container Deployment**: Docker support for easier deployment and scaling
- **Monitoring and Logging**: Comprehensive application monitoring and error tracking
- **Security Enhancements**: API authentication, rate limiting, and data encryption

### Business Enhancements
- **Industry Expansion**: Adapt for restaurants, hotels, and other service businesses
- **White-label Solutions**: Customizable branding for different clients
- **Analytics Dashboard**: Business intelligence for salon owners
- **Integration Marketplace**: Third-party integrations and plugins
- **Subscription Model**: Tiered pricing with advanced features

## 📝 License

This project is for educational and demonstration purposes.

## 🤝 Contributing

This is an educational project. For suggestions or improvements, please create an issue or submit a pull request.

---

**Built with ❤️ for the beauty industry - Making salon information accessible through AI**