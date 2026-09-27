import shutil
from pathlib import Path

import uvicorn
from fastapi import FastAPI, File, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import HOST, PORT
from app.database import init_db
from app.routes.admin import router as admin_router
from app.routes.chat import router as chat_router
from app.routes.health import router as health_router
from app.routes.products import router as products_router
from app.routes.sales import router as sales_router

app = FastAPI(title="ตู้เครื่องเขียนอัตโนมัติ", version="2.0.0")

init_db()

app.include_router(health_router)
app.include_router(products_router)
app.include_router(sales_router)
app.include_router(admin_router)
app.include_router(chat_router)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

IMAGES_DIR = Path("app/static/images")
IMAGES_DIR.mkdir(exist_ok=True)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})


@app.post("/developer/image")
async def upload_developer_image(file: UploadFile = File(...)):
    """อัปโหลดรูปผู้พัฒนา"""
    allowed = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    suffix = Path(file.filename).suffix.lower()
    if suffix not in allowed:
        return JSONResponse(status_code=400, content={"error": "รองรับเฉพาะ jpg, png, gif, webp"})
    dest = IMAGES_DIR / f"developer{suffix}"
    with dest.open("wb") as f:
        shutil.copyfileobj(file.file, f)
    return {"image_url": f"/static/images/developer{suffix}"}


if __name__ == "__main__":
    print(f"\n🖊️  ตู้เครื่องเขียนอัตโนมัติ")
    print(f"   เปิดจากเครื่องนี้ : http://localhost:{PORT}")
    print(f"   เปิดจากเครื่องอื่น: ใช้ IP ของเครื่องนี้ เช่น http://192.168.x.x:{PORT}\n")
    uvicorn.run("app.main:app", host=HOST, port=PORT, reload=True)
