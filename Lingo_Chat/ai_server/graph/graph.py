
import os
import json

from dotenv import load_dotenv

from Levenshtein import ratio
from typing import Annotated, Literal
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages, AnyMessage
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.checkpoint.aiosqlite import AsyncSqliteSaver
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableConfig


from configs import (default_system_prompt,
    orbit_role_name, orbit_role_description
)

load_dotenv()

### llm setting
local_llm = ChatOpenAI(
    model="/home/iwbaporandhh/huggingface/models/llama3_PAL_orbit_v0.2.2.3",
    openai_api_base="http://0.0.0.0:2496/v1",       # gpt api 가 아닌, vllm이 동작하는 포트로 연결
    max_tokens=2048,
    temperature=0.7,
    api_key="test_api_key",
    streaming=True,
    stop=['<|im_end|>', '<|endoftext|>', '<|im_start|>', '</s>'],
    model_kwargs={'top_p': 0.9, 
                  'frequency_penalty': 1.4,
                  'seed': 42,
                  }
)

gemini_llm = ChatGoogleGenerativeAI(
    model="gemini-pro",
    google_api_key=os.environ.get("JH_GEMINI_API_KEY"),
    convert_system_message_to_human = True,
    verbose = True,
)

tool = TavilySearchResults(max_results=1)
tools = [tool]
tool_name_list = [tool.name for tool in tools]

system_prompt = default_system_prompt.format(role_name=orbit_role_name,
                                             role_description_and_catchphrases=orbit_role_description)

primary_assistant_prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("placeholder", "{messages}"),
])

search_llm = gemini_llm.bind_tools(tools)
local_llm = primary_assistant_prompt | local_llm


### graph setting
class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    
    
def chatbot_search(state: State, config: RunnableConfig):
    print(f"\n>> [chatbot search] state:\n>> {state}\n\n")
    return {"messages": [search_llm.invoke(state["messages"], config)]}


async def chatbot_chat(state: State, config: RunnableConfig):
    """
        Chatbot Chat 함수는 다음과 같은 순서로 동작한다.
        - chatbot search 가 호출되었을 경우 해당 결과를 받아서 다시 답변을 생성
        - chatbot search 가 호출되지 않았을 경우, 사용자의 입력만을 추출해서 답변을 생성
        
        추후 업데이트:
            - tool calling 부분의 AImessages 부분을 제외한 HumanMessages, AIMessages 만을 다시 append 해서 호출해야 함...
    """
    print(f"\n>> [chatbot chat] state:\n>> {state}\n\n")
    
    result = []
    
    for idx, message in enumerate(state['messages']):
        print(f"\n>> [chatbot chat] {idx} th message:\n>> {message}\n")
        
        if type(message) == HumanMessage:
            result.append(message)
        elif type(message) == AIMessage and 'llama3' in message.response_metadata.get('model_name', 'Gemini'):
            result.append(message)
    
    result = {'messages': result}
    
    print(f"\n\n >> chatbot_chat final input: \n>> {result}\n>> type: {type(result)}\n\n")
    print(f">> type of state['messages']: {type(state['messages'])}\n\n")
    
    response = await local_llm.ainvoke(result, config)
    return {"messages": response}


