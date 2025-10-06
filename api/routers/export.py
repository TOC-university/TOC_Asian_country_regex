from fastapi import APIRouter, HTTPException, Query as Q
import csv
import io
from fastapi.responses import StreamingResponse
from orchestrators.crawler import crawl_university_detail as crawl_university_detail_orch, crawl_universities as crawl_universities_orch
from orchestrators.search import Searcher
searcher = Searcher()
import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/export", tags=["csv"])

@router.get("/all_universities", response_class=StreamingResponse)
def export_all_university_detail():
    try:
        universities = crawl_universities_orch()
        if not universities:
            raise HTTPException(status_code=404, detail="No universities found")

        # Create a CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Name", "Abbreviation", "Country", "Path", "Established", "Location", "Campuses", "Website", "Faculties"])  # Write header

        for uni in universities:
            detail = crawl_university_detail_orch(uni.path)
            writer.writerow([uni.name, 
                             uni.abbreviation, 
                             uni.country,
                            uni.path,
                            detail.get('estab', 'N/A'),
                            detail.get('location', 'N/A'),
                            "; ".join(detail.get('campuses', [])) if detail.get('campuses') else 'N/A',
                            detail.get('website', 'N/A'),
                            "; ".join(detail.get('faculties', [])) if detail.get('faculties') else 'N/A',
                             ])

            yield output.getvalue()
            output.seek(0)
            output.truncate(0)
        return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=universities.csv"})

    except Exception as e:
        logger.error(f"Error exporting universities: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/all_universities_pagination", response_class=StreamingResponse)
def export_all_university_pagination(
    page: int = Q(1, ge=1),
    page_size: int = Q(100, ge=1, le=500)
):
    try:
        universities = crawl_universities_orch()
        if not universities:
            raise HTTPException(status_code=404, detail="No universities found")

        start = (page - 1) * page_size
        end = start + page_size
        total = len(universities)
        if start >= total:
            raise HTTPException(status_code=404, detail="Page out of range")
        paginated_universities = universities[start:end]
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Name", "Abbreviation", "Country", "Path", "Established", "Location", "Campuses", "Website", "Faculties"])  # Write header

        for uni in paginated_universities:
            detail = crawl_university_detail_orch(uni.path)
            writer.writerow([uni.name, 
                             uni.abbreviation, 
                             uni.country,
                            uni.path,
                            detail.get('estab', 'N/A'),
                            detail.get('location', 'N/A'),
                            "; ".join(detail.get('campuses', [])) if detail.get('campuses') else 'N/A',
                            detail.get('website', 'N/A'),
                            "; ".join(detail.get('faculties', [])) if detail.get('faculties') else 'N/A',
                             ])

            yield output.getvalue()
            output.seek(0)
            output.truncate(0)
        return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=universities.csv"})

    except Exception as e:
        logger.error(f"Error exporting universities: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/universities")
def export_university_detail(name: str):
    # ดึงข้อมูลเฉพาะมหาลัยนี้
    detail = crawl_university_detail_orch(name)

    def generate():
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Name", "Abbreviation", "Country", "Path",
                         "Established", "Location", "Campuses", "Website", "Faculties"])
        writer.writerow([
            detail.get("name", "N/A"),
            detail.get("abbr", "N/A"),
            detail.get("country", "N/A"),
            name,
            detail.get("estab", "N/A"),
            detail.get("location", "N/A"),
            "; ".join(detail.get("campuses", [])) if detail.get("campuses") else "N/A",
            detail.get("website", "N/A"),
            "; ".join(detail.get("faculties", [])) if detail.get("faculties") else "N/A",
        ])
        yield output.getvalue()

    return StreamingResponse(
        generate(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={name}_detail.csv"}
    )

@router.get("/search")
def export_search_suggestions(q: str, k: int = 10):
    try:
        if not getattr(searcher, "_built_at", None):
            searcher.build()
        suggestions = searcher.search(q, k=k)

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

