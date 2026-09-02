from fastapi.middleware.cors import CORSMiddleware

from .config import settings


def setup_cors(app):
    # Local origins for development
    allowed_origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://localhost:8000",
    ]

    # Add configurable frontend URL from settings if available
    frontend_url = getattr(settings, "FRONTEND_URL", None)
    if frontend_url:
        allowed_origins.append(frontend_url)

    # Regex for preview branches (Vercel and Netlify)
    # Matches *.vercel.app and *.netlify.app
    allow_origin_regex = r"^https:\/\/.*(\.vercel\.app|\.netlify\.app)$"

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_origin_regex=allow_origin_regex,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization", "X-Requested-With", "Accept"],
        expose_headers=["Content-Length", "X-Response-Time"],
        max_age=86400, # Cache preflight responses for 24 hours
    )
