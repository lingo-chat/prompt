## Description
Redis - db 간 백업 및 불러오기 작업을 수행하는 패키지

### backup.py
- 주기적으로 redis queue를 탐색하며 백업 기준에 만족하는 채팅 히스토리를 save 합니다.

### How to run
GCP 혹은 AWS와 같은 리모트 공간에서 동작시키길 권장합니다.  
모두 지속적으로 동작해야하므로 tmux 사용을 권장합니다.
- backup.py
```shell
python backup.py
```