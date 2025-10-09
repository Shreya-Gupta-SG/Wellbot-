#!/bin/bash
# Start FastAPI backend in background
uvicorn backend:app --host 0.0.0.0 --port 8000 &

# Wait a moment to ensure backend starts
sleep 5

# Start Streamlit frontend (will run on Render's $PORT)
streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
