import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routers import examples, generate, report, auth, user, documents
from database import init_db
from auth import validate_auth_settings
from config import settings

if settings.dev_mode:
    os.environ["LANGCHAIN_VERBOSE"] = "true"
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
else:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    validate_auth_settings()
    await init_db()
    yield


app = FastAPI(title="知识闯关 API", version="2.0.0", lifespan=lifespan)
uploads_dir = Path(__file__).resolve().parent / "uploads"
uploads_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(examples.router)
app.include_router(generate.router)
app.include_router(report.router)
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(documents.router)


@app.get("/")
async def root():
    return {"message": "知识闯关 API is running"}
