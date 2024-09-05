import os
import pytz
import time
import redis
import requests

from dotenv import load_dotenv
from datetime import datetime, timedelta


load_dotenv(override=True)
seoul_tz = pytz.timezone('Asia/Seoul')

redis_url = os.getenv('VM_URL')
redis_port = os.getenv('REDIS_PORT')
redis_ms_id = os.getenv('REDIS_MS_ID')
db_port = os.getenv('DB_PORT')

# Redis 및 SQLite 연결 설정
r = redis.Redis(host=redis_url, port=redis_port, db=1)
url = "http://"+redis_url+":"+db_port+'/backup'


def backup_chat_rooms():
    # Redis에서 채팅방 목록 조회
    redis_queues = [i.decode('utf-8') for i in r.keys('*')]
    if 'user_ms_queue' in redis_queues:
        redis_queues.remove('user_ms_queue')
        
    print(f"\n\n>> Now saved chat rooms: {redis_queues}\n\n")
    now = datetime.strptime(datetime.now(seoul_tz).strftime('%Y-%m-%d-%H-%M-%S'), '%Y-%m-%d-%H-%M-%S')
    
    for rq_name in redis_queues:
        _last_chat = r.lrange(rq_name, -2, -1)
        _last_chat = [eval(i.decode('utf-8')) for i in _last_chat]
        try:
            _last_chat_created_time = _last_chat[-1]['created_time']
            last_created_time = datetime.strptime(_last_chat_created_time, '%Y-%m-%d-%H-%M-%S')
            print(f">> Chat room {{ {rq_name} }} : {now-last_created_time}")
            
            # 1분 이상 차이나는지 확인
            if (now - last_created_time) > timedelta(seconds=30):
                print(f">> Chat room {{ {rq_name} }} is now backuped!\n\n")
                
                _chat_history = r.lrange(rq_name, 0, -1)
                _chat_history = [eval(i.decode('utf-8')) for i in _chat_history]
                
                _chat_history_data = {
                    "chat_room_id":int(_chat_history[0]['chat_room_id']),
                    "user_id":str(_chat_history[0]['user_id']),
                    "chat_history":str(_chat_history)
                }
                
                response = requests.post(url, json=_chat_history_data)
                if response.status_code == 200:
                    # print(f"Output saved successfully, time: {response}")
                    r.delete(rq_name)
                else:
                    print("Failed to save output", response)
                    
                # if backup(_chat_history_data):
                #     r.delete(rq_name)
                
        except Exception as e:
            print(f">> Error in whole backup sequence: {e}\n\n")
            

# 실제로 Airflow의 PythonOperator에서 호출될 함수
def run_backup():
    backup_chat_rooms()

    
if __name__ == "__main__":
    while(True):
        time.sleep(10)
        backup_chat_rooms()
