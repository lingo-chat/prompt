import os
import pytz
import requests
import socketio
import multiprocessing

from typing import List
from datetime import datetime
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage

from graph import chat_graph, config


##########
### dotenv setting
##########
load_dotenv(override=True)
redis_url = os.getenv('VM_URL')
redis_port = os.getenv('REDIS_PORT')
redis_ms_id = os.getenv('REDIS_MS_ID')
db_port = os.getenv('DB_PORT')


# Redis 및 SQLite 연결 설정
# redis_client = redis.Redis(host=redis_url, port=redis_port, db=1)
# db_reload_url = "http://"+redis_url+":"+db_port+'/reload'
db_reload_url = f"http://"+redis_url+"/chats/db/ai/{chat_room_id}"

websocket_url = "http://"+os.getenv('VM_URL')+":"+os.getenv('API_PORT')
websocket_namespace = os.getenv('API_WS_NAMESPACE')
websocket_event = os.getenv('API_WS_EVENTNAME')

connection_test_message = "ai 서버에서 보내는 연결 테스트 메세지 입니다."

seoul_tz = pytz.timezone('Asia/Seoul')
asio = socketio.AsyncClient(logger=True, engineio_logger=True)

lock = multiprocessing.Lock()

##########
### utility function setting
##########
def _convert_format_to_Message(_chat_history: List) -> List:
    """
        chat_history 포맷을 Message로 변환합니다.
    """
    chat_history = []
    for data in _chat_history:
        _data = eval(data.decode('utf-8'))
        if _data.get('role') == 'user':
            _data = HumanMessage(content=_data["content"])
        elif _data.get('role') == 'assistant':
            _data = AIMessage(content=_data["content"])
        chat_history.append(_data)
    
    # chat_history = [eval(data.decode('utf-8')) for data in _chat_history]    
    return chat_history


async def _get_chat_history_redis(redis_client,
                                  chat_room_id: int) -> List:
    _chat_history = await redis_client.lrange(chat_room_id, 0, -1)
    chat_history = _convert_format_to_Message(_chat_history)
    return chat_history


async def _get_chat_history_db(redis_client,
                               user_id: str,
                               chat_room_id: int) -> List[dict]:
    """
        db로부터 채팅 히스토리를 가져옵니다.
    """
    result = []
    db_chat_history = requests.get(db_reload_url.format(chat_room_id=chat_room_id))
    
    if not db_chat_history.status_code == 200 or db_chat_history.json() is None:
        return result
    
    # 편의상 여기서 user_id 를 추가합니다.
    db_chat_history = fill_user_id(db_chat_history, user_id)
    
    # 마지막 메세지에 시간 초기화
    for idx, chat in enumerate(eval(db_chat_history[0]["chat_history"])):
        if idx == len(eval(db_chat_history[0]["chat_history"]))-1:
            chat["created_time"] = datetime.now(seoul_tz).strftime('%Y-%m-%d %H:%M:%S')
        result.append(str(chat))
    # db_chat_history = [chat for chat in eval(db_chat_history[0]['chat_history'])]
    
    await redis_client.rpush(chat_room_id, *result)
    # chat_history = await get_chat_history(redis_client, chat_room_id)
    # chat_history = _convert_format_to_Message(eval(db_chat_history[0]['chat_history']))
    chat_history = await _get_chat_history_redis(redis_client, chat_room_id)
    
    return chat_history


def fill_user_id(chat_history: List[dict], user_id: str) -> List[dict]:
    """
        chat_history에 user_id를 추가합니다.
    """
    if chat_history[0].get('user_id') is not None:
        return chat_history
    
    for chat in chat_history:
        chat['user_id'] = user_id
    return chat_history


async def get_chat_history(redis_client,
                           user_id: str, 
                           chat_room_id: int) -> List:
    """
        redis로부터 채팅 히스토리를 가져와 포맷을 변경하여 반환합니다.
        
        레디스 안에서: _chat_history == [bytes(list(dict))]
        request로부터 받은 데이터: db_chat_history == [{'chat_room_id': int, 'user_id': str, 'chat_history': str}]
        리턴 형태: chat_history == [HumanMessage(), AIMessage()...]
    """
    # 레디스로부터 채팅 히스토리 조회
    chat_history = await _get_chat_history_redis(redis_client, chat_room_id)
    
    # db 조회 시퀀스 추가 feat-#22
    if len(chat_history) == 0:
        chat_history = await _get_chat_history_db(redis_client, user_id, chat_room_id)
            
    return chat_history


async def save_chat_history(redis_client,
                            chat_room_id: int,
                            user_id: str,
                            user_message: str,
                            final_response: str)-> None:
    """
        chat_history를 redis에 저장합니다.
    """
    current_time = datetime.now(seoul_tz).strftime('%Y-%m-%d %H:%M:%S')
    save_messages = [
        str({"role": "user", "content": user_message, "user_id": user_id, "chat_room_id": chat_room_id}),
        str({"role": "assistant", "content": final_response, "user_id": user_id, "chat_room_id": chat_room_id, "created_time": current_time}),
    ]
    await redis_client.rpush(chat_room_id, *save_messages)
    

async def emit_chat_message(chat_room_id: int,
                            user_id: str,
                            response: str,
                            is_final: bool) -> None:
    """
        웹소켓으로 메세지를 전송합니다.
    """
    lock.acquire()
    await asio.emit(event="ai_chat_message", 
                    data={"user_id": user_id,
                          "chat_room_id": chat_room_id,
                          "response": response,
                          "is_final": is_final},
                    namespace=websocket_namespace)
    lock.release()
    return


async def call_chat_graph(chat_history: List,
                          user_message: str,
                          chat_room_id: int,
                          user_id: str) -> str:
    """
        chat_graph를 호출하여 chatbot의 답변을 받아옵니다.
        Refer to: Lingo_Chat/ai_server/graph/graph.py
    """
    response = chat_graph.astream_events({"history": chat_history, "messages": user_message}, config=config, version='v1')    # return: async_generator
    
    final_response = ""
    async for resp in response:
        try:
            chatbot_messages = resp['data']['chunk'].content
            if chatbot_messages and resp['name'] == 'ChatOpenAI':
                # print(f"{chatbot_messages}", end='')
                
                await emit_chat_message(chat_room_id, user_id, chatbot_messages, False)
                
                final_response += chatbot_messages
                
            if resp['name'] == 'ChatOpenAI' and resp['data']['chunk'].response_metadata['finish_reason'].lower() == 'stop':
                print(f">> [Langgraph 생성 답변]: {final_response}")
                print(f"\n\n>> [response handler] finished...\n\n")
                
        except Exception as e:
            pass
    
    return final_response