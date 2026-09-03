"""
Vercel serverless entry point.

Vercel's Python runtime looks for a WSGI-compatible callable named
`app` in this file. Every request to the site (aside from static
files, which vercel.json routes separately) gets forwarded here and
handled by Django exactly like it would be by gunicorn on any other
host.
"""

import os
import sys
from pathlib import Path

# make the project root (one level up from /api) importable
sys.path.append(str(Path(__file__).resolve().parent.parent))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

from django.core.wsgi import get_wsgi_application  # noqa: E402

app = get_wsgi_application()
