import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from api.routers.countries import router as countries_router
from api.routers.universities import router as universities_router
from api.routers.search import router as search_router
from routers.logo_router import router as logo_router

BASE_DIR = os.path.dirname(__file__)  # path to apps/backend/src
STATIC_DIR = os.path.join(BASE_DIR, "static")

app = FastAPI(title="TOC-country", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.include_router(countries_router)
app.include_router(universities_router)
app.include_router(search_router)
app.include_router(logo_router)

@app.get("/health")
def health():
    return {"status": "ok"}