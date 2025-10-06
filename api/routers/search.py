import difflib
from fastapi import APIRouter
from models.search import SearchRequest, SearchResponse, PaginatedSearchRequest, PaginatedSearchResponse
from orchestrators.search import Searcher

router = APIRouter(prefix="/search")
Searcher = Searcher()
@router.post("/suggest", response_model=SearchResponse)
def search(req: SearchRequest):
    if req.rebuild or not getattr(Searcher, "_built_at", None):
        Searcher.build(limit_units=req.limit_units, countries=req.countries)
    suggestions = Searcher.search(req.q, k = req.k)
    return SearchResponse(query=req.q, suggestions=suggestions, build_at=Searcher._built_at)

@router.post("/paginated-searach", response_model=PaginatedSearchResponse)
def paginated_search(req: PaginatedSearchRequest):
    if req.rebuild or not getattr(Searcher, "_built_at", None):
        Searcher.build(limit_units=req.limit_units, countries=req.countries)
    suggestions = Searcher.paginated_search(query=req.q, page=req.page, limit=req.limit)
    return PaginatedSearchResponse(query=req.q, suggestions=suggestions["results"], total=suggestions["total"], page=suggestions["page"], limit=suggestions["limit"], total_pages=suggestions["total_pages"], built_at=Searcher._built_at)