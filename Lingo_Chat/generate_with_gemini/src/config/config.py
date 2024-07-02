from pydantic import BaseModel, Field
from typing import Dict

##########
### Inference Configurations
##########
class ArgsConfig(BaseModel):
    """
    기본적으로 사용하는 configuration
    """
    temperature: float
    top_p: float
    seed: int
    max_tokens: int
    frequency_penalty: float = 1.2
    presence_penalty: float = 0.0
    repetition_penalty: float = 1.0

class ModelInferenceConfig(ArgsConfig):
    """
    Model 추론 시 추가적으로 사용하는 configuration

    tensor_parallel_size 는 vllm serving 시 사용합니다.
    """
    model_path: str
    tokenizer_path: str
    model_name: str
    tensor_parallel_size: int = 1

class MultiturnGenerationConfig(BaseModel):
    """
    Multiturn Generation 시 사용하는 configuration
    """
    key_list: list
    model_name: str
    persona_name: str
    use_answer_prefix: bool = False
    target_turn: int

class JsonConfig(BaseModel):
    """
    Json 파일을 읽을 때 사용하는 configuration
    """
    inspiring_json_dir: str
    start_idx: int = 0
    jsonl_save_dir: str
    filtered_save_dir: str
    
class ScoringConfig(BaseModel):
    """
    Scoring 시 사용하는 configuration
    """
    scoring_prompt: str
    score_threshold: float
    score: float = 0.0

class Config(BaseModel):
    """
    전체적인 configuration
    """
    model_inference: ModelInferenceConfig
    multiturn_generation: MultiturnGenerationConfig
    json: JsonConfig
    scoring: ScoringConfig

# ##########
# ### Prompt Configurations
# ##########
# class SingleTurnGenerationPromptConfig(BaseModel):
#     """
#     Single Turn Generation 시 사용하는 configuration prompts
#     """
#     system_prompt: str
#     single_turn_scoring_prompt: str

# class MultiTurnGenerationPromptConfig(SingleTurnGenerationPromptConfig):
#     """
#     Multi Turn Generation 시 사용하는 configuration prompts
#     """
#     next_turn_question_induce_prompt: str
#     next_turn_answer_induce_prompt: str
#     multi_turn_scoring_prompt: str
    
# class PersonaSingleTurnGenerationPromptConfig(SingleTurnGenerationPromptConfig):
#     """
#     Persona Single Turn Generation 시 사용하는 configuration prompts
#     """
#     persona_role_name: str
#     persona_description: str
    
# class PersonaMultiturnGenerationPromptConfig(MultiTurnGenerationPromptConfig, PersonaSingleTurnGenerationPromptConfig):
#     """
#     Persona Multiturn Generation 시 사용하는 configuration prompts
#     """
#     pass



##########
### DB & Generation result Configurations
##########
class QAResult(BaseModel):
    question: str
    answer: str

# class OutputConfig(BaseModel):
#     QA: Dict[str, QAResult]

class SingleTurnResultFormat(BaseModel):
    model_name: str
    sys_prompt: str
    args: ArgsConfig
    output: Dict[str, QAResult]
