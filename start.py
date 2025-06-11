#!/usr/bin/env python3
"""
AI Chat Assistant Startup Script
"""

import os
import sys
import subprocess
import threading
import time
import webbrowser

def print_banner():
    print("=" * 60)
    print("🤖 AI Chat Assistant")
    print("=" * 60)
    print("📱 Frontend: http://localhost:3000")
    print("🚀 Backend: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("=" * 60)

def install_backend_deps():
    """Install backend dependencies"""
    print("📦 Checking backend dependencies...")
    os.chdir("backend")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
    os.chdir("..")

def start_backend():
    """Start backend service"""
    print("🚀 Starting backend service...")
    os.chdir("backend")
    subprocess.run([sys.executable, "main.py"])

def start_frontend():
    """Start frontend service"""
    print("🎨 Starting frontend service...")
    os.chdir("frontend")
    subprocess.run(["npm", "start"])

def main():
    print_banner()
    
    try:
        # Install backend dependencies
        install_backend_deps()
        
        # Start backend (in new thread)
        backend_thread = threading.Thread(target=start_backend, daemon=True)
        backend_thread.start()
        
        # Wait for backend to start
        time.sleep(3)
        
        # Auto open browser
        webbrowser.open("http://localhost:3000")
        
        # Start frontend
        start_frontend()
        
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Startup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 