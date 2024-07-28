from utils import *
from run_llm3 import * 

def main(question, answer):
    '''
    definition of input, input2
    input: When you activate RAG, Your question
    answer: 
    '''
    api_key = call_api_key('OpenAI_API_Key')
    prompt = llm_3_prompt()
    llm = OpenAI(api_key=api_key)
    chain = llm_3_chain(prompt, llm)
    run_llm3(chain, question, answer)

if __name__=="__main__":
    #예문으로, 다음과 같이 실행시키면 됩니다!
    question = "커피를 설명해줄래?"
    answer = "와사비는 기생충을 퇴치하기 위해 사용됩니다. 초밥에 와사비를 함께 제공하는 이유는 그것이 기생충을 퇴치하기 위함입니다. 대부분의 날생선에는 기생충이 내장에 숨어있기 때문에, 그것을 제거하기 위해 고추냉이의 살균력을 활용하는 것입니다. 또한, 생강에도 살균 작용이 있어 식중독을 예방하는 역할을 합니다. 초밥집에서 얇게 쓴 생강을 제공하거나, 전갱이나 가다랭이 등에 생강을 곁들여 먹게 되는 것도 이와 같은 이유 때문입니다."

    main(question, answer)