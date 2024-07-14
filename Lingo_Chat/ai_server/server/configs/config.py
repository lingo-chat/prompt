from pydantic import BaseModel, Field
from typing import Dict


class AIServerConfig(BaseModel):
    """
    vllm 을 구동하는 AI 서버의 configuration
    """
    llm_model_path: str
    
    num_gpus: int = 1
    gpu_memory_utilization: float = 0.90
    
    seed: int = 42
    max_model_len: int = 4096
    
    request_port: int = 2496
    ws_port: int = 8080
    secure_api_key: str