import pytest

from app.chains import answer_question
from app.config import Settings
from app.models import AskRequest


@pytest.mark.anyio
async def test_answer_question_returns_retrieved_sources_without_llm() -> None:
    settings = Settings(OPENAI_API_KEY=None)

    response = await answer_question(AskRequest(question="What affects RO recovery?"), settings)

    assert "recovery" in response.answer.lower()
    assert response.sources


@pytest.mark.anyio
async def test_answer_question_returns_sources_for_flux_topic() -> None:
    settings = Settings(OPENAI_API_KEY=None)

    response = await answer_question(AskRequest(question="What is flux?"), settings)

    assert "flux" in response.answer.lower()
    assert response.sources


@pytest.mark.anyio
async def test_answer_question_returns_sources_for_ro_acronym_question() -> None:
    settings = Settings(OPENAI_API_KEY=None)

    response = await answer_question(AskRequest(question="What is RO?"), settings)

    assert "reverse osmosis" in response.answer.lower()
    assert response.sources


@pytest.mark.anyio
async def test_answer_question_rejects_unsupported_topic() -> None:
    settings = Settings(OPENAI_API_KEY=None)

    response = await answer_question(AskRequest(question="What is MCDI?"), settings)

    assert response.answer == "I cannot answer from the provided local documents."
    assert response.sources == []
