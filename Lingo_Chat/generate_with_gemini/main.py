"""
    기존 '과학 커뮤니케이터 궤도' 말투로 답변을 변형한 KoAlpaca_v1.1_orbit_v1.4.3 을 기반으로
    Multiturn 데이터를 생성하는 코드입니다.
    
    - reference: Ultrachat
    - dataset: HEYPAL/persona_orbit_dataset
    - model: GEMINI pro 1.0 free
    - creator: Joo Hyeong Lee
"""
import os
import time
import random
import argparse
import asyncio
import concurrent.futures

from dotenv import load_dotenv
from datasets import load_dataset
from typing import Dict, List
from tqdm import tqdm

from src.api import gemini
from src.utils import (jsonl_save, count_answer_length, 
                       argparse_load_from_yaml, jsonl_read)
from src.post_processing import PostProcessing
from src.quality_check import multiturn_main
from src.prompt import (system_prompt, semi_science_communicator_role_name, semi_science_communicator_role_description,
                        orbit_role_name, orbit_role_description,
                        neuroticism_role_name, neuroticism_role_description, neuroticism_answer_prefix,
                        historian_and_physician_role_name, historian_and_physician_role_description,
                        humanities_scholar_role_name, humanities_scholar_role_description,
                        question_conv_induce_prompt, conv_induce_prompt, conv_induce_prompt_with_prefix,
                        question_induce_prompt, answer_induce_prompt,
                        CORRECTNESS_MULTITURN_SCORING_PROMPT)


def convert_org_question(model_name: str,
                         api_key: str,
                         system_prompt: str,
                         question_conv_induce_prompt: str,
                         _data: Dict[str, str],
                         temperature: float = 0.4)-> str:
    """
    오리지널의 _data['instruction']를 받아서 새로운 질문을 생성하는 함수입니다.
    원본 질문과 같을 수 있고, 다른 질문이 생성될 수 있습니다.

    Args:
        model_name (str): 생성에 사용할 proprietary model name
        api_key (str): api key
        system_prompt (str): role이 부여된 시스템 프롬프트
        question_conv_induce_prompt (str): 질문을 변형하기 위한 프롬프트
        _data (Dict[str, str]): _description_
        temperature (float): 생성 시 온도

    Returns:
        str: 생성된(변형된) 질문
    """
    
    user_input= system_prompt + "\nUser: "+_data['instruction']+"\n\n\n"
    conv_output = asyncio.run(_run(model_name, user_input, question_conv_induce_prompt, api_key, temperature))
    
    return conv_output


def convert_org_answer(model_name: str,
                       api_key: str,
                       instruction: str,
                       system_prompt: str,
                       role_name: str,
                       conv_induce_prompt: str,
                       answer_prefix: str = None,
                       temperature: float = 0.2) -> str:
    """
    생성 및 변형된 질문을 받아 답변을 생성하는 함수입니다.

    Args:
        model_name (str): 생성에 사용할 proprietary model name
        api_key (str): api key
        instruction (str): 변형/생성된 질문
        system_prompt (str): role이 부여된 시스템 프롬프트
        role_name (str): role 이름
        conv_induce_prompt (str): 답변을 생성(유도)하기 위한 프롬프트
        answer_prefix (str): 답변 생성 시 prefix
        temperature (float): 생성 시 온도

    Returns:
        str: 생성된(변형된) 답변
    """
    
    if answer_prefix: 
        conv_induce_prompt = conv_induce_prompt.format(role_name=role_name, answer_prefix=answer_prefix)
    else:
        conv_induce_prompt = conv_induce_prompt.format(role_name=role_name)
    user_input= system_prompt + "\nUser: "+instruction+"\n\n\n"
    conv_output = asyncio.run(_run(model_name, user_input, conv_induce_prompt, api_key, temperature))
    
    return conv_output