class BasicToolNode:
    """A node that runs the tools requested in the last AIMessage.
    솔직히 이거 무슨 함수인지 잘 모르겠음. 일단 패스
    """

    def __init__(self, tools: list) -> None:
        self.tools_by_name = {tool.name: tool for tool in tools}
        print(f"self.tools_by_name: {self.tools_by_name}\n\n")

    def __call__(self, inputs: dict):
        print(f">> [BasicToolNode] inputs:\n>> {inputs}\n\n")
        if messages := inputs.get("messages", []):
            message = messages[-1]
        else:
            raise ValueError("No message found in input")
        
        print(f">> [BasicToolNode] messages:\n>> {messages}\n\n")
        
        outputs = []
        for tool_call in message.tool_calls:
            called_tool_name = tool_call['name']
            
            ### llm이 호출한 함수 이름이 tool_name_list에 있는지 확인하고, 
            # 조금의 철자가 틀리면 호출이 안 되기 때문에, 레벤슈타인 거리를 계산하여 가장 높은 ratio를 가진 idx를 선택하여 tool을 호출한다.
            # 1. 레벤슈타인 거리 계산
            _max_tool_name_ratio, _max_idx = 0.0, 0
            for idx, _name in enumerate(tool_name_list):
                _tool_name_ratio = ratio(_name, called_tool_name)
                if _tool_name_ratio > _max_tool_name_ratio:
                    _max_tool_name_ratio = _tool_name_ratio
                    _max_idx = idx
            
            # 2. 가장 높은 ratio를 가진 idx 선택
            called_tool_name = tool_name_list[_max_idx]
            
            # 3. 해당 idx 로 tool 호출
            tool_result = self.tools_by_name[called_tool_name].invoke(
                tool_call["args"]
            )
            outputs.append(
                ToolMessage(
                    content=json.dumps(tool_result),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            )
        return {"messages": outputs}


def route_tools(
    state: State,
) -> Literal["tools", "__end__"]:
    """
    Use in the conditional_edge to route to the ToolNode if the last message
    has tool calls. Otherwise, route to the end.
    """
    if isinstance(state, list):
        ai_message = state[-1]
    elif messages := state.get("messages", []):
        ai_message = messages[-1]
    else:
        raise ValueError(f"No messages found in input state to tool_edge: {state}")
    print(f">> [route] This is ai messages:\n>>{ai_message}\n\n")
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tools"
    print(f">> [route] tools return end!\n\n")
    # return "__end__"
    return "__next__"

   
def init_graph():
    """
        vllm(ChatOpenAI)와 langgraph를 연동하여 graph를 만들기 위한 initialization 코드입니다.
    """
    # 시스템 프롬프트 설정
    # system_prompt = default_system_prompt.format(role_name=orbit_role_name,
    #                                              role_description_and_catchphrases=orbit_role_description)
    # primary_assistant_prompt = ChatPromptTemplate.from_messages([
    #     ("system", system_prompt),
    #     ("placeholder", "{messages}"),
    # ])

    # llm inference with sys prompt
    # sys_llm = primary_assistant_prompt | local_llm
    
    # search llm
    # search_llm = gemini_llm.bind_tools(tools)
    
    
    # def chatbot(state: State):  # state: state: {'messages': [HumanMessage(content='hi', id='<random_id>'), HumanMessage(content='당신은 누구신가요?', id='4d04d7f3-3f4a-4ee9-b53d-434e38eee217'),...]}
    #     return {"messages": [sys_llm.astream(state)]}   # "messages" 형태로 ChatPromptTemplate 가 받으므로, state 전체를 전달
    
    # 대화 내용 기억을 위한 메모리설정
    memory = AsyncSqliteSaver.from_conn_string(":memory:")

    # Langgraph 설정
    # graph_builder = StateGraph(State)
    # graph_builder.add_node("chatbot", chatbot)
    
    # graph_builder.add_edge(START, "chatbot")
    # graph_builder.add_edge("chatbot", END)
    
    # new version
    tool_node = BasicToolNode(tools=[tool])
    
    graph_builder = StateGraph(State)
    graph_builder.add_node("chatbot search", chatbot_search)
    graph_builder.add_node("tools", tool_node)
    graph_builder.add_node("chatbot chat", chatbot_chat)
    
    graph_builder.add_conditional_edges(
        "chatbot search",
        route_tools,
        {"tools": "tools", "__next__": "chatbot chat"},
    )
    graph_builder.add_edge("tools", "chatbot search")
    graph_builder.add_edge(START, "chatbot search")
    graph_builder.add_edge("chatbot chat", END)
    # new version
    
    graph = graph_builder.compile(checkpointer=memory)    
    config = {"configurable": {"thread_id": "0"}}   # 이 thread 가 없다면 애초에 state 에 예전 기록이 남질 않는다.
    
    print(f"\n\n>> Graph initialized successfully.\n\n")
    return graph, config

chat_graph, config = init_graph()