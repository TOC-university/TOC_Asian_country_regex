from fastapi import FastAPI
from api.routers.countries import router as countries_router
from api.routers.universities import router as universities_router
from api.routers.search import router as search_router
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
# from config import PROJECT_NAME, VERSION

# app = FastAPI(title=PROJECT_NAME, version=VERSION)
app = FastAPI(title="TOC-country", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.include_router(countries_router)
app.include_router(universities_router)
app.include_router(search_router)

@app.get("/health")
def health():
    return {"status": "ok"}