def main(data_list: List[Dict],
         system_prompt: str,
         gemini_api_key_list: List[str],
         multiturn_config,
         json_config,
         scoring_config,
         ) -> None:
    """
    Multiturn 데이터를 생성 main code
    
    생성 시퀀스:
        1. KoAlpaca_v1.1_orbit_v1.4.3 데이터 불러오기
        2. 첫 번째 turn 로드
        3. (시스템 프롬프트 + 첫 번째 turn + user 질문생성 프롬프트) 모델 전송 -> 생성된 질문 async receive
            ((동일한 프롬프트) + 모델 답변=질문 + assistant 답변생성 프롬프트) 모델 전송 -> 답변 생성
        4. 원하는만큼 반복 후 종료(총 n 턴 데이터 생성)
    """
    ### base setting
    model_name = multiturn_config.model_name
    role_name = eval(f"{multiturn_config.persona_name}_role_name")
    
    multiturn_question_induce_prompt = question_induce_prompt.format(role_name=role_name)
    multiturn_answer_induce_prompt = answer_induce_prompt.format(role_name=role_name)
    
    data_save_path = json_config.jsonl_save_dir
    target_turn = multiturn_config.target_turn
    start_idx = json_config.start_idx
    scoring_prompt = eval(f"{scoring_config.scoring_prompt}")
    
    conv_answer_flag = False
    if not data_list[0].get('org_output', None):    # not none, then 'KoAlpaca_orbit'.
        conv_answer_flag = True
        print(f"원본 데이터만 존재하므로, 원본데이터 {os.path.basename(json_config.inspiring_json_dir)}의 질문답변을 바탕으로\n새로운 멀티 턴(턴 수: {multiturn_config.target_turn}) 데이터를 생성합니다.\n\n")
    if multiturn_config.use_answer_prefix is True:
        _prefixes = "\n".join(eval(f'{multiturn_config.persona_name}_answer_prefix'))
        print(f"\n첫 답변 생성 시, 다음 중 하나의 prefix가 추가됩니다.\n\n--\n{_prefixes}\n--\n\n\n")
    
    
    def _filtering_and_scoring(idx: int,
                               model_name: str,
                               _data: List[Dict],
                               system_prompt: str,
                               filtered_save_dir: str,
                               gemini_api_key_list: List[str]):
        """
        생성된 데이터를 후처리 후 점수를 매깁니다.

        Args:
            _data (List[Dict]): 생성된 데이터
        """
        # filtering
        filtered_data = PostProcessing.multiturn(file_dir=_data,
                                                 save_dir=filtered_save_dir,
                                                 if_save=False)
        # scoring
        try:
            multiturn_main(model_name=model_name,
                        jsonl_data_path=filtered_data, 
                        jsonl_save_path=filtered_save_dir,
                        gemini_api_key_list=gemini_api_key_list,
                        system_prompt=system_prompt,
                        start_idx=0,
                        sleep_sec=0.1,
                        if_thread=False,)
        except Exception as e:
            print(f"scoring Error: {e}\n")
        
    
    def _generate_turn_data(idx, _data):
        print(f"\n\n\n------------------------- {idx} -------------------------\n")
        gemini_api_key = gemini_api_key_list[idx%len(gemini_api_key_list)]
        
        now_turn = 1
        
        # 첫 번째 turn 생성
        instruction = _data['instruction']
        output = _data['output']
        
        if conv_answer_flag:
            instruction = convert_org_question(model_name, gemini_api_key, system_prompt, question_conv_induce_prompt, _data)
            if multiturn_config.use_answer_prefix is True:
                answer_prefix = random.choice(eval(f"{multiturn_config.persona_name}_answer_prefix"))
                output = convert_org_answer(model_name=model_name, 
                                            api_key=gemini_api_key, 
                                            instruction=instruction, 
                                            system_prompt=system_prompt, 
                                            role_name=role_name, 
                                            conv_induce_prompt=conv_induce_prompt_with_prefix, 
                                            answer_prefix=answer_prefix)
            else:
                output = convert_org_answer(model_name=model_name, 
                                            api_key=gemini_api_key, 
                                            instruction=instruction, 
                                            system_prompt=system_prompt, 
                                            role_name=role_name, 
                                            conv_induce_prompt=conv_induce_prompt,)
            
        _input = system_prompt+'\nUser: '+instruction+'\nAssitant: '+output+'\n\n\n'
        
        _num_first_answer = count_answer_length(output)
        ans_num_paragraphs = [_num_first_answer[0]]
        ans_num_words = [_num_first_answer[1]]

        messages = [{'role': 'user', 'content': instruction},
                    {'role': 'assistant', 'content': output},]
        
        # 원하는 turn 수 만큼 생성
        while(now_turn < target_turn):
            try:
                # 새로운 turn 생성
                _gen_new_turn = gen_new_turn(model_name=model_name, 
                                             gemini_api_key=gemini_api_key, 
                                             _user_input=_input, 
                                             question_induce_prompt=multiturn_question_induce_prompt, 
                                             answer_induce_prompt=multiturn_answer_induce_prompt)
                
                # 생성된 turn의 길이 계산
                _num_new_answer = count_answer_length(_gen_new_turn['gen_answer'])
                
                # 생성된 turn 저장
                messages.append({'role': 'user', 'content': _gen_new_turn['gen_question']})
                messages.append({'role': 'assistant', 'content': _gen_new_turn['gen_answer']})
                ans_num_paragraphs.append(_num_new_answer[0])
                ans_num_words.append(_num_new_answer[1])
                
                now_turn += 1
                _input = _input.split('\n\n\n')[0]+'\nUser: '+_gen_new_turn['gen_question']+'\nAssistant: '+_gen_new_turn['gen_answer']+'\n\n\n'
                time.sleep(6)
                
            except Exception as e:
                print(f"Error: {e}\n")
                with open(os.path.basename(data_save_path).split('.')[0]+'_error.txt', 'a+') as f:
                    f.write(f"{idx}번째 데이터에서 에러 발생\n")
                break
        
        if ans_num_paragraphs:
            # 생성된 데이터 포맷 세팅
            _new_multiturn_data = {
                'instruction': instruction,
                'ans_num_paragraphs': ans_num_paragraphs,
                'ans_num_words': ans_num_words,
                'num_turns': len(ans_num_paragraphs),
                'messages': messages,
                # 'output': _data['output'],
                # 'org_output': _data['org_output'],
                'url': _data['url'],
                'persona': multiturn_config.persona_name,
            }
            # 생성된 데이터 저장(raw data)
            jsonl_save(data_save_path, _new_multiturn_data)
            
            # 필터링 & 점수화
            _filtering_and_scoring(idx=idx,
                                   model_name=model_name,
                                   _data=[_new_multiturn_data],
                                   system_prompt=scoring_prompt,
                                   filtered_save_dir=json_config.filtered_save_dir,
                                   gemini_api_key_list=gemini_api_key_list)

            print(f"{idx} is done with scoring & saving.\n\n")
            return _new_multiturn_data
            
        else:
            print(f"{idx} is not scored and not saved.\n\n")

    # 병렬 처리
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(gemini_api_key_list)) as executor:
        futures = [executor.submit(_generate_turn_data, idx, _data) for idx, _data in enumerate(data_list) if idx >= start_idx]
        
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
        top_p=0.99,
        top_k=60,  
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
    gen_answer = asyncio.run(_run(model_name, _new_user_input, answer_induce_prompt, gemini_api_key, 0.05))
    
    return {'gen_question': gen_question, 'gen_answer': gen_answer}


