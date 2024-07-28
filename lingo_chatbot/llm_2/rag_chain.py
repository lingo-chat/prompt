# rag_chain.py
from langchain_chroma import Chroma
from langchain_openai import OpenAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import OpenAIEmbeddings
from langchain_core.prompts import PromptTemplate
from utils import call_api_key
from llm_2.vector_db import *
import os

api_key = call_api_key('OpenAI_API_Key')

def llm_2_prompts():
    '''
    프롬프트 템플릿을 불러오는 함수:
    prompt_evaluate는 RAG 시동 유무를 결정,
    prompt_prompt_generate는 RAG 생성 작업과 관련된 프롬프트입니다.
    (추후 수정 예정.)
    '''
    prompt_evaluate = '''
You are the evaluator of the question-answer task. In the retrieved context, check whether the appropriate information exists for the user's input. If you can explain users question in retrieved context, the value of 'activate_RAG' is 'Yes'. If you can't, return 'No'.
Don't print any idea not retrieved data. And be flexible with your questions. And Don't finish your process untill print nothing.
You should print answer in json returning 1 parameter: "Answer". You must only answer Yes or No for that parameter. Responses are based on the following criteria:
- If you can explain users question in retrieved context, the value of "Answer" is "Yes".
- Otherwise, If you cannot find the answer in the retrieved context, or if the answer does not require retrieved context, the value of "Answer" is "No".
Be sure, no matter what happens, do not print out any answers. Return "No" if you do not want to print any answer.

Question: {question}

Context: {context}

[Example]
Question: 커피 좋아하세요?

"Answer": "No"
'''
    prompt_generate = '''
You are an assistant in the question answering task and are responsible for outputting the answers as json format. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
You must print only in retrieved context about the questions. Don't print any idea not retrieved data. Be flexible with your questions. (Example: What is React? -> This is a question about reAct prompting in Prompt Engineering, Not React framework.)
When you print answer, you should print answer in json returning 2 parameters: 'activate_RAG' and 'Explain'. If you can explain users question in retrieved context, the value of 'activate_RAG' is 'Yes'. If you can't, return 'No'.
And if 'activate_RAG' value is 'Yes' return the answer in 'Explain' parts, 'activate_RAG' is 'No', Print 'None'.
마지막으로, 답변을 출력할 때는 한글로 출력하세요. 그리고 정해진 형식에 맞게 json 파일로 출력해야 함을 잊지 마세요.

Question: {question}

Context: {context}

[Example]
"activate_RAG": "No",
"Explain": "I don't know"

Answer:'''
    prompt_decision = PromptTemplate.from_template(prompt_evaluate)
    prompt_generation = PromptTemplate.from_template(prompt_generate)

    return prompt_decision, prompt_generation

def call_vectordb(DB_PATH, embedding_function, chunk_size, chunk_overlap, api_key):
    '''
    예시 입력값
    chunk_size = 500, 
    chunk_overlap = 200
    DB_PATH="./chroma_db"
    embedding_function = OpenAIEmbeddings(openai_api_key=api_key)
    - openai embeddng function은 이런식으로 작성하시면 됩니다(api_key는 본인꺼 넣기!).
    '''
    if not os.path.exists(DB_PATH):
        raise ValueError(f"The specified path '{DB_PATH}' does not exist. Please check the path and ensure the vector database is saved first.")

    vectorstore = load_vectordb(DB_PATH=DB_PATH, api_key=api_key, embedding_function=embedding_function)
    retriever = vectorstore.as_retriever()
    return retriever



def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)



# 생성 모델 초기화
llm = OpenAI(api_key=api_key)


def rag_chain(retriever, prompt, llm):
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | JsonOutputParser()
    )

    return rag_chain

# Example invocation
# question = "커피 좋아하세요?"
# result_decision = rag_chain_decision.invoke(question)
# result_generation = rag_chain_generation.invoke(question)
# print("Decision Result:", result_decision)
# print("Generation Result:", result_generation)
