from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.auth import get_username_from_token
from src.routers.upload import router as upload_router
from src.routers.files import router as files_router
from src.routers.delete import router as delete_router
from src.routers.update import router as update_router
from src.routers.query import router as query_router
from src.routers.download import router as download_router
from src.routers.rename import router as rename_router
from src.routers.auth import router as auth_router


app = FastAPI(
    title="PDF Chat API",
    description="Upload PDFs and Ask Questions",
    version="1.0.0"
)


app.include_router(upload_router)
app.include_router(files_router)
app.include_router(delete_router)
app.include_router(update_router)
app.include_router(query_router)
app.include_router(download_router)
app.include_router(rename_router)
app.include_router(auth_router)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def home(request: Request):
    token = request.cookies.get("session_token")
    username = get_username_from_token(token)

    if not username:
        return FileResponse("static/login.html")

    return FileResponse("static/index.html")


@app.get("/login")
def login_page():
    return FileResponse("static/login.html")

@app.get("/verify")
def verify_page():
    return FileResponse("static/verify.html")
