import asyncio
import websockets

from .handler import response_handler

async def _init_(ws_port: int):
    async with websockets.serve(ws_handler=response_handler,
                                host="localhost",
                                port=ws_port    # 이 포트는 외부접속용 포트로, fastapi vllm을 동작시키는 포트와는 달라야 함.
                                ):  
        await asyncio.Future()                  # run forever


def start_websockets(ws_port: int):
    """
        웹소켓 서버를 초기화합니다.
        
        websockets.serve: 
        Whenever a client connects, the server creates a WebSocketServerProtocol, performs the opening handshake, and delegates to the connection handler, ws_handler.
    """
    # 웹소켓 설정
    asyncio.run(_init_(ws_port=ws_port))
    
    return True