# LangChain RO Knowledge Assistant — Minimal Project Plan

## Goal
Build a **small, public-safe, RO-relevant LLM project** that demonstrates:
- **LangChain**
- **LLM API integration**
- **FastAPI**
- **structured outputs with Pydantic**
- lightweight retrieval over local documents

This project should be general enough for a public resume, while still feeling natural next to your reverse osmosis background.

## Recommended Project Title
**LangChain RO Knowledge Assistant**

Alternative safe titles:
- **RO Operations Knowledge Assistant**
- **LangChain-Based RO Documentation Assistant**
- **RO Knowledge QA Assistant**

## Public-Safe Project Positioning
This project is a general assistant for reverse osmosis documentation and knowledge questions.

It should:
1. answer questions over a small set of local RO-related documents
2. return structured responses
3. expose a simple FastAPI endpoint

## Minimal Use Case
A user asks questions like:
- "What factors affect RO recovery?"
- "Summarize the design assumptions in this note."
- "What is permeate flux?"
- "What operating factors influence membrane performance?"

The assistant should retrieve relevant information from local docs, generate a grounded answer, and return sources.

## Minimum Scope
1. Local document retrieval over 3 to 5 markdown files.
2. LangChain workflow for loading, chunking, retrieval, and answer generation.
3. Structured output with `answer` and `sources`.
4. One FastAPI endpoint: `POST /ask`.

## Minimal Repo Structure
```text
langchain-ro-knowledge-assistant/
├── app/
│   ├── main.py
│   ├── chains.py
│   ├── models.py
│   ├── prompts.py
│   └── config.py
├── data/
│   ├── ro_basics.md
│   ├── ro_design_notes.md
│   ├── membrane_summary.md
│   └── glossary.md
├── tests/
│   └── test_assistant.py
├── requirements.txt
├── README.md
└── .env.example
```

## Dependencies
- `fastapi`
- `uvicorn`
- `pydantic`
- `pydantic-settings`
- `python-dotenv`
- `langchain`
- `langchain-openai`
- `langchain-community`
- `rank-bm25`
- `pytest`

## Suggested Resume-Safe Description
Built a lightweight LangChain-based assistant for reverse osmosis documentation, combining retrieval over local technical notes with a FastAPI service and structured responses validated by Pydantic.

## Success Criteria
- a working LangChain retrieval workflow
- a FastAPI endpoint returning structured responses
- at least one RO document-based answer
- a clean README and repo structure
