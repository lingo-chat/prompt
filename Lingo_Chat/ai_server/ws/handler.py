"""
    web socket으로 클라이언트 측에서 요청이 들어온 경우, vllm을 이용해 답변을 생성하는 핸들러 함수
"""

from graph import chat_graph, config



async def response_handler(websocket):
    """
        websocket handler 함수
        클라이언트 측으로부터 접속이 요청되어 메세지가 도착한다면 async하게 llm으로 요청하고 리턴합니다.
    """
    try:
        async for message in websocket:
            # llm 서버로 user query 요청
            messages = ('user', message)
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

    except ConnectionError:
        print(f">> 클라이언트와의 접속이 끊어졌습니다.\n")
    except Exception as e:
        print(f">> Unexpected error occured: {e}\n")
