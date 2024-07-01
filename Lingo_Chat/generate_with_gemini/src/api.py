import os
import json
import yaml
import aiohttp
import asyncio
import secrets
import google.generativeai as genai

from dotenv import load_dotenv
try:
    from .utils import SAFETY_SETTING
    from .utils import llm_query
except:
    from utils import SAFETY_SETTING
    from utils import llm_query

### setting up the environment
load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
gemini_api_key = os.getenv("GEMINI_API_KEY")
print(f"OpenAI api key : {openai_api_key}")
print(f"Gemini api key : {gemini_api_key}\n\n")

GEMINI_10_BASE = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.0-pro:generateContent?key="
GEMINI_15_BASE = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key="
### setting up the environment end

class gemini:
    """
    Calls api using configuration files.
    Need to fill out 'use_config.yaml' file first.

    Can be revised to used local LLM.
    """

    @staticmethod
    async def async_chat_comp_response(
        model_name: str = "geminipro1.0",
        model_api_key: str = gemini_api_key,
        system_input: str = "",
        user_input: str = "",
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 40,
        # seed: int = 42,
        max_tokens: int = 8192,
        # json_format:str=None,
        # logprobs:bool=False,
        # streaming:bool=False,
        message_history: list = None,
    ):
        """
        Calls GEMINI chat completion api

        Gemini에서는 System prompt와 user input의 구분을 구현하지 않았다.
        system prompt가 들어오면 단순히 string concat을 진행한다.

        Params
            model_name:str='geminipro1.0',
            system_input:str="",
            user_input:str="",
            temperature:float=0.7,
            top_k:int=1,
            top_p:float=0.9,
            max_output_token:int=2048,
            # json_format:str=None,     # 현재 구현 X
            # logprobs:bool=False,
            # streaming:bool=True,
            message_history:list=None,

        Return
            response:
        """
        # 모델
        if "1.5" in model_name.lower():
            model = GEMINI_15_BASE
        else:
            model = GEMINI_10_BASE

        # 프롬프트
        if system_input != "":
            input_prompt = system_input + "\n\n" + user_input
        else:
            input_prompt = user_input

        # 대화 내역
        messages = []
        if message_history:
            if type(message_history) != list:
                print("/n/nERROR: Message_history type should be list!!!\n")
                # return None
            messages = message_history

        messages.append({"role": "user", "parts": [{"text": input_prompt}]})

        # 각종 파라미터
        generation_config = {
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "max_output_tokens": max_tokens,
            "response_mime_type": "text/plain",
            "stop_sequences": [],
            # "topK": top_k,
            # "topP": top_p,
            # "maxOutputTokens": max_tokens,
            # "stopSequences": [],
        }

        # 모델 추론 요청
        response = await llm_query(
            model_url=model,
            api_key=model_api_key,
            _input=messages,
            _generation_config=generation_config,
        )

        return response

    @staticmethod
    def chat_comp_response(
        model_name: str = "geminipro1.0",
        model_api_key: str = gemini_api_key,
        system_input: str = "",
        user_input: str = "",
        temperature: float = 0.7,
        top_k: int = 40,
        top_p: float = 0.9,
        max_output_token: int = 8192,
        # json_format:str=None,
        # logprobs:bool=False,
        # streaming:bool=False,
        message_history: list = None,
    ):
        """
        Calls GPT chat completion api

        Notice: 아래 사이트에서 Google cloud 관련 인증을 진행해야 함. 상당히 번거로우므로 사용하지 않는 것을 추천.
            - https://cloud.google.com/docs/authentication/external/set-up-adc

        Params
            model_name:str='geminipro1.0',
            system_input:str="",
            user_input:str="",
            temperature:float=0.7,
            top_k:int=1,
            top_p:float=0.9,
            max_output_token:int=2048,
            # json_format:str=None,     # 현재 구현 X
            # logprobs:bool=False,
            # streaming:bool=True,
            message_history:list=None,

        Return
            response:
        """
        # 모델
        if "1.5" in model_name.lower():
            model = GEMINI_15_BASE
        else:
            model = GEMINI_10_BASE

        # 프롬프트
        if system_input != "":
            input_prompt = system_input + "\n\n" + user_input
        else:
            input_prompt = user_input

        # 대화 내역
        messages = []
        if message_history:
            if type(message_history) != list:
                print("/n/nERROR: Message_history type should be list!!!\n")
                # return None
            messages = message_history

        # 각종 파라미터
        generation_config = {
            "temperature": temperature,
            "top_k": top_k,
            "top_p": top_p,
            "max_output_tokens": max_output_token,
            "stop_sequences": [],
        }

        # 모델 추론 요청
        model = genai.GenerativeModel(
            model_name=model,
            generation_config=generation_config,
            safety_settings=SAFETY_SETTING,
        )
        convo = model.start_chat(history=messages)

        # messages.append({
        #     "role": "user",
        #     "parts": [{"text": user_input}]
        # })

        convo.send_message(user_input)
        response = convo.last.text

        return response


# if __name__ == "__main__":
    
