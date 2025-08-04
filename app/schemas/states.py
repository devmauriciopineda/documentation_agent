from typing import TypedDict, List, Dict, Optional


class QueryState(TypedDict):
    """
    Represents the state of the query graph.

    Attributes:
        question: user's question
        chat_id: chat id
        documents: list of documents
        intent: intent of the question
        answer: generated answer
        code: code
        messages: list of messages
    """
    question: str
    chat_id: str
    documents: Optional[List[Dict]]
    intent: Optional[str]
    answer: Optional[str]
    code: Optional[str]
    messages: List[Dict]


class RagState(TypedDict):
    """
    Represents the state of the rag graph.

    Attributes:
        question: user's question
        answer: generated answer
        documents: list of documents
    """
    chat_id: str
    question: str
    answer: str
    documents: Optional[List[Dict]]
