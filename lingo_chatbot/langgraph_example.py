from typing import Annotated
from utils import call_api_key
from typing_extensions import TypedDict
from langchain_openai import OpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.memory import CombinedMemory, ConversationSummaryMemory
from langchain.chains.conversation.base import ExtendedConversationBufferMemory
from langchain_core.prompts import PromptTemplate
from llm_1.prompts import create_persona, create_prompt
from langchain.runnables import RunnableWithMessageHistory

class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

api_key = call_api_key('OpenAI_API_Key')

llm = OpenAI(api_key=api_key)

persona = create_persona()
prompt = create_prompt()
char = "궤도"
user = "User"

conv_memory = ExtendedConversationBufferMemory(
    llm=llm, 
    memory_key="history", 
    input_key="input", 
    ai_prefix=char, 
    human_prefix=user, 
    extra_variables=["context"]
)
summary_memory = ConversationSummaryMemory(
    llm=llm,
    memory_key="summary",
    input_key="input",
    ai_prefix=char,
    human_prefix=user
)

memories = CombinedMemory(memories=[conv_memory, summary_memory])

def chatbot(state: State):
    chain = RunnableWithMessageHistory(
        llm=llm,
        memory=memories,
        prompt=prompt
    )
    response = chain.invoke({"input": state["messages"], "history": memories.load_memory_variables({})})
    response_content = response.get('response', '')  # 응답의 실제 내용을 가져옵니다.
    return {"messages": state["messages"] + [("assistant", response_content)]}

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

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
