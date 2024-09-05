## Description
redis 에 쌓인 유저의 리퀘스트(채팅 입력)을 (현재) 순차적으로 읽어 langgraph agent를 이용해 inference 를 수행합니다.

### client_main.py
- redis 에 쌓인 유저의 리퀘스트를 읽어들여 inference 를 수행합니다.

### server_main.py
- vllm을 이용한 model api 서버를 구동합니다.

### How to run
GPU 가 인식되는 환경에서 실행하세요. ex) runpod 등  
VRAM이 18GB 이상인 경우에 사용을 권장합니다. 10GB 이하인 경우에는 품질을 장담할 수 없습니다.  
모두 지속적으로 동작해야하므로 tmux 사용을 권장합니다.
- client_main.py
```shell
python client_main.py
```

- server_main.py
```shell
python server_main.py
```