import re
import jsonlines

from tqdm import tqdm

from .utils import jsonl_save

class PostProcessing:
    def __init__(self, file_dir: str, save_dir: str):
        self.file_dir = file_dir
        self.save_dir = save_dir

        self.dataset = self.load_dataset()
    
    def load_dataset(self):
        jsonl_data = []

        with jsonlines.open(self.file_dir) as f:
            for line in f.iter():
                jsonl_data.append(line)
        
        return jsonl_data
    
    @classmethod
    def singleturn(cls, file_dir: str, save_dir: str):
        """
        Singleturn 데이터를 후처리하는 함수입니다.
        
        _dict: {'instruction': '', 'output': '', 'org_output': '', 'url': ''} OR
        _dict: {'instruction': '', 'output': '', 'org_output': '', 'url': '', 'score': '', 'score_feedback': ''}
        """
        inst = cls(file_dir=file_dir, save_dir=save_dir)
        
        for idx, _dict in tqdm(enumerate(inst.dataset), total=len(inst.dataset)):
            # 메인 후처리 함수 호출
            poutput = inst._post_processing(
                instruction=_dict["instruction"], content=_dict["output"]
            )
            
            if poutput is not None:
                _result = {
                    "instruction": _dict["instruction"],
                    "output": poutput,
                    "org_output": _dict["org_output"],
                    "url": _dict["url"],
                }
                if _dict.get("score", None):
                    _result["score"] = _dict["score"]
                    _result["score_feedback"] = _dict["score_feedback"]
                    
                else:
                    pass # continue    

                jsonl_save(
                    dir=save_dir,
                    json_data=_result,
                )
            
    @classmethod
    def multiturn(cls, file_dir: str, save_dir: str):
        """
        Multiturn 데이터를 후처리하는 함수입니다.
        """
        inst = cls(file_dir=file_dir, save_dir=save_dir)
        
        for idx, _dict in tqdm(enumerate(inst.dataset), total=len(inst.dataset)):
            _result_messages = []
            
            for _turn in range(0, len(_dict['ans_num_paragraphs'])):
                question = _dict['messages'][_turn*2]['content']
                answer = _dict['messages'][(_turn*2)+1]['content']
                
                # 메인 후처리 함수 호출
                poutput = inst._post_processing(
                    instruction=question, content=answer
                )
                
                if poutput is not None:
                    _result_messages.append({'role': 'user', 'content': question})
                    _result_messages.append({'role': 'assistant', 'content': poutput})
                else:
                    print(f"Error: poutput is None in idx: {idx}\n\n")
            
            _result = {
                'instruction': _dict['instruction'],
                'messages': _result_messages,
                'ans_num_paragraphs': _dict['ans_num_paragraphs'],
                'ans_num_words': _dict['ans_num_words'],
                'num_turns': _dict['num_turns'],
                'url': _dict['url'],
            }
            
            # 생성된 데이터 저장
            jsonl_save(save_dir, _result)
        
        return None


    def _post_processing(self, instruction: str, content: str):
        """
        main post processing 함수
        """
        pattern_topic = r"주제:\s|[<>]"
        pattern_cot = "given question's topic"
        try:
            pcontent = content
            if instruction in content:  # 질문 그대로 생성하는 것 교체
                _sub = "이것"
                if content[len(instruction) + 1 :].startswith(" "):
                    pcontent = content.replace(instruction + " ", _sub)
                else:
                    pcontent = content.replace(instruction, _sub)

            if (
                '"' in pcontent
            ):  # 큰 따옴표(speech mark) 제거 - 2개만 있는 경우가 거의 '인용' 형태.
                if pcontent.count('"') <= 2:
                    pcontent = re.sub('"', "", pcontent)

            pcontent = re.sub(pattern_topic, "", pcontent)  # '주제' 라는 말 제거
            pcontent = re.sub(r"#{1,}", "", pcontent)  # # 제거
            pcontent = re.sub(
                r"\n{1,}", r"\n\n", pcontent
            )  # 하나 이상의 줄바꿈을 두 개로 변경(가독성)
            # pcontent = pcontent.replace('\n', '\n\n')
            # pcontent = re.sub(r'\s{2,}', '', pcontent).strip()  # end. 공백 2개 이상 제거
            # pcontent = re.sub(r"\\n", r'\n', pcontent)
            pcontent = pcontent.strip()
            if pcontent[-1] == '"':
                pcontent = pcontent[:-1]
            
            if pattern_cot in pcontent:  # cot 유도 문구가 있으면 그냥 저장 x
                return None
        except:
            return content

        return pcontent
    

# if __name__ == '__main__':
#     from utils import jsonl_save
# 
#     ps = PostProcessing.multiturn(file_dir='../data/multiturn_data_0626_1.jsonl', 
#                                   save_dir='../data/multiturn_data_0626_1_post2.jsonl')