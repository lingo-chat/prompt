"""
    기존 '과학 커뮤니케이터 궤도' 말투로 답변을 변형한 KoAlpaca_v1.1_orbit_v1.4.3 을 기반으로
    Multiturn 데이터를 생성하는 코드입니다.
    
    - reference: Ultrachat
    - dataset: HEYPAL/persona_orbit_dataset
    - model: GEMINI API
    - creator: Joo Hyeong Lee
"""
import os
import asyncio

from datasets import load_dataset
from typing import Dict, List

from src.api import gemini, gemini_api_key
from src.utils import jsonl_save
from src.prompt import system_prompt, orbit_role_name, orbit_role_description, question_induce_prompt, answer_induce_prompt

system_prompt = system_prompt.format(role_name=orbit_role_name, role_description_and_catchphrases=orbit_role_description)


def main(model_name: str,
         data_save_path: str,
         target_turn: int = 3,) -> None:
    """
        1. KoAlpaca_v1.1_orbit_v1.4.3 데이터 불러오기
        2. 첫 번째 turn 로드
        3. (시스템 프롬프트 + 첫 번째 turn + user 질문생성 프롬프트) 모델 전송 -> 생성된 질문 async receive
            ((동일한 프롬프트) + 모델 답변=질문 + assistant 답변생성 프롬프트) 모델 전송 -> 답변 생성
        4. 원하는만큼 3번 반복 후 종료(총 n 턴 데이터 생성)
    """
    
    koalpaca_orbit = load_dataset("HEYPAL/persona_orbit_dataset", "KoAlpaca_v1.1_orbit_v1.4.3")['train']
    
    for idx, _data in enumerate(koalpaca_orbit):
        # if idx > 100: break
        print(f"\n\n\n------------------------- {idx} -------------------------\n")
        now_turn = 1
        
        first_user = _data['instruction']
        first_model = _data['output']
        
        # 첫 번째 turn 생성
        _num_first_answer = count_answer_length(first_model)
        ans_num_paragraphs = [_num_first_answer[0]]
        ans_num_words = [_num_first_answer[1]]
        messages = [{'role': 'user', 'content': first_user},
                    {'role': 'assistant', 'content': first_model},]
        
        _input = system_prompt+'\n\nUser: '+first_user+'\nAssitant: '+first_model+'\n\n\n'
        
        # 원하는 turn 수 만큼 생성
        while(now_turn < target_turn):
            try:
                # 새로운 turn 생성
                _gen_new_turn = gen_new_turn(model_name, _input, question_induce_prompt, answer_induce_prompt)
                
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
            
        # 생성된 데이터 포맷 세팅
        _new_multiturn_data = {
            'instruction': _data['instruction'],
            'ans_num_paragraphs': ans_num_paragraphs,
            'ans_num_words': ans_num_words,
            'num_turns': target_turn,
            'messages': messages,
            'output': _data['output'],
            'org_output': _data['org_output'],
            'url': _data['url'],
        }
        
        # 생성된 데이터 저장
        jsonl_save(data_save_path, _new_multiturn_data)

        
def gen_new_turn(model_name: str,
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
    
    async def _run(_user_input, _induce_prompt, temperature) -> str:
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
    
    gen_question = asyncio.run(_run(_user_input, question_induce_prompt, 0.5))
    _new_user_input = _user_input.split('\n\n\n')[0]+'\nUser: '+gen_question+'\n\n\n'
    gen_answer = asyncio.run(_run(_new_user_input, answer_induce_prompt, 0))
    
    return {'gen_question': gen_question, 'gen_answer': gen_answer}
    
    
def count_answer_length(answer) -> List[int]:
    def _count_paragraphs(answer):
        return len(answer.split('\n\n'))
    
    def _count_words(answer):
        return len(answer.split(' '))
    
    return [_count_paragraphs(answer), _count_words(answer)]


if __name__ == '__main__':
    main(model_name="geminipro1.0",
         data_save_path='data/multiturn_data_0625_first50.jsonl',
         target_turn=3)