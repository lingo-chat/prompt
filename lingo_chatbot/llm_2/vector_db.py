from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_openai import OpenAI
from utils import call_api_key
from chromadb.utils import embedding_functions



def save_vectordb(file_path, chunk_size, chunk_overlap, DB_PATH, api_key):
    api_key = call_api_key('OpenAI_API_Key')
    loader = TextLoader(file_path)
    documents = loader.load()


    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, 
                                                chunk_overlap=chunk_overlap)

    splits = text_splitter.split_documents(documents)
    embedding = OpenAIEmbeddings(openai_api_key=api_key)

    vectorstore = Chroma.from_documents(documents=splits, 
                                    embedding=embedding, 
                                    persist_directory=DB_PATH)    
    return vectorstore

def load_vectordb(DB_PATH, api_key, embedding_function):
    vectorstore =  Chroma(persist_directory=DB_PATH, 
                       embedding_function=embedding_function)
    return vectorstore

