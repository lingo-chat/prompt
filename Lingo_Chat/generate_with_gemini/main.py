"""
    기존 '과학 커뮤니케이터 궤도' 말투로 답변을 변형한 KoAlpaca_v1.1_orbit_v1.4.3 을 기반으로
    Multiturn 데이터를 생성하는 코드입니다.
    
    - reference: Ultrachat
    - dataset: HEYPAL/persona_orbit_dataset
    - model: GEMINI pro 1.0 free
    - creator: Joo Hyeong Lee
"""
import os
import random
import jsonlines
import asyncio
import concurrent.futures

from dotenv import load_dotenv
from datasets import load_dataset
from typing import Dict, List
from tqdm import tqdm

from src.api import gemini
from src.utils import jsonl_save
from src.prompt import (system_prompt, semi_scientist_role_name, semi_scientist_description,
                        orbit_role_name, orbit_role_description, 
                        conv_induce_prompt, question_induce_prompt, answer_induce_prompt)


def convert_org_answer(model_name: str,
                       gemini_api_key: str,
                       system_prompt: str,
                       conv_induce_prompt: str,
                       _data:str) -> str:

    conv_induce_prompt = conv_induce_prompt.format(role_name=semi_scientist_role_name)
    user_input= system_prompt + "\nUser: "+_data['instruction']+ "\nAssistant: "+_data['output']+ "\n\n\n"
    conv_output = asyncio.run(_run(model_name, user_input, conv_induce_prompt, gemini_api_key, 0.1))
    
    return conv_output


def main(data_list:Dict[List],
         system_prompt:str,
         model_name: str,
         gemini_api_key_list: List[str],
         data_save_path: str,
         target_turn: int = 3,
         start_idx: int = 0) -> None:
    """
    Multiturn 데이터를 생성 main code
    
    생성 시퀀스:
        1. KoAlpaca_v1.1_orbit_v1.4.3 데이터 불러오기
        2. 첫 번째 turn 로드
        3. (시스템 프롬프트 + 첫 번째 turn + user 질문생성 프롬프트) 모델 전송 -> 생성된 질문 async receive
            ((동일한 프롬프트) + 모델 답변=질문 + assistant 답변생성 프롬프트) 모델 전송 -> 답변 생성
        4. 원하는만큼 반복 후 종료(총 n 턴 데이터 생성)
    """
    conv_answer_flag = False
    if not data_list[0].get('org_output', None):    # not none, then 'KoAlpaca_orbit'.
        conv_answer_flag = True
        
    
    def _process_data(idx, _data, conv_answer_flag):
        print(f"\n\n\n------------------------- {idx} -------------------------\n")
        gemini_api_key = gemini_api_key_list[idx%len(gemini_api_key_list)]
        
        now_turn = 1
        
        # 첫 번째 turn 생성
        # set this first
        instruction = _data['instruction']
        output = _data['output']
        if conv_answer_flag:
            ouput = convert_org_answer(model_name, gemini_api_key, system_prompt, conv_induce_prompt, _data)
        
        _input = system_prompt+'\nUser: '+instruction+'\nAssitant: '+output+'\n\n\n'
        # print(f"question:\n{_data['instruction']}\nanswer:\n{conv_output}\n-----\n\n")
        
        _num_first_answer = count_answer_length(output)
        ans_num_paragraphs = [_num_first_answer[0]]
        ans_num_words = [_num_first_answer[1]]

        messages = [{'role': 'user', 'content': _data['instruction']},
                    {'role': 'assistant', 'content': output},]
        
        # 원하는 turn 수 만큼 생성
        while(now_turn < target_turn):
            try:
                # 새로운 turn 생성
                _gen_new_turn = gen_new_turn(model_name, gemini_api_key, _input, question_induce_prompt, answer_induce_prompt)
                
                # 생성된 turn의 길이 계산
                _num_new_answer = count_answer_length(_gen_new_turn['gen_answer'])
                
                # 생성된 turn 저장
                messages.append({'role': 'user', 'content': _gen_new_turn['gen_question']})
                messages.append({'role': 'assistant', 'content': _gen_new_turn['gen_answer']})
                ans_num_paragraphs.append(_num_new_answer[0])
                ans_num_words.append(_num_new_answer[1])
                
                now_turn += 1
                _input = _input.split('\n\n\n')[0]+'\nUser: '+_gen_new_turn['gen_question']+'\nAssistant: '+_gen_new_turn['gen_answer']+'\n\n\n'
            
            except Exception as e:
                print(f"Error: {e}\n")
                with open(os.path.basename(data_save_path).split('.')[0]+'_error.txt', 'a+') as f:
                    f.write(f"{idx}번째 데이터에서 에러 발생\n")
                break
        
        if len(ans_num_paragraphs) > 1:
            # 생성된 데이터 포맷 세팅
            _new_multiturn_data = {
                'instruction': _data['instruction'],
                'ans_num_paragraphs': ans_num_paragraphs,
                'ans_num_words': ans_num_words,
                'num_turns': len(ans_num_paragraphs),
                'messages': messages,
                # 'output': _data['output'],
                # 'org_output': _data['org_output'],
                'url': _data['url'],
            }
            # 생성된 데이터 저장
            jsonl_save(data_save_path, _new_multiturn_data)
            print(f"{idx} is saved.\n\n")
        else:
            print(f"{idx} is not saved.\n\n")

    
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(gemini_api_key_list)) as executor:
        futures = [executor.submit(_process_data, idx, _data) for idx, _data in enumerate(data_list) if idx >= start_idx]
        for future in tqdm(concurrent.futures.as_completed(futures), total=(len(data_list)-start_idx)):
            future.result()


