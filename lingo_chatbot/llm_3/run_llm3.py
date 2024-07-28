from utils import *
from langchain_openai import OpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser


def llm_3_prompt(): 
    Prompt_template = '''
    You will help evaluate whether the retrieved context has properly addressed the user's question. 
    If the answer to the question is correctly presented, output 'Yes'. If it is not properly reflected, output 'No'.

    [Output Example]
    Answer:"Yes"


    Question: {input}
    Answer: {response}
    '''
    
    prompt = PromptTemplate(
            input_variables=['input', 'response'], 
            template=Prompt_template
        )
    return prompt

def llm_3_chain(prompt, llm):
    return prompt | llm | StrOutputParser()

def run_llm3(llm_chain, input_text, response_text):
    response = llm_chain.invoke({"input":input_text, "response":response_text})
    print(response)