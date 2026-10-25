"""
AI Multi-Disease Risk Prediction — ML Service Startup Script
Launches the FastAPI app using uvicorn on port 8000.

Usage:
    python run.py               # Development (auto-reload on code changes)
    python run.py --prod        # Production mode (no reload, multi-workers)

Ensure you have installed dependencies first:
    pip install -r requirements.txt
"""

import sys
import uvicorn

if __name__ == "__main__":
    prod_mode = "--prod" in sys.argv

    if prod_mode:
        print("Starting ML service in PRODUCTION mode (port 8000, 4 workers)...")
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            workers=4,
            log_level="info",
        )
    else:
        print("Starting ML service in DEVELOPMENT mode (port 8000, auto-reload enabled)...")
        print("API docs available at: http://127.0.0.1:8000/docs")
        print("Health check:          http://127.0.0.1:8000/health")
        uvicorn.run(
            "app.main:app",
            host="127.0.0.1",
            port=8000,
            reload=True,
            log_level="info",
        )
