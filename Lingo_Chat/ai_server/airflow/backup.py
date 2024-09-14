import os
import re
import pytz
import time
import redis
import requests

from dotenv import load_dotenv
from typing import List
from datetime import datetime, timedelta

# dotenv 설정
load_dotenv(override=True)
seoul_tz = pytz.timezone('Asia/Seoul')

redis_url = os.getenv('VM_URL')
redis_port = os.getenv('REDIS_PORT')
redis_ms_id = os.getenv('REDIS_MS_ID')
db_port = os.getenv('DB_PORT')

# Redis 및 SQLite 연결 설정
r = redis.Redis(host=redis_url, port=redis_port, db=1)
get_last_created_time_url = "http://"+redis_url+":"+db_port+'/get_last_created_time'
backup_url = "http://"+redis_url+":"+db_port+'/backup'


def filter_current_chat_history(chat_history: List[dict],
                                last_created_time: datetime.datetime) -> List[dict]:
    """
        last_created_time 이후에 진행된 대화 데이터만 필터링하여 반환합니다.
    """
    
    return [i for i in chat_history if datetime.datetime.strptime(i['created_time'], '%Y-%m-%d %H:%M:%S') > last_created_time]


def request_backup(chat_history: List[dict]) -> bool:
    """
        해당 채팅방의 대화 내역을 백업 요청합니다.
        
        Args:
            chat_history: List[dict] - 채팅방의 대화 내역
            # [{'role': 'user', 'content': '', 'user_id': '', 'chat_room_id': 000},
               {'role': 'assistant', 'content': '', 'user_id': '', 'chat_room_id': 000, 'created_time': '2024-09-14 15:04:58'},
                {}, {}, ...]
                
        Action:
        1. 해당 채팅방의 chat_room_id 및 user_id를 담고있는 Json을 전송
        2. 해당 chat_room_id의 마지막 대화의 created_time을 수신
        3. 해당 created_time을 포함한 시간 이후의 대화 내역 필터링 및 송신
        
        Returns:
            bool - 백업 성공 여부
    """
    # 1. 해당 채팅방의 chat_room_id 및 user_id를 담고있는 Json을 전송
    user_info_data = {
        "chat_room_id": int(chat_history[0]['chat_room_id']),
        "user_id": str(chat_history[0]['user_id'])
    }
    response = requests.get(get_last_created_time_url, params=user_info_data)
    
    # 2. last_create_time을 기준으로 백업할 데이터 세팅
    if response.status_code == 200 and response.json()['lastCreatedTime']:
        last_created_time = response.json()['lastCreatedTime']
        _chat_history = filter_current_chat_history(chat_history, last_created_time)
    
    elif response.status_code == 200 and not response.json()['lastCreatedTime']:
        _chat_history = chat_history
    
    else:
        print(f"\n>> Error in request_backup: {response}\n\n")
        return False
    
    # 3. 백업 진행
    chat_history_data = {
        "redisDataList": _chat_history
    }
    
    response = requests.post(backup_url, json=chat_history_data)
    return response.status_code == 200


def backup_chat_rooms():
    # Redis에서 채팅방 목록 조회
    redis_queues = [key.decode('utf-8') for key in r.keys('*') if re.match(r'^\d+$', key.decode('utf-8'))]
    
    now = datetime.strptime(datetime.now(seoul_tz).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
    os.system('clear')
    print(f">> Redis chats will be backuped after 1 minute of inactivity.\n\n")
    print(f">> Now saved chat rooms: {redis_queues}\n>> Last checked at: {now}\n\n")
    
    for rq_name in redis_queues:
        _last_chat = r.lrange(rq_name, -2, -1)
        _last_chat = [eval(i.decode('utf-8')) for i in _last_chat]
        
        try:
            _last_chat_created_time = _last_chat[-1]['created_time']
            last_created_time = datetime.strptime(_last_chat_created_time, '%Y-%m-%d %H:%M:%S')
            print(f">> Chat room {{ {rq_name} }} : {now-last_created_time}")
            
            # 1분 이상 차이나는지 확인
            if (now - last_created_time) > timedelta(seconds=60):
                print(f">> Chat room {{ {rq_name} }} is now backuped!")
                
                _chat_history = r.lrange(rq_name, 0, -1)
                _chat_history = [eval(i.decode('utf-8')) for i in _chat_history]
                
                if request_backup(_chat_history):
                    r.delete(rq_name)
                else:
                    print(">> Error, Failed to save output!\n>>Queue name: {rq_name}\n\n")
                
        except Exception as e:
            print(f">> Error in whole backup sequence: {e}\n\n")
            

# 실제로 Airflow의 PythonOperator에서 호출될 함수
def run_backup():
    backup_chat_rooms()

    
if __name__ == "__main__":
    while(True):
        time.sleep(10)
        backup_chat_rooms()
