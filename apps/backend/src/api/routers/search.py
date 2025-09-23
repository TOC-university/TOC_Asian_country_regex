import difflib
from fastapi import APIRouter
from models.search import SearchRequest, SearchResponse
from orchestrators.search import Searcher

router = APIRouter(prefix="/search")
Searcher = Searcher()
@router.post("/suggest", response_model=SearchResponse)
def search(req: SearchRequest):
    if req.rebuild or not getattr(Searcher, "_built_at", None):
        Searcher.build(limit_units=req.limit_units)
    suggestions = Searcher.search(req.q, k = req.k)
    return SearchResponse(query=req.q, suggestions=suggestions, build_at=Searcher._built_at)