import os
import json
import jsonlines
import aiohttp

from tqdm import tqdm
from datasets import Dataset, DatasetDict
from typing import Any, Dict, List


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


def jsonl_read(file_dir: str) -> List[Dict]:
    """
    jsonl 파일을 읽어서 list로 반환합니다.
    """
    result = []
    with jsonlines.open(file_dir) as f:
        for _data in f.iter():
            result.append(_data)
    return result


def json_read() -> List[Dict]:
    """
    Jsonl이 json형태로 저장된 형태 + 각 json이 줄바꿈으로 저장되어있을 때 사용
    """
    json_objects = []

    with open('./Orbit_generated_data_YH_1.jsonl', 'r', encoding='utf-8') as file:
        json_str = ''
        for line in file:
            if line.strip() == '':  # 빈 줄을 만나면 그때까지 읽은 JSON 객체를 파싱
                if json_str.strip() != '':  # 빈 문자열이 아니면
                    try:
                        json_object = json.loads(json_str)
                        json_objects.append(json_object)
                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON: {e}")
                    json_str = ''
            else:
                json_str += line

        if json_str.strip() != '':
            try:
                json_object = json.loads(json_str)
                json_objects.append(json_object)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")

    return json_objects


def count_answer_length(answer) -> List[int]:
    def _count_paragraphs(answer):
        return len(answer.split('\n\n'))
    
    def _count_words(answer):
        return len(answer.split(' '))
    
    return [_count_paragraphs(answer), _count_words(answer)]


### model ouput utility functions
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
### model ouput utility functions

def _append_jsonl(file_path: List[str], 
                  save_path: str):
    """
    흩어진 Jsonl files를 하나로 합치는 함수입니다.

    Args:
        file_path (List[str]): 파일 경로 리스트
        save_path (str): 저장경로
    """
    total_data = [] 
    for idx, data_path in tqdm(enumerate(file_path), total=len(file_path), desc='Appending Jsonl files'):
        _data = jsonl_read(data_path)
        
        if '0626' in data_path:
            _data = list(map(lambda d: {**d, 'persona': 'science_communicator'}, _data))
        elif 'YH' in data_path:
            _data = list(map(lambda d: {**d, 'persona': 'semi-science_communicator'}, _data))
        elif 'history_physics' in data_path:
            _data = list(map(lambda d: {**d, 'persona': 'historian_and_physicist'}, _data))
        elif 'humanities' in data_path:
            _data = list(map(lambda d: {**d, 'persona': 'humanities_scholar'}, _data))

        total_data.extend(_data)
    
    for _data in total_data:
        jsonl_save(save_path, _data)
        

def upload_to_hf(
    _datasetdict,
    directory,
    save_file_name,
    save_directory=None,
    hf_repo_name=None,
    hf_commit_message=None,
):
    """
    Upload to HF
    """
    from dotenv import load_dotenv

    load_dotenv()

    HF_TOKEN = os.getenv("HF_TOKEN")

    # parquet_dir = "parquet"
    # parquet_load_dir = os.path.join(directory, parquet_dir)

    # if not os.path.isdir(parquet_load_dir):
    #     os.makedirs(parquet_load_dir)

    print(
        f"\n\n>> [DatasetDict] ({directory})\n[Num of rows are]: {len(_datasetdict['train'])}\n[Parquet name]: {save_directory}\n\n"
    )
    if hf_commit_message is None:
        hf_commit_message = f"Upload Dataset - {save_file_name}"

    try:
        train_dataset = _datasetdict
        train_dataset.push_to_hub(
            hf_repo_name,
            token=HF_TOKEN,
            config_name=save_file_name,
            commit_message=hf_commit_message,
            private=False,
        )
        print(f">> Upload to HF is done !\n\n")

    except Exception as E:
        print(f"ERROR with saving {directory}, {E}")


def save_into_datadict(
    train_file_dir: str = "",
    test_file_dir: str = "",
    save_directory: str = "",
    save_file_name: str = "",
    hf_repo_name: str = "",
    hf_commit_message: str = "",
):
    """
    jsonl포맷 파일을 Datadict 형태로 변환하여 저장합니다.
    """

    def _gen(_list):
        for item in _list:
            yield item

    train_list = jsonl_read(train_file_dir)
    test_list = None
    if test_file_dir != "" and test_file_dir is not None:
        test_list = jsonl_read(test_file_dir)

    save_directory = "../data/datasets"
    save_file_name = save_file_name
    save_directory = os.path.join(save_directory, save_file_name)

    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    # datasetdict 으로 변환
    train_converted = Dataset.from_generator(lambda: _gen(train_list))
    if test_list:
        test_converted = Dataset.from_generator(lambda: _gen(test_list))
        _datasetdict = text_converted = DatasetDict(
            {"train": train_converted, "test": test_converted}
        )
    else:
        _datasetdict = text_converted = DatasetDict({"train": train_converted})
    text_converted.save_to_disk(save_directory)

    print(f">> Now Upload to HF . . .")

    upload_to_hf(
        _datasetdict=_datasetdict,
        directory=save_directory,
        save_file_name=save_file_name,
        # save_directory=dataset_dir,
        hf_repo_name=hf_repo_name,
        hf_commit_message=hf_commit_message,
    )


