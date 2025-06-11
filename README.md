# AI Chat Application

## Project Overview

This is a simple AI chat application built for a university assignment. The application allows users to chat with an AI powered by OpenAI's GPT model.

**Components:**
- Backend: Python FastAPI server
- Frontend: HTML/CSS/JavaScript webpage
- AI Integration: OpenAI GPT-3.5-turbo

## Files Structure

```
salon_QandA/
├── backend/main.py          # Backend server code
├── index.html              # Frontend chat interface
├── start.py                # Startup script
├── test_backend.py         # Backend testing
├── .env                    # API key configuration
└── README.md              # This file
```

## Setup Instructions

### 1. Get OpenAI API Key
1. Go to https://openai.com/
2. Sign up and get an API key
3. Create a `.env` file in the project root
4. Add your API key: `OPENAI_API_KEY=your_api_key_here`

### 2. Install Dependencies
```bash
pip install fastapi uvicorn openai python-dotenv
```

## How to Run

### Method 1: Use the startup script
```bash
python start.py
```

### Method 2: Manual startup
1. Start the backend server:
```bash
cd backend
python -m uvicorn main:app --host localhost --port 8000
```

2. Start the frontend (in another terminal):
```bash
python3 -m http.server 3000
```

3. Open your browser and go to:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

## Usage

1. Open the chat interface in your browser
2. Type your message in the input field
3. Click "Send" or press Enter
4. The AI will respond to your message

## Notes

- Make sure your `.env` file contains a valid OpenAI API key
- The backend runs on port 8000
- The frontend runs on port 3000
- Both services need to be running for the chat to work 