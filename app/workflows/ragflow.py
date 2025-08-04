from pprint import pprint

from langgraph.graph import END, START, StateGraph
from schemas.states import RagState
from services.bedrock_llm import query_model

from .retriever import search_in_docs
from .utils import (
    format_docs,
    grade_answer,
    grade_hallucination,
    grade_retrieval,
    rewrite_question,
)


def retrieve(state: RagState):
    """
    Retrieve documents

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, documents, that contains retrieved documents
    """
    print("---RETRIEVE---")
    question = state.get("question")
    chat_id = state.get("chat_id")
    points = search_in_docs(question, chat_id)
    documents = [point.payload for point in points]
    return {"documents": documents, "question": question}


def generate(state):
    """
    Generate answer

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, generation, that contains LLM generation
    """
    print("---GENERATE---")
    question = state.get("question")
    documents = state.get("documents")

    # RAG generation
    docs_txt = format_docs(documents)
    prompt = (
        "You are an assistant for question-answering tasks. "
        "Use the following pieces of retrieved context to answer the question. "
        "If you don't know the answer, just say that you don't know. "
        "Use three sentences maximum and keep the answer concise.\n"
        f"Question: {question}\n"
        f"Context: {docs_txt}\n"
        "Answer:"
    )
    answer = query_model(
        messages=[{"role": "user", "content": prompt}], temperature=0.0, tokens=400
    ).strip()
    return {"documents": documents, "question": question, "answer": answer}


def grade_documents(state):
    """Determines whether the retrieved documents are relevant to the question."""

    print("---CHECK DOCUMENT RELEVANCE TO QUESTION---")
    question = state.get("question")
    documents = state.get("documents")

    # Score each doc
    filtered_docs = []
    for d in documents:
        score = grade_retrieval(question, d.get("text"))
        grade = score.binary_score
        if grade == "yes":
            print("---GRADE: DOCUMENT RELEVANT---")
            filtered_docs.append(d)
        else:
            print("---GRADE: DOCUMENT NOT RELEVANT---")
            continue
    return {"documents": filtered_docs, "question": question}


def transform_query(state):
    """Transform the query to produce a better question."""

    print("---TRANSFORM QUERY---")
    question = state.get("question")
    documents = state.get("documents")

    better_question = rewrite_question(question)
    return {"documents": documents, "question": better_question}


def decide_to_generate(state):
    """Determines whether to generate an answer, or re-generate a question."""

    print("---ASSESS GRADED DOCUMENTS---")
    state.get("question")
    filtered_documents = state.get("documents")

    if not filtered_documents:
        print(
            "---DECISION: ALL DOCUMENTS ARE NOT RELEVANT TO QUESTION, TRANSFORM QUERY---"
        )
        return "transform_query"
    else:
        print("---DECISION: GENERATE---")
        return "generate"


def grade_generation_v_documents_and_question(state):
    """
    Determines whether the generation is grounded in the document
    and answers question.
    """

    print("---CHECK HALLUCINATIONS---")
    question = state.get("question")
    documents = state.get("documents")
    answer = state.get("answer")

    score = grade_hallucination(documents, answer)
    grade = score.binary_score

    # Check hallucination
    if grade == "yes":
        print("---DECISION: GENERATION IS GROUNDED IN DOCUMENTS---")
        # Check question-answering
        print("---GRADE GENERATION vs QUESTION---")
        score = grade_answer(question, answer)
        grade = score.binary_score
        if grade == "yes":
            print("---DECISION: GENERATION ADDRESSES QUESTION---")
            return "useful"
        else:
            print("---DECISION: GENERATION DOES NOT ADDRESS QUESTION---")
            return "not useful"
    else:
        pprint("---DECISION: GENERATION IS NOT GROUNDED IN DOCUMENTS, RE-TRY---")
        return "not supported"


rag_workflow = StateGraph(RagState)

# Define the nodes
rag_workflow.add_node("retrieve", retrieve)
rag_workflow.add_node("grade_documents", grade_documents)
rag_workflow.add_node("generate", generate)
rag_workflow.add_node("transform_query", transform_query)

# Build graph
rag_workflow.add_edge(START, "retrieve")
rag_workflow.add_edge("retrieve", "grade_documents")
rag_workflow.add_conditional_edges(
    "grade_documents",
    decide_to_generate,
    {
        "transform_query": "transform_query",
        "generate": "generate",
    },
)
rag_workflow.add_edge("transform_query", "retrieve")
rag_workflow.add_conditional_edges(
    "generate",
    grade_generation_v_documents_and_question,
    {
        "not supported": "generate",
        "useful": END,
        "not useful": "transform_query",
    },
)

# Compile
compiled_rag_graph = rag_workflow.compile()

png_rag_graph = compiled_rag_graph.get_graph().draw_mermaid_png()
with open("rag-graph.png", "wb") as f:
    f.write(png_rag_graph)
