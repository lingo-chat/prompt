"""
    web socket으로 클라이언트 측에서 요청이 들어온 경우, vllm을 이용해 답변을 생성하는 핸들러 함수
"""

<<<<<<< HEAD
from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages, AnyMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.checkpoint.aiosqlite import AsyncSqliteSaver

from configs import (default_system_prompt,
    orbit_role_name, orbit_role_description
)


llm = ChatOpenAI(
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
=======
from graph import chat_graph, config

>>>>>>> origin


async def response_handler(websocket):
    """
        websocket handler 함수
        클라이언트 측으로부터 접속이 요청되어 메세지가 도착한다면 async하게 llm으로 요청하고 리턴합니다.
    """
    try:
        async for message in websocket:
            # llm 서버로 user query 요청
            messages = ('user', message)
<<<<<<< HEAD
            response = graph.astream({"messages": messages}, config=config)    # return: async_generator
            
            async for resp in response:
                # resp: agent 가 각각의 key 값으로 된 dict[] 이 리턴됨.
                
                chatbot_messages = resp['chatbot']['messages']  # return: async_generator
                # client에게 생성된 답변을 전송
                # await websocket.send(resp.content)  # 리턴 타입은 AIMessages 타입이므로, str/byte 형태로 send 해야한다. - ChatOpenAI에서 바로 .stream 호출 시의 response
                
                async for messages in chatbot_messages[-1]:
                    if websocket.closed:
                        raise ConnectionError
                
                    if messages.content:
                        await websocket.send(messages.content)
                        
                # if response.response_metadata.get('finish_reason', False):    # - ChatOpenAI에서 바로 .stream 호출 시의 response
                if messages.response_metadata['finish_reason'] == 'stop':
                    await websocket.send('<|im_end|>')
=======
            response = chat_graph.astream_events({"messages": messages}, config=config, version='v1')    # return: async_generator
            
            async for resp in response:
                # resp: agent 가 각각의 key 값으로 된 dict[] 이 리턴됨.
                # print(f">> [response_handler] resp: {resp}\n\n")
                # chatbot_messages = resp['chatbot']['messages']  # return: async_generator
                # # client에게 생성된 답변을 전송
                # # await websocket.send(resp.content)  # 리턴 타입은 AIMessages 타입이므로, str/byte 형태로 send 해야한다. - ChatOpenAI에서 바로 .stream 호출 시의 response
                
                # async for messages in chatbot_messages[-1]:
                #     if websocket.closed:
                #         raise ConnectionError
                
                #     if messages.content:
                #         await websocket.send(messages.content)
                try:
                    chatbot_messages = resp['data']['chunk'].content
                    if chatbot_messages and resp['name'] == 'ChatOpenAI' and not websocket.closed:
                        await websocket.send(chatbot_messages)
                    # print(f">> [response handler] resp['data']['chunk']: {resp['data']['chunk']}\n")
                    
                    if resp['name'] == 'ChatOpenAI' and resp['data']['chunk'].response_metadata['finish_reason'].lower() == 'stop':
                        print(f">> [response handler] finished...\n\n")
                        await websocket.send('<|im_end|>')
                except:
                    pass
                        
                # # if response.response_metadata.get('finish_reason', False):    # - ChatOpenAI에서 바로 .stream 호출 시의 response
                # if messages.response_metadata['finish_reason'] == 'stop':
                #     await websocket.send('<|im_end|>')
>>>>>>> origin

    except ConnectionError:
        print(f">> 클라이언트와의 접속이 끊어졌습니다.\n")
    except Exception as e:
<<<<<<< HEAD
        print(f">> Unexpected error occured: {e}\n")
    

class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    
    
def init_graph():
    """
        vllm(ChatOpenAI)와 langgraph를 연동하여 graph를 만들기 위한 initialization 코드입니다.
    """
    # 시스템 프롬프트 설정
    system_prompt = default_system_prompt.format(role_name=orbit_role_name,
                                                 role_description_and_catchphrases=orbit_role_description)
    primary_assistant_prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("placeholder", "{messages}"),
    ])

    # llm inference with sys prompt
    sys_llm = primary_assistant_prompt | llm
    
    def chatbot(state: State):  # state: state: {'messages': [HumanMessage(content='hi', id='<random_id>'), HumanMessage(content='당신은 누구신가요?', id='4d04d7f3-3f4a-4ee9-b53d-434e38eee217'),...]}
        return {"messages": [sys_llm.astream(state)]}   # "messages" 형태로 ChatPromptTemplate 가 받으므로, state 전체를 전달
    
    # 대화 내용 기억을 위한 메모리설정
    memory = AsyncSqliteSaver.from_conn_string(":memory:")

    # Langgraph 설정
    graph_builder = StateGraph(State)
    graph_builder.add_node("chatbot", chatbot)
    
    graph_builder.add_edge(START, "chatbot")
    graph_builder.add_edge("chatbot", END)
    
    graph = graph_builder.compile(checkpointer=memory)    
    config = {"configurable": {"thread_id": "0"}}
    
    print(f"\n\n>> Graph initialized successfully.\n\n")
    return graph, config

graph, config = init_graph()
=======
        print(f">> Unexpected error occured: {e}\n")
>>>>>>> origin
