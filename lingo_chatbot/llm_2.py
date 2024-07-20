'''
RAG가 적용된 llm을 만들때 사용할 프로토타입 코드
'''

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import OpenAIEmbeddings
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
import os


# Load environment variables
load_dotenv()
api_key = os.getenv('OpenAI_API_Key')

# Ensure the API key is loaded correctly
if not api_key:
    raise ValueError("API key is missing. Please ensure it is set in the environment variables.")

# 마크다운 파일 경로
file_path = 'rag_example.jsonl'

loader = TextLoader(file_path)
documents = loader.load()
chunk_size = 500
chunk_overlap = 200
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=chunk_size, chunk_overlap=chunk_overlap
)

# Split
splits = text_splitter.split_documents(documents)
embedding = OpenAIEmbeddings(openai_api_key=api_key)
# 생성 모델 초기화
vectorstore = Chroma.from_documents(documents=splits, embedding=embedding)

# Retrieve and generate using the relevant snippets of the blog.
retriever = vectorstore.as_retriever()

prompt_generate = '''
You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
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

prompt_decide = '''
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

prompt_decision = PromptTemplate.from_template(prompt_decide)
prompt_generation = PromptTemplate.from_template(prompt_generate)

# 생성 모델 초기화
llm = OpenAI(api_key=api_key)

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

rag_chain_decision = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt_decision
    | llm
    | StrOutputParser()
)

rag_chain_generation = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt_generation
    | llm
    | StrOutputParser()
)

# Example invocation
question = "커피 좋아하세요?"
result_decision = rag_chain_decision.invoke(question)
result_generation = rag_chain_generation.invoke(question)
print("Decision Result:", result_decision)
print("Generation Result:", result_generation)
