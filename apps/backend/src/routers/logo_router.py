from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from services.logo_crawler import get_logo_for
import os

router = APIRouter()

@router.get("/logo")
async def get_logo_info(name: str):
    """
    คืนเป็น JSON { name, logo_url } เพื่อให้ Swagger/ลูกค้าเห็น URL ของไฟล์
    """
    path = await get_logo_for(name)
    if not path:
        raise HTTPException(status_code=404, detail="Logo not found")
    filename = os.path.basename(path)
    return {"name": name, "logo_url": f"/static/logos/{filename}"}

@router.get("/logo/image")
async def get_logo_image(name: str):
    """
    ถ้าต้องการ endpoint คืนรูปโดยตรง
    """
    path = await get_logo_for(name)
    if not path:
        raise HTTPException(status_code=404, detail="Logo not found")
    return FileResponse(path, media_type="image/png")
