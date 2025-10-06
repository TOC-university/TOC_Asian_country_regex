from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from orchestrators.logo_crawler import get_logo_for
import os

router = APIRouter()

@router.get("/logo")
async def get_logo_info(name: str):
    path = await get_logo_for(name)
    if not path:
        raise HTTPException(status_code=404, detail="Logo not found")
    filename = os.path.basename(path)
    return {"name": name, "logo_url": f"/static/logos/{filename}"}


@router.get("/logo/image")
async def get_logo_image(name: str):
    path = await get_logo_for(name)
    if not path:
        raise HTTPException(status_code=404, detail="Logo not found")
    return FileResponse(path, media_type="image/png")