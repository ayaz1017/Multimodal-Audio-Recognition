"""Vercel Serverless entrypoint.

Vercel looks for Serverless Functions under the `api/` directory.
We re-export the existing Flask app from backend/app.py.
"""

from backend.app import app  # noqa: F401
