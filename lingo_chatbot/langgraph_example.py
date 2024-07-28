from typing import Annotated
from utils import call_api_key
from typing_extensions import TypedDict
from langchain_openai import OpenAI, OpenAIEmbeddings
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from llm_2.vector_db import *
from llm_2.rag_chain import *
from llm_3 import *  # Import missing module
import os

class State(TypedDict):
    messages: Annotated[list, add_messages]
    rag_evaluate: bool

graph_builder = StateGraph(State)

api_key = call_api_key('OpenAI_API_Key')

llm = OpenAI(api_key=api_key)

def chatbot(state: State):
    response = llm.invoke(state["messages"])
    return {"messages": state["messages"] + [("assistant", response)]}

def RAG_chat(state: State):
    prompt_evaluate, prompt_generate = llm_2_prompts()
    embedding_function = OpenAIEmbeddings(openai_api_key=api_key)

    retriever = None
    try:
        retriever = call_vectordb(DB_PATH="./chroma_db", 
                                  embedding_function=embedding_function, 
                                  chunk_size=300, 
                                  chunk_overlap=0, 
                                  api_key=api_key)
    except RuntimeError as e:
        print(f"Error loading vector database: {e}")
        return {"messages": state["messages"] + [("assistant", "Error loading vector database.")]}

    evaluate_chain = rag_chain(retriever=retriever, prompt=prompt_evaluate, llm=llm)
    generate_chain = rag_chain(retriever=retriever, prompt=prompt_generate, llm=llm)

    user_message = state["messages"][-1][1]
    evaluate_result = evaluate_chain.invoke(user_message)
    generation_result = generate_chain.invoke(user_message)

    response = f"Evaluate Result: {evaluate_result}\nGeneration Result: {generation_result}"
    return {"messages": state["messages"] + [("assistant", response)]}

def is_rag_needed(state: State):
    user_message = state["messages"][-1][1]
    return "RAG" in user_message or "search" in user_message

# Add nodes to the graph
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("RAG_chat", RAG_chat)

# Add conditional edges
graph_builder.add_edge(START, "chatbot", condition=lambda state: not is_rag_needed(state))
graph_builder.add_edge(START, "RAG_chat", condition=is_rag_needed)

# Connect the nodes to END
graph_builder.add_edge("chatbot", END)
graph_builder.add_edge("RAG_chat", END)

graph = graph_builder.compile()

while True:
    user_input = input("User: ")
    if user_input.lower() in ["quit", "exit", "q"]:
        print("Goodbye!")
        break
    state = {"messages": [("user", user_input)]}
    
    for event in graph.stream(state):
        for value in event.values():
            print("Assistant:", value["messages"][-1][1])
