import os
import redis

from dotenv import load_dotenv
from datetime import datetime, timedelta

from app import models, schemas, crud
from app.database import SessionLocal, engine


load_dotenv(override=True)

redis_url = os.getenv('VM_URL')
redis_port = os.getenv('REDIS_PORT')
redis_ms_id = os.getenv('REDIS_MS_ID')

# Redis 및 PostgreSQL 연결 설정
r = redis.Redis(host=redis_url, port=redis_port, db=1)

models.Base.metadata.create_all(bind=engine)


def backup(chat_history: schemas.chat_history_backup):
    db = SessionLocal()
    try:
        crud.backup_chat_history(db, chat_history)
        return True
    except Exception as e:
        print(f">> Error in crud backup: {e}\n\n")
        return False


def backup_chat_rooms():
    # Redis에서 채팅방 목록 조회
    redis_queues = [i.decode('utf-8') for i in r.keys('*')]
    if 'user_ms_queue' in redis_queues:
        redis_queues.remove('user_ms_queue')
        
    print(f"\n\n>> Now saved chat rooms: {redis_queues}\n\n")
    now = datetime.now()
    
    for rq_name in redis_queues:
        _last_chat = r.lrange(rq_name, -2, -1)
        _last_chat = [eval(i.decode('utf-8')) for i in _last_chat]
        try:
            _last_chat_created_time = _last_chat[-1]['created_time']
            last_created_time = datetime.strptime(_last_chat_created_time, '%Y-%m-%d-%H-%M-%S')
            
            # 1분 이상 차이나는지 확인
            if (now - last_created_time) > timedelta(minutes=1):
                print(f"\n\n>> Chat room {{ {rq_name} }} is now backuped!\n\n")
                
                _chat_history = r.lrange(rq_name, 0, -1)
                _chat_history = [eval(i.decode('utf-8')) for i in _chat_history]
                
                _chat_history_data = schemas.chat_history_backup(
                    chat_room_id=int(_chat_history[0]['chat_room_id']),
                    user_id=str(_chat_history[0]['user_id']),
                    chat_history=str(_chat_history)
                )
                
                if backup(_chat_history_data):
                    r.delete(rq_name)
                
        except Exception as e:
            print(f">> Error in whole backup sequence: {e}\n\n")
            

# 실제로 Airflow의 PythonOperator에서 호출될 함수
def run_backup():
    backup_chat_rooms()

    
if __name__ == "__main__":
    backup_chat_rooms()
