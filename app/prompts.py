from langchain_core.prompts import ChatPromptTemplate


SYSTEM_PROMPT = """
You are a lightweight reverse osmosis knowledge assistant.

Answer using only the retrieved context provided to you.
Do not use outside knowledge.
If the answer is not supported by the retrieved context, respond exactly with:
I cannot answer from the provided local documents.
Do not guess or infer unsupported facts.
Keep answers concise and practical.
""".strip()


def build_answer_prompt() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            (
                "human",
                "Question: {question}\n\n"
                "Retrieved context:\n{context}",
            ),
        ]
    )
