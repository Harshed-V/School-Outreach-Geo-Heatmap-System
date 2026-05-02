#!/bin/bash
# Quick startup script for development

echo "🚀 Starting School Outreach Geo-Heatmap System (Development)"
echo "=============================================================="

# Check if backend is running
echo ""
echo "Starting Backend (Python)..."
cd backend
python app.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 2

# Test backend
echo ""
echo "Testing Backend..."
python quick_test.py

# Check if frontend should be started
echo ""
echo "=============================================================="
echo "Backend is running at http://localhost:5000"
echo "To start frontend in another terminal:"
echo "  cd frontend"
echo "  npm run dev"
echo ""
echo "Then open http://localhost:5173"
echo "=============================================================="
echo ""

# Keep script running
wait $BACKEND_PID