def _conv_to_multi_chat(example: Dict[str, Any]) -> Dict[str, Any]:
    """
        load_dataset으로 불러들인 데이터세트의 example을 multi-turn chat 형식으로 변환합니다.
        
        사용:
            dataset = load_dataset('dataset_name')
            dataset = dataset.map(_conv_to_multi_chat, num_proc=64)
        
        참고:
            *DatasetDict는 dict 을 반환해야한다.
        
        Returns:
            Dict
    """
    if example.get('answer', False):    # role_specific 데이터세트일 경우
        example['messages'] = [{'role': 'user', 'content': example['question']}, {'role': 'assistant', 'content': example['answer']}]
    elif example.get('output', False):   # neuroticism 데이터세트일 경우
        example['messages'] = [{'role': 'user', 'content': example['instruction']}, {'role': 'assistant', 'content': example['output']}]
    else:                               # koalpaca 데이터세트일 경우
        example['messages'] = [{'role': 'user', 'content': example['question']}, {'role': 'assistant', 'content': example['chosen']}]
    return {'messages': example['messages']}


def add_system_prompt() -> None:
    # system prompt 추가해보기
    """
    1. orbit persona + orbit specific prompt
    2. neuroticism
    3. doctor
    4. semi-scientist persona / history_physics / humanities
    5. general persona
    """
    from datasets import load_dataset

    from prompt import (system_prompt, system_prompt_without_name,
                        orbit_role_name, orbit_role_description,
                        medician_role_name, medician_role_description, 
                        neuroticism_role_name, neuroticism_role_description,
                        semi_science_communicator_role_name, semi_science_communicator_description,
                        historian_and_physician_role_name, historian_and_physician_description,
                        humanities_scholar_role_name, humanities_scholar_description)
    
    orbit_system_prompt = system_prompt.format(role_name=orbit_role_name, role_description_and_catchphrases=orbit_role_description)
    neuroticism_system_prompt = system_prompt.format(role_name=neuroticism_role_name, role_description_and_catchphrases=neuroticism_role_description)
    medician_system_prompt = system_prompt.format(role_name=medician_role_name, role_description_and_catchphrases=medician_role_description)
    # semi_science_communicator_system_prompt = system_prompt.format(role_name=semi_science_communicator_role_name, role_description_and_catchphrases=semi_science_communicator_description)
    historian_and_physicist_system_prompt = system_prompt.format(role_name=historian_and_physician_role_name, role_description_and_catchphrases=historian_and_physician_description)
    humanities_scholar_system_prompt = system_prompt.format(role_name=humanities_scholar_role_name, role_description_and_catchphrases=humanities_scholar_description)
    
    def _add_system_prompt(data_path: str=None, 
                           save_path: str=None,
                           hf_path: str=None,
                           hf_name: str=None,
                           system_prompt: str=None,
                           persona_desc: str=None
                           ) -> None:
        """
        Jsonl data를 읽거나 DatasetDict 형태로 받아서, system prompt를 추가한 뒤, 저장합니다.
        Args:
            data_path (str): _description_
            save_path (str): _description_
        """
        def _remove_reversed(example):
            if not example["reversed"]: return example
            else:   return None

        def _remove_under_6_turns(example):  # medician 데이터 전용 필터링 함수
            return int(example["num_turns"]) >= 6  # 3038 rows 중 1366 rows 만 리턴(10 turns)

        def _remove_under_4_score(example):  # KoAlpaca 데이터 전용 필터링 함수
            return int(example["score"]) >= 4
        
        if data_path is not None:
            data = jsonl_read(data_path)
            
            
        elif hf_path is not None:
            data = load_dataset(hf_path, hf_name, split='train')
            if 'persona_data' in hf_name:
                data = data.filter(_remove_reversed)
            # if 'medician_persona' in hf_name:
            #     data = data.filter(_remove_under_6_turns)
            if 'KoAlpaca_v1.1' in hf_name:
                data = data.filter(_remove_under_4_score)
            
            if not data.to_dict().get('messages', None):
                data = data.map(_conv_to_multi_chat, num_proc=8)
                
            data_dict = data.to_dict()
            data = [dict(zip(data_dict.keys(), values)) for values in zip(*data_dict.values())]
        else:
            raise ValueError("You must provide either data_path or hf_path.")
        
        # if system_prompt is None:
        #     raise ValueError("You must provide system_prompt.")
        
        def _attach_system_prompt(example: Dict[str, Any], 
                                  system_prompt: str,
                                  persona_desc: str=None) -> Dict[str, Any]:
            if system_prompt is None:   # 이 경우 general persona 데이터로 간주 -> 페르소나 description이 column에 있는 경우로 간주.
                system_prompt = system_prompt_without_name.format(role_description_and_catchphrases=example['persona_desc'])
            example['messages'].insert(0, {"role": "system", "content": system_prompt})
            
            if not example.get('persona', None) and persona_desc:
                example['persona'] = persona_desc
            
            # return example
            return {"messages": example['messages'], "persona": example.get('persona', None)}
            
        
        data_with_system_prompt = [_attach_system_prompt(example, system_prompt, persona_desc) for example in tqdm(data, total=len(data))]
        if data_path:
            print(f"\nData path: {os.path.basename(data_path)}\nData length: {len(data)}\n-----\n")
        if hf_path:
            print(f"\nData path: {hf_path}/{hf_name}\nData length: {len(data)}\n------\n")
        for _data in data_with_system_prompt:
            jsonl_save(save_path, _data)
        
        return None

    data_and_sys = [
        {"data_path": "../data/post/multiturn_data_orbit_multi_0626_1_post.jsonl", "system_prompt": orbit_system_prompt, "persona_desc": "science_communicator"},
        # {"data_path": "../data/post/Orbit_generated_data_YH_post.jsonl", "system_prompt": semi_science_communicator_system_prompt, "persona_desc": "semi-science_communicator"},
        {"data_path": "../data/post/multiturn_data_history_physics_post.jsonl", "system_prompt": historian_and_physicist_system_prompt, "persona_desc": "historian_and_physicist"},
        {"data_path": "../data/post/multiturn_data_humanities_post.jsonl", "system_prompt": humanities_scholar_system_prompt, "persona_desc": "humanities_scholar"},
    ]
    data_and_sys_hf = [
        {"hf_path": "HEYPAL/persona_general_dataset", "hf_name": "044.persona_data", "system_prompt": None, "persona_desc": "general_persona"},
        {"hf_path": "HEYPAL/persona_general_dataset", "hf_name": "medician_persona", "system_prompt": medician_system_prompt, "persona_desc": "medician"},
        {"hf_path": "HEYPAL/persona_general_dataset", "hf_name": "neuroticism_persona", "system_prompt": neuroticism_system_prompt, "persona_desc": "neuroticism"},
        # {"hf_path": "HEYPAL/persona_orbit_dataset", "hf_name": "KoAlpaca_v1.1_orbit_v1.4.3", "system_prompt": orbit_system_prompt, "persona_desc": "science_communicator"},
    ]

    for _data in data_and_sys:
        _data_path = _data.get('data_path', None)
        _system_prompt = _data.get('system_prompt', None)
        persona_desc = _data.get('persona_desc', None)
        
        if _data_path:
            _add_system_prompt(data_path=_data_path,
                               save_path="../data/persona_total_sys_0701_1.jsonl",
                               system_prompt=_system_prompt,
                               persona_desc=persona_desc)
    
    
    for _data in data_and_sys_hf:
        hf_path = _data.get('hf_path', None)
        hf_name = _data.get('hf_name', None)
        _system_prompt = _data.get('system_prompt', None)
        persona_desc = _data.get('persona_desc', None)
        
        if hf_path and hf_name:
            _add_system_prompt(# data_path=_data,
                               hf_path=hf_path,
                               hf_name=hf_name,
                               save_path="../data/persona_total_sys_0701_1.jsonl",
                               system_prompt=_system_prompt,
                               persona_desc=persona_desc)
    
    

