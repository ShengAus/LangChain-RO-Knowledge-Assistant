from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import re

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI

from app.config import Settings
from app.models import AskRequest, AssistantResponse, LLMAnswerPayload
from app.prompts import build_answer_prompt


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
QUERY_EXPANSIONS = {
    "ro": "reverse osmosis",
}
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "be",
    "by",
    "for",
    "from",
    "how",
    "in",
    "influence",
    "influences",
    "is",
    "note",
    "of",
    "on",
    "or",
    "operating",
    "summarize",
    "tell",
    "that",
    "the",
    "this",
    "to",
    "what",
    "which",
}
UNSUPPORTED_ANSWER = "I cannot answer from the provided local documents."


def _expand_query(text: str) -> str:
    expanded_text = text
    for term, expansion in QUERY_EXPANSIONS.items():
        expanded_text = re.sub(rf"\b{re.escape(term)}\b", expansion, expanded_text, flags=re.IGNORECASE)
    return expanded_text


@lru_cache(maxsize=1)
def get_chunks() -> tuple[Document, ...]:
    loader = DirectoryLoader(
        str(DATA_DIR),
        glob="*.md",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
        show_progress=False,
    )
    documents = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=100)
    chunks = splitter.split_documents(documents)
    return tuple(chunks)


def _format_context(documents: list[Document]) -> str:
    if not documents:
        return "No local documents matched this question."
    return "\n\n".join(document.page_content.strip() for document in documents)


def _extract_sources(documents: list[Document]) -> list[str]:
    sources: list[str] = []
    for document in documents:
        source = Path(document.metadata.get("source", "")).name
        if source and source not in sources:
            sources.append(source)
    return sources


def _tokenize(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-zA-Z0-9]+", text.lower())
        if len(token) >= 2 and token not in STOPWORDS
    }


def _has_grounding(question: str, documents: list[Document]) -> bool:
    question_terms = _tokenize(question)
    if not question_terms:
        return False

    context_terms = _tokenize(" ".join(document.page_content for document in documents))
    return bool(question_terms & context_terms)


def _retrieve_documents(question: str, limit: int = 3) -> list[Document]:
    question_terms = _tokenize(question)
    if not question_terms:
        return []

    scored_chunks: list[tuple[int, int, Document]] = []
    for chunk in get_chunks():
        overlap = question_terms & _tokenize(chunk.page_content)
        if overlap:
            scored_chunks.append((len(overlap), len(chunk.page_content), chunk))

    scored_chunks.sort(key=lambda item: (item[0], item[1]), reverse=True)
    return [chunk for _, _, chunk in scored_chunks[:limit]]


def _select_best_context_paragraph(question: str, context: str) -> str:
    paragraphs = [paragraph.strip() for paragraph in context.split("\n\n") if paragraph.strip()]
    if not paragraphs:
        return context.strip()

    content_paragraphs = [paragraph for paragraph in paragraphs if not paragraph.startswith("#")]
    if content_paragraphs:
        paragraphs = content_paragraphs

    question_terms = _tokenize(question)
    if not question_terms:
        return paragraphs[0]

    def score(paragraph: str) -> tuple[int, int]:
        overlap = question_terms & _tokenize(paragraph)
        return (len(overlap), len(paragraph))

    return max(paragraphs, key=score)


async def _generate_llm_answer(
    *,
    question: str,
    context: str,
    settings: Settings,
) -> LLMAnswerPayload:
    llm = ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
        temperature=0,
    )
    chain = build_answer_prompt() | llm.with_structured_output(LLMAnswerPayload)
    return await chain.ainvoke(
        {
            "question": question,
            "context": context,
        }
    )


def _build_fallback_answer(
    question: str,
    context: str,
    *,
    scoring_question: str | None = None,
) -> LLMAnswerPayload:
    if context and context != "No local documents matched this question.":
        best_paragraph = _select_best_context_paragraph(scoring_question or question, context)
        return LLMAnswerPayload(
            answer=f"For the question '{question}', the local notes say: {best_paragraph}"
        )

    return LLMAnswerPayload(
        answer=(
            f"No supporting local context was found for: {question}. "
            "Add more markdown notes or configure the LLM to improve the answer."
        )
    )


async def answer_question(request: AskRequest, settings: Settings) -> AssistantResponse:
    retrieval_question = _expand_query(request.question)
    documents = _retrieve_documents(retrieval_question)
    if not _has_grounding(retrieval_question, documents):
        return AssistantResponse(answer=UNSUPPORTED_ANSWER, sources=[])

    context = _format_context(documents)
    sources = _extract_sources(documents)

    if settings.llm_enabled:
        llm_payload = await _generate_llm_answer(
            question=request.question,
            context=context,
            settings=settings,
        )
    else:
        llm_payload = _build_fallback_answer(
            request.question,
            context,
            scoring_question=retrieval_question,
        )

    return AssistantResponse(answer=llm_payload.answer, sources=sources)
