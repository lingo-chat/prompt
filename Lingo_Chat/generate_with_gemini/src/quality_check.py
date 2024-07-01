"""
This module is used to check the quality of the generated text.

멀티 턴 전체를 로드해서 다음 기준을 통해 품질을 체크합니다.
    1. 일단 기본적으로 post-processing을 진행(질문 반복 제거, 특수문자 제거 등)
    2. 답변의 정확성 및 답변을 했는가, 질문 및 답변을 반복하는가를 기준으로 점수를 매긴다.
        1점: 답변이 반복되거나, 전혀 도움되지 않는 말만 하느 ㄴ경우
        2-3점: 답변이 어느정도 질문에 연관이 있는 경우
        4-5점: 답변이 질문에 꽤 근접하고 연관있는 경우
"""


"""
    Gemini / Local Llama-3 model이 생성된 데이터를 평가
"""

import re
import os
import time
import json
import jsonlines
import asyncio
import concurrent.futures

try:    # main.py 위치 기준
    from src.api import gemini
    from src.prompt import CORRECTNESS_ORBIT_SYS_TMPL, CORRECTNESS_USER_TMPL
    from src.utils import jsonl_save
except: # __file__ 위치 기준
    from api import gemini
    from prompt import CORRECTNESS_ORBIT_SYS_TMPL, CORRECTNESS_USER_TMPL
    from utils import jsonl_save

from tqdm import tqdm
from typing import Dict, List, Any, Union
from dotenv import load_dotenv

load_dotenv()

#################
##### Gemini Utility 함수 시작
#################


def run_gemini(model="geminipro1.0", model_api_key="", system_input="", user_input=""):
    """
    Gemini를 async하게 run할 수 있도록 하는 매개함수
    """
    result = asyncio.run(get_gemini_reponse(model, model_api_key, system_input, user_input))
    return result


async def get_gemini_reponse(model_name, model_api_key, system_input, user_input):
    response = await gemini.async_chat_comp_response(
        model_name=model_name,
        model_api_key=model_api_key,
        system_input=system_input,
        user_input=user_input,
        temperature=0.5,
        top_p=0.9,
        top_k=40,
        max_tokens=8192,
        # message_history=chat_history
    )
    return response


#################
##### Gemini Utility 함수 끝
#################


def filter_by_score(json_data, boundary, score_name: str = "score"):
    """
    score가 boundary 를 넘지 못하는 경우 해당 데이터 삭제

    Argument:
        json_data: Dict representing JSON data with a score field.
        boundary: The minimum score required to keep the data.
        score_name: The name of the score field in json_data (defaults to 'score')

    Return:
        json_data: Dict or None if the score is below the boundary.

    Raises:
        KeyError: If the score_name is not found in json_data.
    """
    if score_name not in json_data:
        raise KeyError(
            f"[Key Error] Score name {score_name} should be matched in the given dictionary!"
        )
        # return json_data

    score = json_data.get(score_name, None)
    if int(score) < int(boundary):
        return None
    return json_data


#################
##### Evaluation 함수 시작
#################


