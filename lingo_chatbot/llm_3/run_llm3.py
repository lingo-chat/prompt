from utils import *
from langchain_openai import OpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser


def rag_evaluation_prompt(): 
    Prompt_template = '''
You will help evaluate whether the retrieved context has properly addressed the user's question. 
If the answer to the question is correctly presented, output 'Yes'. If it is not properly reflected, output 'No'.
You must print output: only "Yes" or "No".

[Output Example]
evaluation result:"No"


Question: {input}
RAG output: {response}
    
evaluation result:'''
    
    prompt = PromptTemplate(
            input_variables=['input', 'response'], 
            template=Prompt_template
        )
    return prompt

def rag_eval_chain(prompt, llm):
    return prompt | llm | StrOutputParser()

def run_rag_eval_chain(evaluation_chain, user_input, rag_answer):
    try:
        print(f"Running evaluation chain with input: {user_input}, rag_answer: {rag_answer}")
        result = evaluation_chain.invoke({"input": user_input, "response": rag_answer})
        print(f"Evaluation chain result: {result}")
        # Check if result is a dictionary
        if isinstance(result, dict):
            return result.get("evaluation_result", None)
        # If result is a string, return it directly
        return result
    except Exception as e:
        print(f'Error in run_rag_eval_chain: {e}')
        raise
