from schemas.states import QueryState
from langgraph.graph import START, END, StateGraph
from services.bedrock_llm import query_model
from workflows.retriever import search_in_docs
from workflows.ragflow import rag_workflow
from typing import List


def process_query(state: QueryState) -> dict:
    """Extract the query from the state."""
    query = state.get('question')
    messages = state.get('messages', [])
    messages.append({'role': 'user', 'content': query})
    return {'question': query, 'messages': messages}


def classify_query(state: QueryState) -> dict:
    """Analyzes the query from the state and returns an analysis."""
    query = state.get('question')
    prompt = (
        "You are a conditional router node in a workflow graph. "
        "You can access to a knowledge base about the documentation of a library, "
        "framework or API."
        "Given the following user query, classify its intent as one of the following: "
        "'general' (for general questions related to the documentation, "
        "route to a retrieval-augmented generation node), "
        "'code' (for questions related to a specific piece of code, "
        " route to a code analysis node), or "
        "'clarification' (if the intent is unclear and more information is needed from the user). "
        "Respond with only one word: 'general', 'code', or 'clarification'.\n\n"
        f"User query: {query}"
    )
    query_type = query_model(
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        tokens=50
    ).strip()
    print(f"Query type selected: {query_type}")
    return {'intent': query_type}


def route_query(state: QueryState) -> str:
    """Routes the query based on its classified intent and returns a routing decision."""
    intent = state.get('intent')
    if intent == 'retrieval':
        decision = "retrieval"
    # elif intent == 'code':
    #     decision = "code"
    elif intent == 'clarification':
        decision = "clarification"
    else:
        decision = "retrieval"
    return decision


def ask_clarification(state: QueryState) -> dict:
    """Generates an answer for the user, asking to clarify the query."""
    query = state.get('question')
    messages = state.get('messages', [])
    prompt = (
        f"The user has made this question: '{query}'"
        "However, since the question is unclear or "
        "some information is missing, please generate an answer "
        "asking the user to provide additional details. "
        "Make some suggestions in order to help the user to clarify the query. "
        "Return only the answer for the user."
        "Answer (asking clarification):"
    )
    message = {"role": "user", "content": prompt}
    messages.append(message)
    answer = query_model(
        # messages=[{"role": "user", "content": prompt}],
        messages=messages,
        temperature=0.0,
        tokens=400
    ).strip()
    messages.pop()
    messages.append({'role': 'assistant', 'content': answer})
    return {'answer': answer, 'messages': messages}


def analyze_code(state: QueryState) -> dict:
    """Inspect the code fragment, and find errors or suggest improvements"""
    query = state.get('question')
    messages = state.get('messages', [])
    prompt = (
        "You are a helpul assistant, capable of analyze and improve code. "
        "Extract the code contained in the query and inspect it "
        "looking for errors or opportunities of improvement, "
        "in order to answer the user's question."
        "When applicable, return the improved version of the code."
        f"Question: {query}"
        "Answer:"
    )

    answer = query_model(
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        tokens=400
    ).strip()
    messages.append({'role': 'assistant', 'content': answer})
    return {'answer': answer, 'messages': messages}


def retrieve_info(state: QueryState) -> dict:
    """Retrieves information based on the query from the state."""
    query = state.get('question')
    chat_id = state.get('chat_id', None)
    points = search_in_docs(query, chat_id)
    documents = [point.payload for point in points]
    print(f"Documents: {documents}")
    return {'documents': documents}


def generate_answer(state: QueryState) -> dict:
    """Generates an answer based on the query and context from the state."""
    query = state.get('question')
    messages = state.get('messages')
    documents = state.get('documents', [])
    documents_text = ""
    for chunk in documents:
        chunk_text = chunk.get('text')
        documents_text += f"{chunk_text}\n"
    prompt = (
        "You are an assistant for question-answering tasks. "
        "Use the following pieces of retrieved context to answer the question. "
        "If you don't know the answer, just say that you don't know. "
        "Keep the answer concise."
        f"Question: {query}\n"
        f"Context: {documents_text}\n"
        "Answer:"
    )
    message = {"role": "user", "content": prompt}
    messages.append(message)
    answer = query_model(
        messages=messages,
        temperature=0.0
    ).strip()
    return {'answer': answer, 'messages': messages}


def format_code(state: QueryState) -> dict:
    """Formats the code based on the query and context from the state."""
    code = state.get('code', '')
    formatted_code = code
    return {'code': formatted_code}


def add_to_memory(state: QueryState) -> List[dict]:
    """Adds the query and answer to memory for future reference."""
    query = state.get('question')
    answer = state.get('answer')
    messages = state.get('messages', [])
    messages.append({'role': 'user', 'content': query})
    messages.append({'role': 'assistant', 'content': answer})
    return {'messages': messages}


query_graph = StateGraph(QueryState)

# Define the nodes
query_graph.add_node("process_query", process_query)
query_graph.add_node("analyze_query", classify_query)
query_graph.add_node("route_query", route_query)
query_graph.add_node("retrieve_info", rag_workflow.compile())
query_graph.add_node("generate_answer", generate_answer)
query_graph.add_node("add_to_memory", add_to_memory)
query_graph.add_node("ask_clarification", ask_clarification)

# Build graph
query_graph.add_edge(START, "process_query")
query_graph.add_edge("process_query", "analyze_query")
query_graph.add_conditional_edges(
    "analyze_query",
    route_query,
    {
        "retrieval": "retrieve_info",
        # "code": "analyze_code",
        "clarification": "ask_clarification"
    }
)
query_graph.add_edge("retrieve_info", "generate_answer")
query_graph.add_edge("generate_answer", "add_to_memory")
query_graph.add_edge("ask_clarification", "add_to_memory")
query_graph.add_edge("add_to_memory", END)

# Compile
compiled_graph = query_graph.compile()

png_graph = compiled_graph.get_graph().draw_mermaid_png()
with open("graph.png", "wb") as f:
    f.write(png_graph)