class ResponseCorrectness:
    def __init__(self): ...

    @classmethod
    def run(
        self,
        idx=None,
        model="geminipro1.0",
        question: str = "",
        response: str = "",
        answer: str = "",
    ):
        """
        생성된 답변이 질문에 대해 Correct 한지를 1~5점 사이로 채점합니다. Higher is better.
        채점 프롬프트: LlamaIndex Correctness Evaluator

        Question: 원본 질문
        Response: 생성된 답변
        Answer: 원본 답변

        채점 모델:
            - Gemini pro v1.0
            - Local LLM: 현재 구현 x
        """
        self.model = model
        if "gemini" in self.model:
            model_api_key = "AIzaSyB57MsoWYRFfvlYwdGxltyeLnHXkE1d3wM"  # 추후 api 전달받으면서 진행할 수 있도록 수정해야 함
            if idx is not None:
                _model_api_key = [
                    "AIzaSyB57MsoWYRFfvlYwdGxltyeLnHXkE1d3wM",
                    "AIzaSyATcEkxmqQjF-M34Ul-PfRjYBP_0QDh65o",
                ]
                model_api_key = _model_api_key[idx % 2]

            # SYSTEM_PROMPT = response_correctness.CORRECTNESS_SYS_TMPL
            SYSTEM_PROMPT = CORRECTNESS_ORBIT_SYS_TMPL
            USER_PROMPT = CORRECTNESS_USER_TMPL.format(
                query=question, reference_answer=answer, generated_answer=response
            )
            result = run_gemini(
                model=model,
                model_api_key=model_api_key,
                system_input=SYSTEM_PROMPT,
                user_input=USER_PROMPT,
            )
            return result

        else:
            print(f"gemini 이외에는 구현 안되어있음")
            
        
    @classmethod
    def multiturn_run(
        self,
        gemini_api_key: str,
        model="geminipro1.0",
        messages: List[Dict]=[],
    ):
        """
        생성된 답변이 질문에 대해 Correct 한지를 1~5점 사이로 채점합니다. Higher is better.
        채점 프롬프트: LlamaIndex Correctness Evaluator

        Arguments:
            idx: The index of the data to be evaluated.
            model: The model to use for evaluation.
            messages: The messages to evaluate.

        채점 모델:
            - Gemini pro v1.0
            - Local LLM: 현재 구현 x
        """
        self.model = model
        
        if "gemini" in self.model:
            # SYSTEM_PROMPT = response_correctness.CORRECTNESS_SYS_TMPL
            SYSTEM_PROMPT = CORRECTNESS_ORBIT_SYS_TMPL
            USER_PROMPT = _get_user_prompt_from_multiturn(messages=messages)
            result = run_gemini(
                model=model,
                model_api_key=gemini_api_key,
                system_input=SYSTEM_PROMPT,
                user_input=USER_PROMPT,
            )
            return result

        else:
            print(f"gemini 이외에는 구현 안되어있음")
    

    @classmethod
    def filter(self, 
               new_dict : Dict[str, Any], 
               score_with_feedback: str, 
               key_name="score"):
        """
        전달된 dictionary를 score에 기반하여 regex 필터링하빈다.
        score를 추출하고, dictionary를 업데이트 한 뒤, 리턴합니다. (score가 특정 점수를 넘는지 필터링하지는 않습니다)

        Argument:
            new_dict (dict): The dictionary to process and save. It should contain a key 'score_with_feedback'.
            score_with_feedback(str): The string feedback from LLM API(here, Gemini pro 1.0)

        Return:
            new_dict (dict): The updated dict with score

        * score가 boundary 를 넘는지 안넘는지를 기준으로 필터링 하는것은 결과를 많이 보고 임의로 설정해야 함 -> 따로 수행
        """
        # 저장
        try:
            score_pattern = r"-?\d+\.?\d*"
            score = re.findall(score_pattern, score_with_feedback)[0]
            if score:
                new_dict[key_name] = score[0]
            else:
                new_dict[key_name] = None
            new_dict[key_name + "_feedback"] = re.sub(
                score_pattern, "", score_with_feedback, count=1
            ).strip()
            return new_dict

        except Exception as E:
            print(f"\n[ERROR with GEMINI API] error message:{E}\n\n")
            raise Exception

    
def _get_user_prompt_from_multiturn(messages: List[Dict]) -> str:
    """
    Multiturn messages를 [question] [answer] 형태로 변환합니다.

    Args:
        messages (str): List[Dict]

    Raises:
        Exception: role, content 형태가 아닌 경우 error rasises.

    Returns:
        str: gemini로 채점할 수 있는 형태의 prompt
    """
    if messages[-1].get('role', None) is None or messages[-1].get('content', None) is None:
        raise Exception("Role or Content key are not found in the messages")
    
    result = ""
    
    for idx, message in enumerate(messages):
        if message['role'] == 'user':
            _data = "[Question]: " + message['content'] + "\n"
        else:
            _data = "[Answer]: " + message['content'] + "\n"
        result += _data
    return result
        

    
