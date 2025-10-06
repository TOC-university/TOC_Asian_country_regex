from fastapi import APIRouter, HTTPException, Query as Q
import csv
import io
from fastapi.responses import StreamingResponse
from orchestrators.crawler import crawl_university_detail as crawl_university_detail_orch, crawl_universities_name as crawl_universities_orch
from .search import Searcher as SSearcher
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/export", tags=["csv"])

@router.get("/all_universities", response_class=StreamingResponse)
def export_all_university_detail():
    try:
        if not getattr(SSearcher, "_built_at", None):
            SSearcher.build()

        def generate():
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["Name", "Abbreviation", "Country", "Path", "Established", "Location", "Campuses", "Website", "Faculties"])  # Write header

            for uni in SSearcher._phrases:
                if not (uni.path and uni.established and uni.location and uni.website and (uni.campuses or uni.campuses == []) and (uni.faculties or uni.faculties == [])):
                    ud = crawl_university_detail_orch(uni.path)
                    uni.abbreviation, uni.established, uni.location, uni.website, uni.campuses, uni.faculties = ud["abbr"], ud["estab"], ud["location"], ud["website"], ud["campuses"], ud["faculties"]
                writer.writerow([uni.name, 
                                uni.abbreviation, 
                                uni.country,
                                uni.path,
                                uni.established,
                                uni.location,
                                "; ".join(uni.campuses) if uni.campuses else 'N/A',
                                uni.website,
                                "; ".join(uni.faculties) if uni.faculties else 'N/A',
                                ])

                yield output.getvalue()
                output.seek(0)
                output.truncate(0)
        return StreamingResponse(generate(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=universities.csv"})

    except Exception as e:
        logger.error(f"Error exporting universities: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/all_universities_pagination", response_class=StreamingResponse)
def export_all_university_pagination(
    page: int = Q(1, ge=1),
    page_size: int = Q(100, ge=1, le=500)
):
    try:
        if not getattr(SSearcher, "_built_at", None):
            SSearcher.build()

        start = (page - 1) * page_size
        end = start + page_size
        total = len(SSearcher._phrases)
        if start >= total:
            raise HTTPException(status_code=404, detail="Page out of range")
        paginated_universities = SSearcher._phrases[start:end]
        def generate():
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["Name", "Abbreviation", "Country", "Path", "Established", "Location", "Campuses", "Website", "Faculties"])  # Write header

            for uni in paginated_universities:
                if not (uni.path and uni.established and uni.location and uni.website and (uni.campuses or uni.campuses == []) and (uni.faculties or uni.faculties == [])):
                    ud = crawl_university_detail_orch(uni.path)
                    uni.abbreviation, uni.established, uni.location, uni.website, uni.campuses, uni.faculties = ud["abbr"], ud["estab"], ud["location"], ud["website"], ud["campuses"], ud["faculties"]
                writer.writerow([uni.name, 
                                uni.abbreviation, 
                                uni.country,
                                uni.path,
                                uni.established,
                                uni.location,
                                "; ".join(uni.campuses) if uni.campuses else 'N/A',
                                uni.website,
                                "; ".join(uni.faculties) if uni.faculties else 'N/A',
                                ])

                yield output.getvalue()
                output.seek(0)
                output.truncate(0)
        return StreamingResponse(generate(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=universities.csv"})

    except Exception as e:
        logger.error(f"Error exporting universities: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/search")
def export_search_suggestions(q: str, k: int = 10):
    try:
        if not getattr(SSearcher, "_built_at", None):
            SSearcher.build()
        suggestions = SSearcher.search(q, k=k)

        def generate():
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["Query", "Name", "Abbreviation", "Country", "Path"])
            yield output.getvalue()
            output.seek(0)
            for suggestion in suggestions:
                writer.writerow([q, suggestion.name, getattr(suggestion, "abbreviation", "N/A"), getattr(suggestion, "country", "N/A"), suggestion.path])
            yield output.getvalue()
            output.seek(0)
            output.truncate(0)

        return StreamingResponse(
            generate(),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=search_suggestions.csv"}
        )
    except Exception as e:
        logger.error(f"Error exporting search suggestions: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

