from typing import Literal, Optional

from pydantic import BaseModel, Field


class DocsInfo(BaseModel):
    url: str
    chatId: Optional[str] = None


class Message(BaseModel):
    message: str


class RouteQuery(BaseModel):
    """
    Route a user query to the most relevant node based on intent.

    - If the question is general, route to a retrieval-augmented generation (RAG) node.
    - If the question is about code, route to a code analysis node.
    - If the agent is unsure, route to a clarification node to request more information from the user.
    """

    intent: Literal["general", "code", "clarification"] = Field(
        ...,
        description=(
            "Intent of the user query. "
            "'general' for general questions (route to RAG), "
            "'code' for code-related questions (route to code analysis), "
            "'clarification' if more information is needed from the user."
        ),
    )


class GradeDocuments(BaseModel):
    """Binary score for relevance check on retrieved documents."""

    binary_score: str = Field(
        description="Documents are relevant to the question, 'yes' or 'no'"
    )


class GradeHallucinations(BaseModel):
    """Binary score for hallucination present in generation answer."""

    binary_score: str = Field(
        description="Answer is grounded in the facts, 'yes' or 'no'"
    )


class GradeAnswer(BaseModel):
    """Binary score to assess answer addresses question."""

    binary_score: str = Field(
        description="Answer addresses the question, 'yes' or 'no'"
    )