def generate_multiturn_with_feedback():
    """
    Multiturn dataset을 생성합니다.
    basic_config.yaml을 수정하여 관련 파라미터를 조절하고 실행합니다.
    
    1. Configuration load
    2. Multiturn generation main function start
    3. Post-processing function call
    4. Quality check function call
    """
    
    load_dotenv()
    random.seed(42)
    
    # 1-1. yaml file load by argparse
    print(f"-------------------------------------------------")
    print(f"\n>>> 1. Load configuration file !!!\n")
    parser = argparse.ArgumentParser(description="Model Inference Configuration")
    parser.add_argument("--args", type=str, required=False, default='src/config/yaml/use_config.yaml', help="Path to the YAML configuration file")
    args = parser.parse_args()
    inference_config, multiturn_config, json_config, scoring_config = argparse_load_from_yaml(args.args)
    
    # 1-2. gemini api key load, dataset setting
    gemini_api_key_list = [os.getenv(f"{i}_GEMINI_API_KEY") for i in multiturn_config.key_list if os.getenv(f"{i}_GEMINI_API_KEY") != 'None']
    jsonl_data = jsonl_read(json_config.inspiring_json_dir)
    jsonl_data = random.sample(jsonl_data, len(jsonl_data))[3016:]
    print(f"\n>> 1-2. Number of available API Keys : {len(gemini_api_key_list)}\n")
    
    # 1-3. prompt setting
    role_name = eval(f"{multiturn_config.persona_name}_role_name")
    role_description = eval(f"{multiturn_config.persona_name}_role_description")
    
    role_system_prompt = system_prompt.format(role_name=role_name, role_description_and_catchphrases=role_description)
    scoring_prompt = eval(f"{scoring_config.scoring_prompt}")
    print(f"\n>> 1-3. Prompt setting is done !!!\n>> Target Role Name: {role_name}\n\n>> Target System prompt: --\n{role_system_prompt}\n--\n\n")
    
    # 2. main function
    print(f"\n>>> 2. Start to generate multi-turn dataset !!!\nStart within 10 secs . . .\n\n")
    print(f"-------------------------------------------------\n\n")
    time.sleep(10)
    
    main(data_list=jsonl_data,
         system_prompt=role_system_prompt,
         gemini_api_key_list=gemini_api_key_list,
         multiturn_config=multiturn_config,
         json_config=json_config,
         scoring_config=scoring_config,
         )


if __name__ == '__main__':
    generate_multiturn_with_feedback()
    
    