# Description
### 데이터 생성이 필요한 이유
1. 싱글턴으로만 학습한 페르소나 모델은 멀티턴으로 대화를 계속 이어나가려고 할 때 답변의 퀄리티에 문제가 생긴다.  
    - 첫 번째로, 궤도의 말투 중 하나인 '이거 참 재밌습니다' 라는 말은 대화에서 한 두번 정도만 등장하는 것이 재미요소이지만, 멀티턴으로 대화를 이어나가려고 할 때 계속 반복하는 경향이 첫 번째 문제점.
    - 두 번째로, 첫 번째 답변 이후 대화를 이어나가려고 할 때, 모델의 답변이 첫 번째 답변에 비해 매우 짧아지는 경향을 보이는 것이 두 번째 문제점.
    - 세 번째로, 직전의 모델이 답변에 '강하게' attention 하여, 모델의 답변이 어떤 질문이던 상관없이 반복되는 경향을 보이는 것이 세 번째 문제점.
2. 이를 극복하기 위해, 행동을 덧붙이는 추가 프롬프트를 멀티턴 입력에 postfix로 붙여 모델에 전달할 수 있다.  
    - 예를 들어, '성격을 유지해서 대화를 이어가시오' 와 같은 프롬프트를 추가할 수 있으나,
    - 하지만 예상되는 문제점은 다음과 같다.  
        - 추가적인 프롬프트로 context length 관리를 위한 정규식 작업이 필요하다. 고정된 prompt 가 아닌 경우 이 작업은 더 복잡해진다.
        - 추가되는 프롬프트로 인해 이 인풋은 학습된 형태가 아니게 되므로 예상치 못한 답변을 생성할 수 있다.
        - 모델의 답변이, 이전 모델의 답변을 반복하는 경우는 추가되는 프롬프트로는 해결할 수 없음.
    - 따라서, multiturn data를 생성하여 추가 학습 할 필요성이 있다.

### 데이터 생성 방식
- 참고 논문: Ultrachat  
- 참고한 코드: museko
- 원본 데이터: KoAlpaca v1.1
- 데이터 생성 모델: Gemini pro 1.5 free version
- How data were created:  
    - 유저의 1번째 질문은 KoAlpaca v1.1에서 추출. 이 질문-답변 세트로부터 궤도 페르소나 데이터 생성(single turn; KoAlpaca_v1.1_orbit_v1.4.3)
    - 유저의 2번째 질문부터는 Ultrachat 에서 사용한 multiturn 자동 생성 프롬프트를 사용하여 생성.
    - 2 개의 Gemini Agent가 각각 User, '궤도' 역할을 담당하며 single turn 데이터를 Multi turn 데이터로 확장  

### 데이터 퀄리티 컨트롤
- 저품질 데이터 필터링: proprietary model을 사용하여(되도록 데이터를 생성한 모델이 아닌 모델 사용 지향) 생성된 multiturn data의 퀄리티를 scoring & filtering
- 점수화 기준: 문맥적 자연스러움 / 전문성 / 답변의 길이 / ...
- 필터링 된 데이터 예시  
    1. 저품질 데이터 예시: ...
    2. 고품질 데이터 예시: ...