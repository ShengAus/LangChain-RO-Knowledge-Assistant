# LLM Evaluation Harness

This folder contains a lightweight, deterministic evaluation harness for the RO knowledge assistant.

Run it from the repository root:

```powershell
python -m evals.llm_eval
```

The suite runs without an API key so it can be used in CI and portfolio reviews without network access.

## Coverage

- **Retrieval quality:** verifies representative RO questions return expected answer terms and source files.
- **Unsupported-answer refusal:** verifies out-of-scope questions return the exact refusal response and no sources.
- **Tool-call correctness:** captures the current contract that the assistant exposes no external tool calls and returns only `answer` and `sources`.
- **Prompt regression:** verifies the prompt still requires retrieved-context-only answering, exact refusal, and no unsupported guessing.

These evals are intentionally small. They provide evidence of evaluation methodology and runtime controls without overstating this prototype as a full enterprise agent platform.
