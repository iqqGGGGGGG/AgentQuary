import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import examples, generate, report

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

app = FastAPI(title="知识闯关 API", version="1.0.0")

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


@app.get("/")
async def root():
    return {"message": "知识闯关 API is running"}
