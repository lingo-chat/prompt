"""
    api 서버에서 ai 서버와 소켓 연결을 했다고 가정하고,
    ai 서버는 Redis를 이용해 유저의 입력을 읽어들인다.

    동작:
    1. 실시간 채팅방 생성에 따른 {user_message, chat_room_id}를 redis 에서 받아옴.
    2. 또한 이전 채팅 히스토리를 chat_room_id를 통해서 받아옴.
    3. chatbot을 호출하고 다시 redis에 저장하며, 결과를 리턴함.
"""
import os
import redis
import asyncio

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage

from graph import chat_graph, config

### Redis 설정
load_dotenv(override=True)
redis_url = os.getenv('REDIS_URL')
redis_port = os.getenv('REDIS_PORT')
redis_ms_id = os.getenv('REDIS_MS_ID')


async def hello():
    uri = redis_url
    r = redis.Redis(host=uri, port=redis_port, db=0)
    
    while True:
        _, message = r.brpop(redis_ms_id)
        
        # 1. 메세지 수신
        message = eval(message.decode('utf-8'))
        user_id, user_message = message['chat_room_id'], message['user_message']
        print(f"chat_room_id: {user_id}, message: {user_message}\n\n")
        
        
        # 2. 히스토리 조회 -> AIMessages, HumanMessages 로 변환이 필요
        def _get_chat_history(user_id):
            """
                _chat_history == [bytes(list(dict))]
            """
            _chat_history = r.lrange(user_id, 0, -1)
            chat_history = []
            
            # 3. chat format으로 다시 변경
            for data in _chat_history:
                _data = eval(data.decode('utf-8'))
                if _data.get('role') == 'user':
                    _data = HumanMessage(content=_data['content'])
                elif _data.get('role') == 'assistant':
                    _data = AIMessage(content=_data['content'])
                chat_history.append(_data)
            
            # chat_history = [eval(data.decode('utf-8')) for data in _chat_history]
            return chat_history
        
        chat_history = _get_chat_history(user_id)
        # print(f"\n\n>> chat_history: {chat_history}\n\n")

        # 4. chatbot 호출
        response = chat_graph.astream_events({"history": chat_history, "messages": user_message}, config=config, version='v1')    # return: async_generator
        final_response = ""
        async for resp in response:
            try:
                chatbot_messages = resp['data']['chunk'].content
                if chatbot_messages and resp['name'] == 'ChatOpenAI':
                    # for i in chatbot_messages:
                    print(chatbot_messages, end="", flush=True)
                    final_response += chatbot_messages
                    
                if resp['name'] == 'ChatOpenAI' and resp['data']['chunk'].response_metadata['finish_reason'].lower() == 'stop':
                    print(f"\n>> [response handler] finished...\n\n")
                    
            except:
                pass
            # if response == '<|im_end|>':
            #     break
 
        # 5. redis history 저장
        save_messages = [
            str({'role': 'user', 'content': user_message}),
            str({'role': 'assistant', 'content': final_response})
        ]
        r.rpush(user_id, *save_messages)

asyncio.get_event_loop().run_until_complete(hello())
