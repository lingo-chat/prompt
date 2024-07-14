"""
    api 서버에서 ai 서버와 소켓 연결을 했다고 가정하고 ai 서버로 테스트 입력을 전송하는 코드입니다.
"""
import yaml
import asyncio
import websockets


async def hello():
    uri = "wss://<your_tunneling_url>"
    while True:
        print(f"\n입력: ", end="")
        user_input = input()
        
        async with websockets.connect(uri) as websocket:
            await websocket.send(user_input)
            # response = await websocket.recv()
            # print(f"서버 응답: {response}")
            
            try:
                while True:
                    response = await websocket.recv()
                    
                    if response == '<|im_end|>':
                        break
                    
                    print(f"{response}", end="", flush=True)
            
            except websockets.ConnectionClosed:
                print("\n서버와의 연결이 닫혔습니다.")

asyncio.get_event_loop().run_until_complete(hello())
