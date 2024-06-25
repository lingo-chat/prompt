import json
import aiohttp


SAFETY_SETTING = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

def jsonl_save(dir, json_data):
    with open(dir, "a+", encoding="utf-8") as f:
        json.dump(
            json_data, f, ensure_ascii=False
        )  # ensure_ascii로 한글이 깨지지 않게 저장
        f.write(
            "\n"
        )  # json을 쓰는 것과 같지만, 여러 줄을 써주는 것이므로 "\n"을 붙여준다.
        

async def llm_query(
    model_url: str, api_key: str, _input: list, _generation_config: dict
):
    """
    Gemini_pro API를 이용해서(post) TEMPLATE 에 대한 답변을 리턴.
    """
    async with aiohttp.ClientSession() as session:
        headers = {"Content-Type": "application/json"}

        payload = {
            "contents": _input,
            "generationConfig": _generation_config,
            "safetySettings": SAFETY_SETTING,
        }

        async with session.post(
            model_url + api_key, headers=headers, json=payload
        ) as response:
            data = ""
            try:
                data = await response.json()
                data = data["candidates"][0]["content"]["parts"][0]["text"]
            except Exception as E:
                print(f"\n[ERROR with GEMINI API] error message:{E}\n\n")
            return data


async def stream_response(url, headers, data):
    """
    VLLM 출력 시 asynchronize 하게 print할 수 있도록 구현한 함수입니다.
    chat_comp_response에서 인자 streaming을 True로 전달하면 해당 함수가 호출됩니다.
    """
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:
            async for line in response.content:
                try:
                    decoded_line = line.decode("utf-8").strip()
                    if decoded_line.startswith("data: "):
                        json_data = json.loads(decoded_line.split("data: ")[1])
                        chunk = (
                            json_data.get("choices", [])[0]
                            .get("delta", {})
                            .get("content", "")
                        )
                        print(chunk, end="", flush=True)
                except Exception as e:
                    pass