async def _run(model_name, _user_input, _induce_prompt, gemini_api_key, temperature) -> str:
    chat_history = [
        {"role": "user", 
            "parts": [{
                "text": _user_input
            }]
        },
    ]
    response = await gemini.async_chat_comp_response(
        model_name=model_name,
        model_api_key=gemini_api_key,
        system_input="",
        user_input=_induce_prompt,
        temperature=temperature,
        top_p=0.95,
        top_k=40,  
        max_tokens=8192,
        message_history=chat_history,
    )
    print(f"gen:\n{response}\n\n")
    return response  
    
    
def gen_new_turn(model_name: str,
                 gemini_api_key: str,
                 _user_input: str,
                 question_induce_prompt: str, 
                 answer_induce_prompt: str) -> Dict[str, str]:
    """
    Gemini api 를 사용해서 새로운 turn을 생성하는 함수입니다.
    
    Arguments:
        _user_input: str - 이전 turn의 user input
        question_induce_prompt: str - 질문 생성 프롬프트
        answer_induce_prompt: str - 답변 생성 프롬프트
        
    Returns: Dict[str, str]
        gen_question: str - 생성된 질문
        gen_answer: str - 생성된 답변
    """

    gen_question = asyncio.run(_run(model_name, _user_input, question_induce_prompt, gemini_api_key, 0.5))
    _new_user_input = _user_input.split('\n\n\n')[0]+'\nUser: '+gen_question+'\n\n\n'
    gen_answer = asyncio.run(_run(model_name, _new_user_input, answer_induce_prompt, gemini_api_key, 0))
    
    return {'gen_question': gen_question, 'gen_answer': gen_answer}
    
    
def count_answer_length(answer) -> List[int]:
    def _count_paragraphs(answer):
        return len(answer.split('\n\n'))
    
    def _count_words(answer):
        return len(answer.split(' '))
    
    return [_count_paragraphs(answer), _count_words(answer)]


if __name__ == '__main__':
    
    ### setting - you need to set these first
    load_dotenv()
    gemini_api_key_list = [os.getenv(f"{i}_GEMINI_API_KEY") for i in ["JH", "YH", "DN"]]    # ["LE", "JH", "DN", "YH"]
    
    # orbit_system_prompt = system_prompt.format(role_name=orbit_role_name, role_description_and_catchphrases=orbit_role_description)
    semi_system_prompt = system_prompt.format(role_name=semi_scientist_role_name, role_description_and_catchphrases=semi_scientist_description)
    
    # target dataset
    # data_list = load_dataset("HEYPAL/persona_orbit_dataset", "KoAlpaca_v1.1_orbit_v1.4.3")['train']
    random.seed(42)
    jsonl_data = []
    with jsonlines.open("./data/org/KoAlpaca_v1.1.jsonl") as f:
        for line in f.iter():
            jsonl_data.append(line)

    jsonl_data_15k = random.sample(jsonl_data, 15000)
    jsonl_data_15k = jsonl_data_15k[3016:3000+4401]
    
    start_idx = 50

    main(data_list=jsonl_data_15k,  # data_list
         system_prompt=system_prompt,
         model_name="geminipro1.0",
         gemini_api_key_list=gemini_api_key_list,
         data_save_path='./multiturn_data_0627_1.jsonl',
         target_turn=3,
         start_idx=start_idx
         )