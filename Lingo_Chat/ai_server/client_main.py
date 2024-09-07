"""
    api 서버에서 ai 서버와 소켓 연결을 했다고 가정하고,
    ai 서버는 Redis를 이용해 유저의 입력을 읽어들인다.

    동작:
    1. 실시간 채팅방 생성에 따른 {user_message, chat_room_id}를 redis 에서 받아옴.
    2. 또한 이전 채팅 히스토리를 
        2-1. redis에서 chat_room_id를 사용해 조회.
        2-2. cloud db에서 chat_room_id를 사용해 조회.
    3. chatbot을 호출하고 다시 redis에 저장하며, 결과를 리턴.
"""

from client import run_client

if __name__ == '__main__':
    run_client()