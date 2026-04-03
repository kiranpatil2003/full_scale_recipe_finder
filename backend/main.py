# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from core.config import settings
from core.firebase import initialize_firebase
from routers import auth, recipes, categories, favorites, user


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup."""
    initialize_firebase()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="A well-organized Recipe Finder API with Firebase authentication.",
    lifespan=lifespan,
)

# CORS — allow requests from any origin (for Flutter app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(auth.router)
app.include_router(recipes.router)
app.include_router(categories.router)
app.include_router(favorites.router)
app.include_router(user.router)


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to the Recipe Finder API! 🍳",
        "docs": "/docs",
        "version": settings.APP_VERSION,
    }
