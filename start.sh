#!/bin/bash
set -e

# Start backend (FastAPI)
uvicorn backend:app --host 0.0.0.0 --port 8000 &

# Start Streamlit (Frontend)
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
