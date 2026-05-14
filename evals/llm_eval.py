from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Awaitable, Callable

from app.chains import UNSUPPORTED_ANSWER, answer_question
from app.config import Settings
from app.models import AskRequest
from app.prompts import SYSTEM_PROMPT


@dataclass(frozen=True)
class EvalResult:
    name: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class RetrievalCase:
    name: str
    question: str
    expected_terms: tuple[str, ...]
    expected_sources: tuple[str, ...] = field(default_factory=tuple)


async def evaluate_retrieval_quality(settings: Settings) -> list[EvalResult]:
    cases = (
        RetrievalCase(
            name="recovery_tradeoff",
            question="What limits higher RO recovery?",
            expected_terms=("recovery", "scaling", "feed"),
            expected_sources=("ro_basics.md",),
        ),
        RetrievalCase(
            name="flux_definition",
            question="What unit is permeate flux expressed in?",
            expected_terms=("flux", "liters", "square", "meter", "hour"),
            expected_sources=("membrane_summary.md",),
        ),
        RetrievalCase(
            name="acronym_expansion",
            question="What is RO?",
            expected_terms=("reverse osmosis",),
            expected_sources=("ro_basics.md",),
        ),
    )

    results: list[EvalResult] = []
    for case in cases:
        response = await answer_question(AskRequest(question=case.question), settings)
        answer = response.answer.lower()
        missing_terms = [term for term in case.expected_terms if term not in answer]
        missing_sources = [source for source in case.expected_sources if source not in response.sources]
        passed = not missing_terms and not missing_sources
        detail = (
            f"answer_terms_missing={missing_terms or 'none'}; "
            f"sources_missing={missing_sources or 'none'}; "
            f"sources={response.sources}"
        )
        results.append(EvalResult(f"retrieval_quality::{case.name}", passed, detail))

    return results


async def evaluate_unsupported_answer_refusal(settings: Settings) -> list[EvalResult]:
    response = await answer_question(AskRequest(question="What is MCDI?"), settings)
    passed = response.answer == UNSUPPORTED_ANSWER and response.sources == []
    return [
        EvalResult(
            "unsupported_answer_refusal::out_of_scope_topic",
            passed,
            f"answer={response.answer!r}; sources={response.sources}",
        )
    ]


async def evaluate_tool_call_contract(settings: Settings) -> list[EvalResult]:
    response = await answer_question(AskRequest(question="What is flux?"), settings)
    response_fields = set(response.model_dump().keys())
    passed = response_fields == {"answer", "sources"}
    return [
        EvalResult(
            "tool_call_correctness::no_external_tool_contract",
            passed,
            f"response_fields={sorted(response_fields)}",
        )
    ]


def evaluate_prompt_regression() -> list[EvalResult]:
    checks = {
        "context_only": "Answer using only the retrieved context provided to you." in SYSTEM_PROMPT,
        "no_outside_knowledge": "Do not use outside knowledge." in SYSTEM_PROMPT,
        "exact_refusal": UNSUPPORTED_ANSWER in SYSTEM_PROMPT,
        "no_guessing": "Do not guess or infer unsupported facts." in SYSTEM_PROMPT,
    }

    return [
        EvalResult(
            f"prompt_regression::{name}",
            passed,
            f"required_prompt_clause_present={passed}",
        )
        for name, passed in checks.items()
    ]


async def run_evals() -> list[EvalResult]:
    settings = Settings(OPENAI_API_KEY=None)
    async_suites: tuple[Callable[[Settings], Awaitable[list[EvalResult]]], ...] = (
        evaluate_retrieval_quality,
        evaluate_unsupported_answer_refusal,
        evaluate_tool_call_contract,
    )

    results: list[EvalResult] = []
    for suite in async_suites:
        results.extend(await suite(settings))
    results.extend(evaluate_prompt_regression())
    return results


def print_results(results: list[EvalResult]) -> None:
    for result in results:
        status = "PASS" if result.passed else "FAIL"
        print(f"{status} {result.name} - {result.detail}")

    passed = sum(result.passed for result in results)
    total = len(results)
    print(f"\n{passed}/{total} evals passed")


def main() -> int:
    results = asyncio.run(run_evals())
    print_results(results)
    return 0 if all(result.passed for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
