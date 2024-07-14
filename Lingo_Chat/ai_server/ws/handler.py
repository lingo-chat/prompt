"""
    web socket으로 클라이언트 측에서 요청이 들어온 경우, vllm을 이용해 답변을 생성하는 핸들러 함수
"""

from langchain_openai import ChatOpenAI

# from server.llm_api import VLLM


llm = ChatOpenAI(
    model="/home/iwbaporandhh/huggingface/models/llama3_PAL_orbit_v0.2.2.3",
    openai_api_base="http://0.0.0.0:2496/v1",       # gpt api 가 아닌, vllm이 동작하는 포트로 연결
    max_tokens=2048,
    temperature=0.7,
    api_key="test_api_key",
    streaming=True,
    model_kwargs={'top_p': 0.9, 
                  'frequency_penalty': 1.4,
                  'seed': 42,
                  'stop': ['<|im_end|>', '<|endoftext|>', '<|im_start|>', '</s>'],
                  }
)


async def response_handler(websocket):
    """
        websocket handler 함수
        클라이언트 측으로부터 접속이 요청되어 메세지가 도착한다면 async하게 llm으로 요청하고 리턴합니다.
    """
    try:
        async for message in websocket:
            # llm 서버로 user query 요청
            response = llm.astream(message)
            
            async for response in response: 
                if websocket.closed:
                    raise ConnectionError
                
                # client에게 생성된 답변을 전송
                await websocket.send(response.content)  # 리턴 타입은 AIMessages 타입이므로, str/byte 형태로 send 해야한다.

                try:
                    if response.response_metadata.get('finish_reason', False):
                        await websocket.send('<|im_end|>')
                except:
                    pass
    except websocket.ConnectionClosed or ConnectionError:
        print(f">> 클라이언트와의 접속이 끊어졌습니다.\n")
    except Exception as e:
        print(f">> Unexpected error occured: {e}\n")