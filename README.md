# LangChain RO Knowledge Assistant

LangChain RO Knowledge Assistant is a lightweight FastAPI application for answering reverse osmosis questions from a small local document set.

The project combines LangChain retrieval, an OpenAI-compatible chat model, and a simple browser interface. It is designed as a small, public-safe prototype that demonstrates grounded question answering over local technical notes rather than broad open-domain answering.

## Screenshots

### Browser Interface

![Browser interface](IMG/use_case1.png)

### Out-of-Scope Refusal

The app is designed to reject questions that are not supported by the local documents.

![Unsupported question refusal](IMG/fail_case.png)

## What This Project Demonstrates

- FastAPI backend with a browser UI served at `/`
- LangChain-based retrieval over local markdown files
- Pydantic request and response models
- OpenAI-compatible LLM integration through `.env`
- Grounding checks that reject unsupported questions
- A fallback mode when no API key is configured

## How It Works

The application uses one FastAPI service.

1. The user opens `/` in the browser or sends a request to `POST /ask`.
2. The app loads markdown files from `data/` and splits them into chunks.
3. A BM25 retriever selects the most relevant chunks for the question.
4. A grounding check verifies that the retrieved content meaningfully overlaps with the question.
5. If the question is not supported by the local notes, the app returns:
   `I cannot answer from the provided local documents.`
6. If the question is supported and `OPENAI_API_KEY` is configured, the app sends the retrieved context to the LLM.
7. If no API key is configured, the app returns a fallback answer built directly from the retrieved notes.
8. The final response includes the answer and the supporting source files.

## Why The Refusal Behavior Matters

A normal LLM may answer from its general training knowledge even when the local documents do not contain the answer. This project explicitly guards against that behavior.

For example, asking a question such as "What is today's weather?" or another topic outside the RO notes should not produce a confident answer from model memory. Instead, the app refuses to answer unless the retrieved local content supports the question.

This is useful for demonstrating prompt design and grounding behavior in a small RAG-style application.

## Project Structure

```text
LangChain-RO-Knowledge-Assistant/
├── app/
│   ├── chains.py       # Retrieval, grounding checks, and answer orchestration
│   ├── config.py       # Settings loaded from .env
│   ├── main.py         # FastAPI entrypoint and UI route
│   ├── models.py       # Pydantic schemas
│   ├── prompts.py      # Prompt template for LLM mode
│   └── static/
│       └── index.html  # Browser interface
├── data/
│   ├── glossary.md
│   ├── membrane_summary.md
│   ├── ro_basics.md
│   └── ro_design_notes.md
├── IMG/
│   ├── use_case1.png
│   └── fail_case.png
├── tests/
│   └── test_assistant.py
├── .env.example
├── requirements.txt
+└── README.md
```

## Setup

### Windows PowerShell

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

## Environment Variables

Configuration is loaded from `.env`.

Example:

```env
OPENAI_API_KEY=your-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
APP_HOST=127.0.0.1
APP_PORT=8000
```

`OPENAI_API_KEY` is optional.

- If it is set, the app uses the LLM to generate the final answer from retrieved context.
- If it is missing, the app still works and returns a fallback answer built from the local notes.

## Run The App

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Then open the browser interface at:

`http://127.0.0.1:8000/`

## API Endpoints

- `GET /`
  Serves the browser UI.
- `GET /health`
  Returns a simple health response.
- `POST /ask`
  Accepts a question and returns an answer plus sources.

### Example Request

```json
{
  "question": "What affects RO recovery?"
}
```

### Example Response

```json
{
  "answer": "RO recovery is affected by several factors including feed water quality, fouling potential, scaling risk, hydraulic limits, and operating conditions.",
  "sources": ["ro_design_notes.md", "ro_basics.md"]
}
```

### Example PowerShell Request

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/ask -ContentType 'application/json' -Body '{
  "question": "What affects RO recovery?"
}' | ConvertTo-Json -Depth 5
```

## Retrieval And Grounding Design

The retrieval layer is intentionally simple.

- Documents are loaded from `data/`
- Text is split with overlap using a recursive character splitter
- BM25 ranks chunks by lexical relevance
- A grounding check compares question terms with retrieved content
- Unsupported questions are rejected before the answer is generated

This keeps the app small and easy to explain while still demonstrating a grounded QA workflow.

## Testing

Run the assistant tests with:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_assistant.py
```

## Limitations

- Retrieval is based on a very small local markdown corpus.
- BM25 retrieval is lexical, not embedding-based semantic retrieval.
- The grounding gate is intentionally simple and conservative.
- The project is a prototype for local demonstration, not a production system.
- Answer quality depends on the coverage and wording of the local documents.

## Resume-Safe Description

Built a lightweight LangChain-based assistant for reverse osmosis documentation, combining retrieval over local technical notes with a FastAPI service, a browser interface, structured Pydantic responses, and prompt-based refusal for unsupported questions.
