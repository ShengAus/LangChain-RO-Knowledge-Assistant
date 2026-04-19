from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from app.chains import answer_question
from app.config import get_settings
from app.models import AskRequest, AssistantResponse


app = FastAPI(
    title="LangChain RO Knowledge Assistant",
    description="Prototype assistant for reverse osmosis notes and question answering.",
    version="0.1.0",
)

STATIC_DIR = Path(__file__).resolve().parent / "static"
INDEX_FILE = STATIC_DIR / "index.html"


@app.get("/", response_class=FileResponse)
async def serve_index() -> FileResponse:
    return FileResponse(INDEX_FILE)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/ask", response_model=AssistantResponse)
async def ask_question(request: AskRequest) -> AssistantResponse:
    settings = get_settings()
    return await answer_question(request, settings)
