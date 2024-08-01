'''
Usage file.
다른 파일에서 사용하고자 할 경우, 앞에 llm_2.~ 이런식으로 진행해야함.
'''
from utils import *
from vector_db import *
from rag_chain import *
from langchain_openai import OpenAI

def main():

    api_key = call_api_key('OpenAI_API_Key')

    prompt_evaluate, prompt_generate = llm_2_prompts()

    embedding_function = OpenAIEmbeddings(openai_api_key=api_key)
    

    retriever = call_vectordb(DB_PATH="./chroma_db", 
                              embedding_function=embedding_function, 
                              chunk_size=300, 
                              chunk_overlap=0, 
                              api_key=api_key
                              )
    
    # If you printed error in set retriever, run this function first.

    llm = OpenAI(api_key=api_key)

    evaluate_chain = rag_chain(retriever=retriever, prompt=prompt_evaluate, llm=llm)
    generate_chain = rag_chain(retriever=retriever, prompt=prompt_generate, llm=llm)

    question = "와사비를 설명해줄래?"
    evaluate_result= evaluate_chain.invoke(question)
    generation_result = generate_chain.invoke(question)
    print("evaluate Result:", evaluate_result)
    print("Generation Result:", generation_result)

if __name__ == "__main__":
    main()