if __name__ == "__main__":
    # system prompt 추가하기
    from datasets import disable_caching
    disable_caching()
    add_system_prompt()
    
    
    # jsonl data를 허깅페이스에 업로드하기
    save_into_datadict(
        train_file_dir="../data/persona_total_sys_0701_1.jsonl",
        test_file_dir=None,
        save_directory="../data/datasets",
        save_file_name="Ko_persona_multiturn_v1.2-sys",
        hf_repo_name="DinoTheLewis/Ko_persona_multiturn_v1.2-sys",
        hf_commit_message="Upload Dataset - Ko_persona_multiturn_v1.2-sys",
    )
    
    # # 여러 jsonl 파일 합치기
    # file_path = ["../data/post/multiturn_data_orbit_multi_0626_1_post.jsonl",
    #              "../data/post/Orbit_generated_data_YH_post.jsonl",
    #              "../data/post/multiturn_data_history_physics_post.jsonl", 
    #              "../data/post/multiturn_data_humanities_post.jsonl",]
    # _append_jsonl(file_path=file_path, 
    #               save_path="../data/persona_total_0628_1.jsonl")

    
    # # YH data에 대한 답변 길이 추가
    # yh_data = jsonl_read("../data/post/Orbit_generated_data_YH_post.jsonl")
    
    # for idx, data in tqdm(enumerate(yh_data), total=len(yh_data)):
    #     ans_num_paragraphs = []
    #     ans_num_words = []

    #     for _turn in data['messages']:
    #         if _turn.get('role', None) == 'assistant':
    #             output = _turn['content']
    #             _num_first_answer = count_answer_length(output)
    #             ans_num_paragraphs.append(_num_first_answer[0])
    #             ans_num_words.append(_num_first_answer[1])
        
    #     data['ans_num_paragraphs'] = ans_num_paragraphs
    #     data['ans_num_words'] = ans_num_words
    #     data['url'] = None
    
    # for _data in yh_data:
    #     jsonl_save("../data/post/Orbit_generated_data_YH_post_1.jsonl", _data)