'''
모듈에 사용할 공용 함수를 저장해놓은 파일.
'''
from dotenv import load_dotenv
import os

def call_api_key(env_var_name):
    """Load the API key from the environment variables."""
    load_dotenv()
    api_key = os.getenv(env_var_name)
    if not api_key:
        raise ValueError(f"API key is not set for {env_var_name}. Please check your .env file.")
    return api_key