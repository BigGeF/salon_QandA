#!/bin/bash

echo "============================================================"
echo "🌟 Beauty Salon Q&A System 🌟"
echo "AI-powered website analysis and intelligent Q&A"
echo "============================================================"
echo

# Check virtual environment
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run: python -m venv venv"
    exit 1
fi

# Check frontend directory
if [ ! -d "frontend" ]; then
    echo "❌ Frontend directory not found"
    exit 1
fi

# Check backend directory
if [ ! -d "backend" ]; then
    echo "❌ Backend directory not found"
    exit 1
fi

echo "✅ All requirements satisfied"
echo

# Start backend service
echo "🚀 Starting backend service..."
source venv/bin/activate
cd backend
python main.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3
echo "✅ Backend service started on http://localhost:8000"

# Start frontend service
echo "🎨 Starting frontend service..."
cd frontend

# Check node_modules
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

npm start &
FRONTEND_PID=$!
cd ..

# Wait for frontend to start
sleep 5
echo "✅ Frontend service started on http://localhost:3000"

echo
echo "============================================================"
echo "📖 USAGE INSTRUCTIONS"
echo "============================================================"
echo "1. 🌐 Enter a beauty salon website URL"
echo "2. ⏳ Wait for the system to process the website"
echo "3. 💬 Ask questions about the salon"
echo
echo "📍 System URLs:"
echo "   • Main Application: http://localhost:3000"
echo "   • API Documentation: http://localhost:8000/docs"
echo "   • User Guide: file://$(pwd)/instructions.html"
echo
echo "🔧 To stop the system: Press Ctrl+C"
echo "============================================================"

# Open browser
echo "🌐 Opening browser..."
if command -v open &> /dev/null; then
    open http://localhost:3000
elif command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:3000
else
    echo "Please manually open: http://localhost:3000"
fi

echo
echo "🎉 System is running! Press Ctrl+C to stop..."

# Handle user interrupt
trap 'echo -e "\n🛑 Shutting down system..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo "✅ System shutdown complete"; exit 0' INT

# Keep script running
while true; do
    sleep 1
done 