"""
AI Multi-Disease Risk Prediction ML Service
FastAPI application package exposing the 'app' instance for uvicorn.

Run with:
    uvicorn app:app --host 0.0.0.0 --port 8000 --reload
or use the convenience script:
    python run.py
"""

from .main import app  # noqa: F401 - exported for 'uvicorn app:app'

__all__ = ["app"]