def multiturn_main(jsonl_data_path: str, 
                   jsonl_save_path: str,
                   gemini_api_key_list: List[str],
                   start_idx: int = 0):
    ## 1. model load
    ## 2. 각 평가기준 프롬프트 구성
    ## 3. loop 돌면서 호출 및 평가
    ## 4. 기록 및 저장
    ## 5. 점수 시각화
    ## 6. 점수 기준으로 필터링

    _data_list = []
    with jsonlines.open(jsonl_data_path) as f:
        for line in f.iter():
            _data_list.append(line)

    def _process_data(idx: int,
                      _data: Dict[str, Any]):
        _new_item = _data
        gemini_api_key = gemini_api_key_list[idx % len(gemini_api_key_list)]
        sleep_sec = 2.5

        # 1. Response correctness 채점
        score_with_feedback = ResponseCorrectness.multiturn_run(
            gemini_api_key=gemini_api_key,
            model="geminipro1.0",
            messages=_data["messages"],
        )

        print(
            f"-------------------------------------------------------------------------------------------------------------------------------------\n"
        )
        # print(f">> Question: {data['question']}\n>> Response:\n{data['en_answer']}\n\n----------\n>> Feedback:\n{score_with_feedback}\n\n\n")
        _content = [i['content'] for i in _data['messages']]
        _messages = "\n- ".join(_content)
        print(
            f">>IDX: {idx}\n>> Messages:\n{_messages}\n\n----------\n>> Feedback:\n{score_with_feedback}\n\n\n"
        )

        try:
            ##### 2. Filtering 1
            _new_item = ResponseCorrectness.filter(
                new_dict=_new_item,
                score_with_feedback=score_with_feedback,
            )

            ##### Filtering 2
            #
            # _new_item = filter_by_score(json_data=_new_item,
            #                             boundary=3,
            #                             score_name='score')
            ##### Save
            jsonl_save(jsonl_save_path, _new_item)
            print(f"{idx} is saved...\n\n")
        except:
            print(f"Error occured while filtering and saving the data.\n\n")
            with open(os.path.basename(jsonl_save_path).split('.')[0]+'_error.txt', 'a+') as f:
                    f.write(f"{idx}번째 데이터에서 에러 발생\n")

        time.sleep(sleep_sec)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(gemini_api_key_list)) as executor:
        futures = [executor.submit(_process_data, idx, _data) for idx, _data in enumerate(_data_list) if idx >= start_idx]
        for future in tqdm(concurrent.futures.as_completed(futures), total=(len(_data_list)-start_idx)):
            future.result()
    
    return


def cutoff_by_score(
    jsonl_data_path: str,
    jsonl_save_path: str,
):
    ultrachat_sampled_v1_orbit = []
    with jsonlines.open(jsonl_data_path) as f:
        for line in f.iter():
            ultrachat_sampled_v1_orbit.append(line)

    for idx, data in tqdm(
        enumerate(ultrachat_sampled_v1_orbit),
        total=len(ultrachat_sampled_v1_orbit),
        desc="Gemini score 기반 필터링 중...",
    ):

        _new_item = filter_by_score(
            json_data=data, boundary=4, score_name="score"  # 이거보다 작으면 삭제
        )
        if _new_item:
            jsonl_save(jsonl_save_path, _new_item)


# if __name__ == "__main__":
    
#     # # jsonl 데이터 post-processing 진행하기
#     # from post_processing import PostProcessing
    
#     # jsonl_data_path = "../data/multiturn_data_0701_1085.jsonl"
#     # jsonl_save_path = "../data/post/multiturn_data_irritated_post.jsonl"
    
#     # ps = PostProcessing.multiturn(file_dir=jsonl_data_path,
#     #                               save_dir=jsonl_save_path)


#     # jsonl로부터 데이터 퀄리티 평가하고 컬럼 추가하기
#     jsonl_data_path = "../data/post/multiturn_data_irritated_post.jsonl"
#     jsonl_save_path = "../data/post/multiturn_data_irritated_post_scored.jsonl"
    
#     start_idx = 0
#     gemini_api_key_list = gemini_api_key_list = [os.getenv(f"{i}_GEMINI_API_KEY") for i in ["HF", "HL"]]    # ["LE", "JH", "DN", "YH"]
    
#     multiturn_main(jsonl_data_path, 
#                    jsonl_save_path,
#                    gemini_api_key_list=gemini_api_key_list,
#                    start_idx=start_idx)


#     # # only cutoff filtering and save
#     # jsonl_data_path = "../data/converted/KoAlpaca/KoAlpaca_v1.4.2_orbit_0604_post_concat_scored_re.jsonl"
#     # jsonl_save_path = "../data/converted/KoAlpaca/KoAlpaca_v1.4.2_orbit_0604_post_concat_scored_re_filtered.jsonl"
#     # cutoff_by_score(jsonl_data_path, jsonl_save_path)
