Prompt Engineering 
===
Prompt Engineering Techniques
정의(Definition):  생성형 AI 모델이 해석하고 이해할 수 있는 지시사항을 구성하는 과정

- 프롬프트(Prompt): AI가 수행해야 할 작업을 설명하는 자연어 텍스트

# 목차

1. **[Shot-based Prompting](#0-shot-based-prompting)**
    1. Zero-Shot Prompting
    2. One Shot & Few-Shot Prompting(In context learning)
    3. Shot-based Prompting 기법의 한계
2. **[Chain of Thought(CoT) Prompting](#1-chain-of-thoughtcot-prompting)**
    1. Zero-Shot CoT Prompting
    2. Automatic Chain-of-Thought (Auto-CoT)
- [Self-Consistency](#2-self-consistency)
- [Generated Knowledge Prompting](#2-generated-knowledge-prompting)
- [Prompt Chaining](#prompt-chaining)
- [Tree of Thoughts](#tree-of-thoughtstot)
- [Retrieval Augmented Generation](#retrieval-augmented-generationrag)
- [Automatic Reasoning and Tool-use](#automatic-reasoning-and-tool-use-art)
- [Automatic Prompt Engineer](#automatic-prompt-engineer-ape)
- [Active-Prompt](#active-prompt)
- [Directional Stimulus Prompting](#directional-stimulus-prompting)
- [Program Aided Language Models](#program-aided-language-models프로그램-지원-언어모델)
- [ReAct](#react-prompting)
- [Reflexion](#reflexion)
- [Multimodal CoT Prompting](#multimodal-cot-prompting)

# Prompt Engineering 의 질문 기법들

## 0. Shot-based Prompting

- 각각의 방식의 구분 기준은 예시를 얼마나 제공하냐에 따라 갈린다.
- 가장 기본적이고, 간단한 방법

### 0-0. Zero-Shot Prompting

- 가장 기본적인 프롬프트 활용법
    - 예제를 제공하지 않고 작업을 수행하라고 요청하는 것
    - 모델은 일반적인 지식과 문맥 이해력을 기반으로 답변.

- `Zero-Shot Prompting` 예시 (GPT-4, 3회 출력)
    
    ```markdown
    ”개에 대해서 한 줄로 설명해줘”
    
    1. 개는 친근하고 충성스러운 성격을 가진 동물로, 인간의 친구이자 반려동물로 널리 사랑받고 있습니다.
    2. 개는 인간의 오랜 친구이며, 충성심이 강하고 다양한 종류가 있는 포유동물입니다.
    3. 개는 사람과 함께 살아가는 가장 친근한 반려동물 중 하나로, 충성심과 사회성을 가진 동물입니다.
    ```
    

---

### 0-1 One Shot & Few-Shot Prompting(In context learning)

- 예시(`Shot`)를 제공하여 질문하는 프롬프트 방법
- 1개의 예시를 제시하면 `One-Shot`, 그 이상을 제시하면 `Few-Shot` 에 해당한다.
- 보통 2~5 개 정도를 제공하면 `Few-Shot`의 범주에 들어간다.
- **In context learning 에서 파생된 개념으로, 이는 이후에 적용되는 기법에도 영향을 미침.**

- `One-Shot Prompting` 예시 (GPT-4, 3회 출력)
    
    ```markdown
    ”개에 대해서 한 줄로 설명해줘. 예시: 고양이는 반려동물의 일종으로, 독립적 성향이 강합니다”
    
    1. **개는 반려동물의 일종으로,** 충성심이 강하고 사람과의 교류를 좋아합니다.
    2. **개는 반려동물의 일종으로,** 인간과의 강한 유대감과 높은 충성심을 보여줍니다.
    3. **개는 반려동물의 일종으로,** 사회성이 높고 사람에게 충성심이 강합니다.
    ```
    
- `Few-Shot Prompting` 예시
    
    ```markdown
    Great product, 10/10: positive
    Didn't work very well: negative
    Super helpful, worth it: positive
    It doesnt work!: negative
    I hope so.:
    
    ---
    neutral
    ```
    

- 보통 `Few-Shot Prompting`이 다른 예시들보다 균일하고, 정확한 결과를 출력함.
- 일반적으로 `Few-Shot Prompting`이 다른 방법보다 선호.

---

### 0-2 예시를 활용한 Prompting 기법의 한계(**Limitations of Few-shot Prompting)**

- 많은 작업에서 `Few-Shot Prompting`은 효과적인 성능을 보이지만 한계가 존재함.
- 특히 복잡한 추론 작업을 처리할 경우, 오답을 도출하는 경우가 존재함.

- `Zero & Few-Shot Prompting` - GPT 3.5 / GPT 4 현재는 해결하나, 이전에는 풀지 못하던 문제
    
    ```markdown
    - Zero Shot
    	
    	이 집합{15, 32, 5, 13, 82, 7, 1}에서 홀수를 모두 더하면 짝수이다.
    	
    	A:
    	
    	---
    	
    	네, 이 집합의 홀수를 모두 더하면 짝수인 107입니다.
    
    - Few Shot
    
    	이 집합 {4, 8, 9, 15, 12, 2, 1}에서 홀수의 합은 짝수입니다.
    	A: 답은 거짓입니다.
    	
    	이 집합 {17, 10, 19, 4, 8, 12, 24}에서 홀수의 합은 짝수입니다.
    	A: 정답은 참입니다.
    	
    	이 집합 {16, 11, 14, 4, 8, 13, 24}에서 홀수의 합은 짝수입니다.
    	A: 답은 참입니다.
    	
    	이 집합 {17, 9, 10, 12, 13, 4, 2}에서 홀수의 합은 짝수입니다.
    	A: 답은 거짓입니다.
    	
    	이 집합 {15, 32, 5, 13, 82, 7, 1}에서 홀수의 합은 짝수입니다.
    	A:
    
    	---
    	
    	답은 참입니다.
    	
    ---
    
    밑에는 현 시점 GPT 3.5를 활용한 답변
    
    	이 집합{15, 32, 5, 13, 82, 7, 1}에서 홀수를 모두 더하면 짝수이다.
    	
    	A:
    	
    	---
    	
    	맞습니다. 이 집합에서 홀수를 모두 더하면 15 + 5 + 13 + 7 + 1 = 41이 되고, 이는 홀수입니다. 하지만 집합에서 홀수를 제외한 나머지 숫자들은 모두 짝수입니다.
    ```
    

- 이런 복잡한 추론에서의 오류를 해결하기 위해 `Chain of Thought Prompting` 이 등장하였음.

---

## 1. Chain of Thought(CoT) Prompting

- 기존의 예시를 제시하는 방식(`Few-Shot Prompting`) 에서 발전된 질문 기법을 갖춤.
    - 중간 추론 단계를 제공하여 복잡한 추론을 할 수 있도록 하는 방법임.
    - 단답형 프롬프트와 결합하면 복잡한 추론을 요하는 작업에서 향상된 결과를 확보할 수 있다.
- 위에서 말한 경우를 토대로 작성한 `Chain of Thought Prompt` 예문
    
    ```markdown
    집합 {4, 8, 9, 15, 12, 2, 1}에서 홀수를 모두 더하면 짝수야.
    답변: 홀수(9, 15, 1)를 모두 더하면 25가 돼. 위의 명제는 거짓이야.
    
    집합 {17, 10, 19, 4, 8, 12, 24}에서 홀수를 모두 더하면 짝수야.
    답변: 홀수(17, 19)를 모두 더하면 36이 돼. 위의 명제는 참이야.
    
    집합 {16, 11, 14, 4, 8, 13, 24}에서 홀수를 모두 더하면 짝수야.
    답변: 홀수(11, 13)를 모두 더하면 24가 돼. 위의 명제는 참이야.
    
    집합 {17, 9, 10, 12, 13, 4, 2}에서 홀수를 모두 더하면 짝수야.
    답변: 홀수(17, 9, 13)를 모두 더하면 39가 돼. 위의 명제는 거짓이야.
    
    집합 {15, 32, 5, 13, 82, 7, 1}에서 홀수를 모두 더하면 짝수야.
    답변:
    
    ---
    
    홀수(15, 5, 13, 7, 1)를 모두 더하면 41이 돼. 위의 명제는 거짓이야.
    ```
    
- 다만, `Chain of Thought`은 크기가 충분히 큰 대규모 언어모델에서만 발생하는 특성이라 학계에서 주장하고 있음(**상대적으로 작은 사이즈의 LLM을 이용할 경우 검증이 필요함.**)

### 1-0 Zero-Shot CoT Prompting


- `Zero-Shot Prompting`에 `“단계별로 생각하기(Let's think step by step)”` 을 추가하는 방법.
    - 다르게 표현하자면, AI에게 생각할 시간을 주는 기법 중 하나.
- Zero_Shot Cot 기법을 활용한 문제 풀이(클로바 Ai 활용)
    
    ```markdown
    나는 시장에 가서 사과 10개를 샀어. 나는 사과 2개를 이웃에게 주고, 2개를 수리공에게 주었어. 그리고 사과 5개를 더 사서 1개는 내가 먹었어. 사과가 몇 개나 남았니? 답만 말해줘.
    (정답: 10개)
    
    ---
    
    사과가 8개 남았습니다. (대부분의 경우 정답을 출력하나, 몇몇 경우에서 오답을 출력함.)
    
    ---
    
    Zero-Shot CoT를 적용한 문제질문
    
    나는 시장에 가서 사과 10개를 샀어. 나는 사과 2개를 이웃에게 주고, 2개를 수리공에게 주었어. 그리고 사과 5개를 더 사서 1개는 내가 먹었어. 사과가 몇 개나 남았니?
    
    **단계별로 생각해 보자.
    
    ---**
    
    단계 1: 처음에 사과 10개를 샀습니다.
    단계 2: 이웃과 수리공에게 각각 2개씩 총 4개를 주었습니다.
    단계 3: 사과 5개를 더 샀습니다.
    단계 4: 새로 산 사과 중 1개를 먹었습니다.
    
    남은 사과의 개수를 계산해 보면,
    
    10개 (처음 산 사과) - 4개 (이웃과 수리공에게 준 사과) + 5개 (새로 산 사과) - 1개 (먹은 사과) = 10개
    
    따라서, 남은 사과의 개수는 10개입니다.
    
    ---
    ```
    

- 간단한 프롬프트 한줄만으로 많은 효과를 이끌어낼 수 있드는 점에서 장점이 있음.
- 프롬프트에 사용할 예시가 부족할 경우, 효과적으로 사용할 수 있음.

---

### 1-2 Automatic Chain-of-Thought (Auto-CoT)

- CoT 프롬프팅을 적용하는 방법에서 약간의 수작업을 더하면, 케이스에서 효과적이고, 다양한 사례를 도출할 수 있음 → `Auto-CoT`
- [Zhang et al. (2022)](https://arxiv.org/abs/2210.03493)(`Auto-CoT`관련 논문)에서 해당 방법은 크게 2 단계로 구분된다:
    1. **Question Clustering**
        1. 각 질문을 `Sentence BERT`로 벡터화 함.
        2. contextualized(문맥화, 상황화)된 벡터값들을 평균화 시킴
        3. 고정된 크기의 질문 표현 형성(vectors are averaged to form a fixed-sized question representation)
        4. 질문 표현을 대상으로 K-means 군집화를 진행 → K개의 질문 군집 생성
        5. 각각의 질문 클러스터 i를 i 중심까지 정렬하여 리스트(q)로 만들어 i에 대한 거리의 오름차순으로 정렬.
    2. **Demonstaration Sampling**
        1. 질문의 군집화: 군집화된 질문들에 대해 CoT 생성. 각 군집 중심에 가까운 질문부터 고려.
        2. Demonstration 생성: 각 군집마다 선택된 질문에 대해 CoT를 만들어 예제를 생성. 
            - 이 예제에는 포함되는 것들
                - 질문(Q)
                - rationale(이론적 해석; 풀이 과정에 가까운 의미??)
                - 답변(answer)
        3. 이 예제 생성 과정에서 `Zero-Shot CoT`적용
            - 예시와 같이 AI가 자동적으로 `Zero-Shot CoT` 적용하여 문제를 해결함.
                
                ```markdown
                Q: While shopping for music online, Zoe bought 3 country albums and 5
                pop albums. Each album came with a lyric sheet and had 3 songs. How
                many songs did Zoe buy total?
                A: **Let’s think step by step.** Zoe bought 3 country albums. Each album has 3
                songs. So she bought 3*3=9 songs from the country albums. Zoe bought 5
                pop albums. Each album has 3 songs. So she bought 5*3=15 songs from
                the pop albums. Zoe bought 9+15=24 songs in total. The answer is 24.
                Q: ...
                ```
                
        4. Heuristic 적용: 최종적으로 i번째 군집에 대한 후보 Demonstration인 d(i)j가 생성됨. 최종적으로 질문, 합리적 근거, 답변이 종합된 형태로 구성됨.
            - Heuristic 선정 시 간단한 휴리스틱을 따라 질문과 합리적 근거가 간단한 것을 우선시
            - 질문: 60 token 이하, rationale 5토큰 이하의 것을 채택함.

---

## 2. Self-Consistency

- 기존의 프롬프트 엔지니어링에서 발전된 형태의 기법
    - CoT(Chain of Thought)에서 사용되는 `Greedy Algorithm Decode` 대체하는 것을 목표로 제작.
    - Few-Shot CoT를 이용하여 여러 추론 경로를 샘플링 하고, 여러번의 프롬프트 생성 과정을 거쳐 가장 일관된 답을 선택(동일 프롬프트에서 결과 출력)
- 최종적으로 산술 및 상식적 추론과 관련된 작업에서 CoT Prompt의 성능을 향상시킬 수 있다.
- [**Self-Consistency Improves Chain of Thought Reasoning in Language Models(2022)](https://arxiv.org/pdf/2203.11171.pdf) 참조**


- 그림을 보면, 위쪽에서는 CoT 하나만을 이용하여 방식으로, 오답이 나왔음을 볼 수 있다.
- 밑에 그림(Self-consistency)
    - 프롬프트를 `Few-shot CoT`로 구성
    - LLM이 다양한 방식으로 문제에 접근할 수 있는 예시 제공(`Few-shot CoT`)
    - 결과를 여러 번 출력하여, 최종적으로 결과가 채택됨.

- 결론적으로, 한 개의 정답을 출력하는 기존 방식이 아닌, 여러 개의 결과를 종합한 결론을 내리기에, 추론의 정확성 및 일관성을 개선할 수 있게됨.


- **GSM8K 예시**는 주어진 문제에 대한 그리디 디코딩과 샘플링된 경로의 답변을 비교.
    - 그리디 디코딩은 오답인 40을 도출했지만, 샘플링된 경로는 정답인 25를 도출합니다.
- **StrategyQA 예시**는 그리디 디코딩이 잘못된 정보를 포함하는 반면, 샘플링된 경로는 정답을 도출한다는 것을 보여줌.
    - 여기서 그리디 디코딩은 알바니(Albany)를 가장 인구가 많은 도시로 잘못 식별,
    - 샘플링된 경로는 정답을 도출.

이러한 예시들은 셀프 컨시스턴시가 그리디 디코딩보다 추론의 정확성과 일관성을 개선할 수 있음을 보여줍니다. 이를 통해 모델이 다양한 경로를 탐색하여 가장 정확한 답을 얻을 수 있습니다.

- 단, Self-consistency의 조기 정확도는 높지 않으며, 샘플링된 추론 수가 증가할수록 정확성이 높아지는 경향이 있음.

---

## 2. Generated Knowledge Prompting

- LLM이 최종 정답을 생성하기 전에 LLM에 주어진 질문 및 프롬프트에 유용할만한 정보들을 생성하는 것.

- 진행 방법(예시)

1. 몇 가지 지식을 생성함(`Knowledge Generation`)
    
    ```markdown
    
    Generate 10 facts about the Kermode bear:
    
    ---
    
    1. The Kermode bear, also known as the Spirit Bear, is a rare subspecies of the American black bear found in British Columbia, Canada.
    
    2. The Kermode bear has a unique white or cream-colored coat, which is caused by a recessive gene.
    
    3. The Kermode bear is a symbol of hope and renewal for the First Nations people of British Columbia.
    
    4. The Kermode bear is a protected species and is listed as a species of special concern by the Committee on the Status of Endangered Wildlife in Canada.
    
    ```
    
2. 제공된 지식을 이용하여 질문에 더 정확하게 대답하게 함(`Knowledge Intergration`)
    
    ```markdown
    
    1. The Kermode bear, also known as the Spirit Bear, is a rare subspecies of the American black bear found in British Columbia, Canada.
    
    2. The Kermode bear has a unique white or cream-colored coat, which is caused by a recessive gene.
    
    3. The Kermode bear is a symbol of hope and renewal for the First Nations people of British Columbia.
    
    4. The Kermode bear is a protected species and is listed as a species of special concern by the Committee on the Status of Endangered Wildlife in Canada.
    
    Use the above facts to write a one paragraph blog post about the Kermode bear:
    
    ---
    
    The Kermode bear, also known as the Spirit Bear, is a rare subspecies of the American black bear found in British Columbia, Canada. This unique bear has a white or cream-colored coat, caused by a recessive gene, and is a symbol of hope and renewal for the First Nations people of British Columbia. The Kermode bear is a protected species and is listed as a species of special concern by the Committee on the Status of Endangered Wildlife in Canada, making it an important part of the region's biodiversity.
    
    ```
    

---

## Prompt Chaining

- 한 개의 작업을 여러 하위 작업으로 분할 하는 것.
- 상세한 프롬프트를 만들고자 할 때 LLM이 처리하기 까다로운 복잡한 작업을 AI가 쉽게 해결하게 할 수 있는 방법.

- 예제(https://www.promptingguide.ai/kr/techniques/prompt_chaining 참조)
    - 문서를 가져온 후, 그 문서에서 관련 인용문을 추출함, 그리고 인용문을 제거한 후, 질문에 대해 답변할 수 있도록 세팅한다면?

---

## Tree of Thoughts(ToT)

- 최근에 나온 개념으로, CoT 기법을 일반화 하여, 여러 중간 단계를 만든 후, 이 과정들을 거쳐 체계적으로 추론 과정을 진행하는 방식
    
    → LM이 문제 해결에 대해 다양한 생각(Thought)을 생성하고 평가할 수 있도록 하는 방법
    
- 각각의 생각(Thought)들은 문제 해결을 위한 중간 단계로, 일련의 언어적 시퀀스(Coherent Language Sequences)를 나타낸다.
    - `Coherent Language Sequences`: 일련의 텍스트로, 문장과 같은 단어의 단락을 의미함.
        - 역할
            - ToT에서 문제 해결 과정에서 중간 단계로서 기능함
            
            → (LLM이 문제 해결을 하기 위한 논리적 단계를 텍스트로 표현)
            
            - 논리적 추론을 보여주어 추론 방향을 제시하고, 문제 해결 경로를 만듦.
                
                이는 일관적인 흐름으로 나타나게 됨.
                
            - 트리 구조에서 노드를 형성함. (각 노드: 문제 해결에서 특정 단계, 생각.)

- ToT의 구조


### ToT의 진행과정

[Tree of Thoughts: Deliberate Problem Solving with Large Language Models](https://arxiv.org/pdf/2305.10601.pdf)

- 기술된 내용을 GPT에 넣어 나온 내용을 정리

---

### ToT의 기본 아이디어

- **트리 구조**: ToT는 문제 해결을 위한 추론 경로를 트리 구조로 표현합니다. 각 노드는 부분 해결책을 나타내며, 각 가지(branch)는 문제 해결을 위한 연산(operators)을 나타냅니다.
- **탐색 및 추론**: ToT는 다양한 탐색 알고리즘(예: 너비 우선 탐색, 깊이 우선 탐색)을 사용하여 트리 구조에서의 추론 경로를 체계적으로 탐색합니다.

### ToT 프롬프팅의 주요 구성 요소

1. **생각의 분해(Thought Decomposition)**:
    - ToT는 문제를 중간 단계의 생각(thoughts)으로 분해하여, 문제 해결을 위한 명확한 경로를 제공합니다.
    - 분해된 생각의 크기는 다양하며, 문제 유형에 따라 다를 수 있습니다. 예를 들어, 크로스워드 퍼즐에서는 단어, Game of 24에서는 수학적 표현, 창작 글쓰기에서는 문단 단위로 생각을 분해할 수 있습니다.
2. **생각 생성기(Thought Generator)**:
    - 주어진 트리 상태에서 다음 단계의 생각을 생성하는 데 사용됩니다.
    - 두 가지 전략이 있습니다:
        - **i.i.d. 샘플링**: 독립적으로 샘플링하여 다양한 생각을 생성합니다. 이는 더 많은 다양성을 제공하며, 창작 글쓰기와 같은 풍부한 생각 공간에 적합합니다.
        - **순차적 제안**: 순차적으로 샘플링하여 중복을 피하고 더 제한된 생각 공간에서 다양한 생각을 생성할 수 있습니다. 이는 크로스워드 퍼즐처럼 각 생각이 단어 또는 짧은 구문인 경우에 유용합니다.
3. **상태 평가(State Evaluation)**:
    - 트리 구조에서 다양한 상태를 평가하여 문제 해결에 얼마나 가까운지 측정합니다.
    - 두 가지 접근 방식이 있습니다:
        - **독립적으로 상태 평가**: 각 상태를 독립적으로 평가하여 값(예: 1~10 스케일) 또는 분류(예: 가능/불가능)를 생성합니다.
        - **상태 투표**: 여러 상태를 비교하여 가장 유망한 상태에 투표합니다. 이는 여러 부분 해결책을 비교하고 가장 유망한 것을 선택하는 데 유용합니다.
4. **탐색 알고리즘(Search Algorithm)**:
    - ToT에서는 다양한 탐색 알고리즘을 사용할 수 있습니다. 두 가지 간단한 탐색 알고리즘이 제안됩니다:
        - **너비 우선 탐색(BFS)**: 매 단계에서 가장 유망한 상태를 몇 개 선택하고 탐색을 진행합니다. 이는 트리 깊이가 제한된 경우에 적합합니다.
        - **깊이 우선 탐색(DFS)**: 가장 유망한 경로를 따라 계속 탐색하고, 필요에 따라 백트래킹하여 다른 경로를 탐색합니다. 이는 더 깊은 트리 구조에서 유용합니다.

### ToT의 장점

- **일반성**: ToT는 CoT, CoT-SC, 셀프 리파인먼트(Self-Refinement) 등의 기법을 포함할 수 있으며, 트리 구조의 깊이와 너비를 조정하여 다양한 문제 유형에 적용할 수 있습니다.
- **모듈성**: ToT는 기본 LM, 생각 분해, 생성, 평가, 탐색 과정 등을 독립적으로 조정할 수 있습니다.
- **적응성**: 다양한 문제 특성, LM 능력, 리소스 제한 등에 따라 ToT를 조정할 수 있습니다.
- **편의성**: 추가 훈련 없이 사전 학습된 LM을 사용하여 문제 해결을 수행할 수 있습니다.

이러한 ToT의 개념적 이점은 여러 가지 문제 유형에서 높은 성능을 보이는 데 기여합니다.

### ToT 프롬프팅

[GitHub - dave1010/tree-of-thought-prompting: Using Tree-of-Thought Prompting to boost ChatGPT's reasoning](https://github.com/dave1010/tree-of-thought-prompting)

- ToT Framework의 주요 개념을 단순 Prompting 기법으로 적용하여 LLM이 단일 프롬프트에서 중간 생각을 평가할 수 있도록 함.

- 다음과 같은 방법으로 작성한다.

```markdown
Imagine three different experts are answering this question.
All experts will write down 1 step of their thinking,
then share it with the group.
Then all experts will go on to the next step, etc.
If any expert realises they're wrong at any point then they leave.
The question is...

(Question)
Bob is in the living room.
He walks to the kitchen, carrying a cup.
He puts a ball in the cup and carries the cup to the bedroom.
He turns the cup upside down, then walks to the garden.
He puts the cup down in the garden, then walks to the garage.
Where is the ball?

---
(번역본)

세 명의 다른 전문가들이 이 질문에 답하고 있다고 상상해보도록 해.(n명의 전문가...)
모든 전문가들은 자신의 생각의 한 단계를 적어내고,
그것을 그룹과 공유할거야.
그런 다음 모든 전문가들은 다음 단계로 넘어가. 등등.
만약 어떤 전문가가 어떤 시점에서든 자신이 틀렸다는 것을 깨닫게 되면 그들은 떠나.
그렇다면 질문은...

(Question)
```

- 이런 식으로 프롬프팅을 하면, LLM(여기서는 `Chat GPT-3.5 turbo`)는 다음과 같이 답변하며, ToT를 구현하게 된다. 각각의 전문가는 노드로서 기능한다.

```markdown
Expert 1: Alright, let's start with the first step. Bob is in the `living room`. So, logically, the ball is also in the `living room`.

Expert 2: I disagree. Bob carries the cup to the `kitchen`, implying that the ball is now in the `kitchen`.

Expert 3: Actually, I think the ball stays in the `living room`. Bob hasn't put the ball in the cup yet, so it remains where it was.

Expert 1: Ah, you're right. My mistake. The ball should indeed still be in the `living room`.

[ball: `living room`]

Expert 2: Agreed. So, moving on to the next step, Bob puts a ball in the cup and carries the cup to the `bedroom`.

[ball: `bedroom`]

Expert 3: The ball is now in the cup, so it moves with Bob to the `bedroom`. It's inside the cup.

[ball: `cup`]

Expert 1: Correct. So, now the ball is in the cup, and Bob is in the `bedroom`. Next, he turns the cup upside down and walks to the `garden`.

[ball: `garden`]

Expert 2: Since the ball was in the cup, when Bob turns it upside down, the ball falls out. So, the ball is now in the `garden`.

[ball: `garden`]

Expert 3: Yes, that seems right. The ball would fall out when the cup is turned upside down. So, now the ball is indeed in the `garden`.

Expert 1: Agreed. So, Bob puts the cup down in the `garden` and walks to the `garage`. The ball should still be in the `garden`.

[ball: `garden`]

Expert 2: Wait, I think I made a mistake earlier. When Bob put the ball in the cup in the `kitchen`, it would have stayed there. So, the ball should be in the `bedroom`, not the `garden`.

[ball: `bedroom`]

Expert 3: Oh, you're right. I didn't catch that. If the ball stayed in the cup, then it would indeed be in the `bedroom` when Bob turns the cup upside down.

[ball: `bedroom`]

Expert 1: I see my mistake now too. The ball should indeed be in the `bedroom`. So, we've reached the conclusion. The ball is in the `bedroom`.

---
(번역본)

Expert 1: 여기 첫 번째 단계에서 시작해볼게요. Bob이 `거실(living room)`에 있어요. 그래서 논리적으로, 공도 `거실`에 있어야 해요.

Expert 2: 제 의견은 달라요. Bob은 컵을 `주방(kitchen)`으로 가져가요. 그러면 공은 이제 `주방`에 있을 거예요.

Expert 3: 실제로는, 공은 `거실`에 그대로 있을 거예요. Bob이 아직 공을 컵에 넣지 않았으니까, 그 자리에 있을 거예요.

Expert 1: 아, 맞아요. 제 실수네요. 공은 실제로 `거실`에 있어야 해요.

[공: `거실`]

Expert 2: 동의해요. 그래서, 다음 단계로 넘어가보죠. Bob은 공을 컵에 넣고 `침실(bedroom)`로 컵을 가져갔어요.

[공: `침실`]

Expert 3: 이제 공은 컵 안에 있으니까, Bob과 함께 `침실`로 이동할 거예요.

[공: `컵`]

Expert 1: 맞아요. 그래서 이제 공은 컵 안에 있고, Bob은 `침실`에 있어요. 다음에는 컵을 뒤집고 `정원(garden)`으로 가요.

[공: `정원`]

Expert 2: 공이 컵 안에 있었기 때문에, Bob이 컵을 뒤집으면 공이 떨어질 거예요. 그래서 이제 공은 `정원`에 있어요.

[공: `정원`]

Expert 3: 그렇죠. 컵을 뒤집으면 공이 떨어지겠죠. 그래서 이제 공은 실제로 `정원`에 있겠네요.

Expert 1: 맞아요. 그래서, Bob이 컵을 `정원`에 놓고 `차고(garage)`로 간 다음에도, 공은 여전히 `정원`에 있을 거예요.

[공: `정원`]

Expert 2: 잠깐, 제가 전에 실수했던 것 같아요. Bob이 `주방`에서 공을 컵에 넣을 때, 공은 그 자리에 있었을 거예요. 그래서 공은 `침실`에 있어야죠, `정원`이 아니에요.

[공: `침실`]

Expert 3: 아, 맞아요. 그걸 놓쳤네요. 만약 공이 컵 안에 있었다면, 컵을 뒤집을 때 공은 실제로 `침실`에 있겠죠.

[공: `침실`]

Expert 1: 저도 이제 실수를 알겠어요. 공은 실제로 `침실`에 있어야 해요. 결론에 도달했어요. 공은 `침실`에 있어요.
```

- 이런식으로 텍스트가 출력이 되는데, 이 기법이 ToT Prompting이다.
    
    (위의 문제 해결 방식이 자료의 남아있는 방식이나, 정답을 틀렸다.)
    
- 위 문제를 보면 각각의 전문가(Expert)를 노드로 생각하고 보면, 이들의 서로 다른 방향으로 뻗어나가다, 정답을 찾아내는 ToT의 방식을 나타내고 있다.

---

## Retrieval Augmented Generation(RAG)

- Meta AI에서 개발한 `language model-based system` (언어 모델 기반 시스템)

### 특징

- `information retrieval component` ,  `text generator model` 의 결합
- 일반적인 LM과 달리 외부 지식 소스(Wikipedia 같은)에 접근하여 작업 진행
- 외부 소스에 접근하기 때문에 일관성을 제공하고, 생성된 응답의 신뢰성 향상
    
    → `Hallucination issue` 완화
    

- RAG 구현 자료
    
    [Prompt-Engineering-Guide/notebooks/pe-rag.ipynb at main · dair-ai/Prompt-Engineering-Guide](https://github.com/dair-ai/Prompt-Engineering-Guide/blob/main/notebooks/pe-rag.ipynb)
    

---

## **Automatic Reasoning and Tool-use (ART)**

- LLM이 복잡한 언어 작업을 처리할 때, 추론과 외부 도구 사용 능력을 결합.
    
    `method for improving LLMs by combining reasoning and the ability to use tools.` 
    
- 모델이 여러 단계의 작업과 외부 리소스를 활용해야 하는 복잡한 작업을 할 수 있게 하는 접근 방식.

### **Automatic Reasoning and Tool-use(**ART)의 진행 과정


1. Task Library
    1. LLM이 주어진 작업을 해결하기 위한 가장 적합한 예시를 선택.
2. Run Program
    1. LLM이 여러 질문을 통해 필요 정보를 수집하고, 코드 스니펫을 실행하여, 최종 결과를 얻음.
    2. 이 과정에서 Frozen LLM(파라미터가 고정된 LLM)을 사용함.
3. Fix Mistakes
    1. 작업 결과에 오류가 발생할 경우, 이 단계에서 수정함.
    2. 사람의 피드백으로 수정할 부분이 있다면, 작업 라이브러리 또는 실행단계에서 필요한 부분 수정 가능

---

## **Automatic Prompt Engineer (APE)**

- 자동 프롬프팅 엔지니어링 기법으로 **언어 모델에 대한 명령 생성 및 선택을 자동화하여 프로세스를 자연어 합성 및 최적화 문제**로 다룸.
- `Zero-shot CoT`에서 사용된 `Step by Step` 프롬프트보다 더 나은 성능을 보여줌.


### APE의 절차

1. 명령어 후보 생성: LM이 작업에 대한 여러 명령어 후보 생성
2. 실행 및 평가: 생성된 명령어를 모델에서 실행하고 점수 함수에 기반하여 효과 평가.
3. 최적화: 가장 효과적인 명령어를 선별하고 개선하여 언어 모델의 성능을 제로샷 방식으로 향상

- 예시

```markdown
문제: "두 수의 합이 15이고 그 차가 3인 두 수는 무엇인가요?"
명령어 후보 생성: "우선 간단한 식을 설정해 봅시다." / "두 수를 x와 y라고 합시다."
실행 및 평가: "x + y = 15"와 "x - y = 3"의 식을 설정하고 해결합니다.
최적화: 가장 정확한 답변을 도출한 방법을 선택하여 다른 비슷한 유형의 문제에 적용
```

---

## Active-Prompt

- 기존 CoT 방법은 고정된 인간이 작성한 주석에 의존함.
    - Active Prompt는 작업에 대한 다양한 예시를 사용하여 성능을 향상시킴


1. **불확실성 추정**
    1. 주어진 작업을 수행하기 위해 LLM을 쿼리화. 
    2. 이때, 몇 개의 CoT 예시를 제공할 수 있습니다. 
    3. 질문에 대해 k개의 가능한 답을 생성, 각 답변의 차를 기준으로 불확실성 지표 계산
    4. 이는 주어진 질문에 대해 모델의 불확실성을 측정하는 데 사용됩니다.
2. **선택**
    1. 계산된 불확실성 지표를 기반으로 가장 불확실한 질문을 선택.
    2. 이러한 질문들은 모델이 명확한 답을 내리기 어려운 부분이며, 주석이 필요합니다.
3. **주석 및 예시 추가**
    1. 선택된 질문은 인간에 의해 주석이 추가됨. 주석은 작업에 대한 예시로 사용됨, 모델이 보다 정확하게 작업을 수행할 수 있도록 지원. 
    2. 이 과정에서 새로운 주석된 예시가 생성됨
4. **추론**:
    1. 새롭게 주석된 예시를 사용하여 각 질문에 대한 답을 추론.
    2. 이는 모델이 더욱 효과적으로 문제를 해결할 수 있도록 도와줍니다.

- 이러한 접근법을 통해, Active-Prompt는 다양한 작업에 적응
- 인간 주석을 통해 모델의 성능 향상 가능
- 프롬프트를 동적으로 최적화하고, 모델의 불확실성을 줄이는 데 도움이 됨.

### Reference

- https://arxiv.org/pdf/2302.12246.pdf
- https://www.promptingguide.ai/techniques/activeprompt

---

## **Directional Stimulus Prompting**


- LLM이 원하는 결과를 생성하도록 더 잘 유도하기 위해 제안된 새 프롬프팅 기법.
- 모델에 대한 지시나 힌트를 제공하는 정책 언어 모델(policy LM)을 활용.

### 특징

1. Policy LM:  stimulus/hint를 생성하기 위해 훈련된 LM
2. LLM을 최적화 하기 위해 강화 학습 적용.
3. Frozen LLM과 통합: Policy LM은 작은 모델로, 동결된 LLM에 힌트 제공하는 역할 수행.
    
    → 동결된 LLM의 이점 유지와 동시에 방향성 있는 힌트로 성능 향상 가능.
    

### Reference

- https://arxiv.org/abs/2302.11520

---

## Program-Aided Language Models(프로그램 지원 언어모델)

- 텍스트를 사용하는 대신, Python 인터프리터와 같은 프로그래밍 방식 런타임을 통해서 단계적으로 해결하는 방식

### 예시

```python
import openai
from datetime import datetime
from dateutil.relativedelta import relativedelta
import os
from langchain.llms import OpenAI
from dotenv import load_dotenv
load_dotenv()
 
# API 구성
openai.api_key = os.getenv("OPENAI_API_KEY")
# LangChain 구성
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
# 모델 인스턴스 설정
llm = OpenAI(model_name='text-davinci-003', temperature=0)

**question = "오늘은 2023년 2월 27일이야. 나는 정확히 25년 전에 태어났어. 내가 태어난 날짜를 MM/DD/YYYY 형식으로 알려줘."
DATE_UNDERSTANDING_PROMPT = """
# Q: 2015년까지 36시간 남았어. 오늘로부터 일주일 뒤는 며칠인지 MM/DD/YYYY 형식으로 알려줘.
# 2015년이 되기까지 36시간이 남았다면 오늘은 36시간 전이다.
today = datetime(2015, 1, 1) - relativedelta(hours=36)
# 오늘부터 일주일 뒤는
one_week_from_today = today + relativedelta(weeks=1)
# 답을 %m/%d/%Y 형식으로 하면
one_week_from_today.strftime('%m/%d/%Y')
# Q: 2019년의 첫 날은 화요일이고 오늘은 2019년의 첫 월요일이야. 오늘 날짜를 MM/DD/YYYY 형식으로 알려줘.
# 2019년의 첫 날이 화요일이고 오늘이 2019년의 첫 월요일이라면 오늘은 6일 후다.
today = datetime(2019, 1, 1) + relativedelta(days=6)
# 답을 %m/%d/%Y 형식으로 하면
today.strftime('%m/%d/%Y')
# Q: 콘서트는 1943년 6월 1일에 열리기로 예정되어 있었는데, 하루 연기되어 오늘로 변경됐어. 10일 전 날짜를 MM/DD/YYY 형식으로 알려줘.
# 콘서트가 1943년 6월 1일로 예정되어 있었으나 오늘로 하루 연기되었다면, 오늘은 하루가 지난 것이다.
today = datetime(1943, 6, 1) + relativedelta(days=1)
# 열흘 전의 날짜는
ten_days_ago = today - relativedelta(days=10)
# 답을 %m/%d/%Y의 형식으로 하면
ten_days_ago.strftime('%m/%d/%Y')
# Q: 오늘은 1969년 4월 19일이야. 24시간 후의 날짜를 MM/DD/YYYY 형식으로 알려줘.
# 오늘의 날짜는 1969년 4월 19일이다.
today = datetime(1969, 4, 19)
# 24시간 후의 날짜는
later = today + relativedelta(hours=24)
# 답을 %m/%d/%Y의 형식으로 하면
today.strftime('%m/%d/%Y')
# Q: 영희는 오늘이 2002년 3월 11일이라고 생각했지만 실제로는 다음날인 3월 12일이야. 24시간 후의 날짜를 MM/DD/YYYY 형식으로 알려줘.
# 영희는 오늘 날짜를 2002년 3월 11일이라고 생각했고, 사실 오늘은 3월 12일이면 오늘 날짜는 2002년 3월 12일이다.
today = datetime(2002, 3, 12)
# 24시간 후의 날짜는
later = today + relativedelta(hours=24)
# 답을 %m/%d/%Y의 형식으로 하면
later.strftime('%m/%d/%Y')
# Q: 영희는 2001년 2월 마지막 날 태어났어. 오늘은 영희의 16번째 생일이야. 어제의 날짜를 MM/DD/YYYY 형식으로 알려줘.
# 영희가 2001년 2월의 마지막 날에 태어났고 오늘이 영희의 16번째 생일이라면 오늘은 16년 후다.
today = datetime(2001, 2, 28) + relativedelta(years=16)
# 어제 날짜는
yesterday = today - relativedelta(days=1)
# 답을 %m/%d/%Y의 형식으로 하면
yesterday.strftime('%m/%d/%Y')
# Q: {question}
""".strip() + '\n'

llm_out = llm(DATE_UNDERSTANDING_PROMPT.format(question=question))

print(llm_out)
exec(llm_out)
print(born)**
```

### Reference

- https://arxiv.org/abs/2211.10435

---

## ReAct prompting

- ReAct Prompting은 LLM을 이용하여 논리적 추론 과정(reaction)과 행동(act)을 수행함.
- 추론(reasoning traces): 모델이 행동 계획을 유도, 추적, 업데이트, 예외 처리
- 행동(action step): 외부 소스와 상호작용하며 정보 수집.

### ReAct Prompting의 진행 과정

- Thought
    - 문제 이해, 추론 과정 시작 → 문제를 분해하여 필요한 정보 파악.
- Action
    - 필요한 정보를 얻기 위해 외부 환경과 상호작용 → 검색엔진을 통해 정보를 찾기, 코드 실행하기 등
- Observation
    - Action 에서 얻은 정보를 기반으로 모델이 추론을 계속함. → 다음 행동 결정에 사용.

- **ReAct 에서 AI의 행동 양식(예시)**
    - Aside from the Apple Remote, what other devices can control the program Apple Remote was originally designed to interact with?(질문)
    - in context example 또한 프롬프트에 추가됨.
    
    
    - 실제 실행 결과(GPT 3.5 Turbo)
    
    ```python
    I will follow the process to find the answer to your question.
    
    Question Aside from the Apple Remote, what other devices can control the program Apple Remote was originally designed to interact with?
    Thought 1 I need to understand what program the Apple Remote was originally designed to interact with.
    Action 1 Search[Apple Remote program]
    Observation 1 The Apple Remote was designed to interact with the Front Row media center program.
    
    Thought 2 Now, I need to find out what other devices can control the Front Row media center program.
    Action 2 Search[devices that can control Front Row media center program]
    Observation 2 Front Row was discontinued by Apple, but devices like iPhone, iPad, and certain third-party remote controls could control it.
    
    Thought 3 Other devices that can control the Front Row media center program include iPhone, iPad, and certain third-party remote controls.
    Action 3 Finish[iPhone, iPad, certain third-party remote controls]
    
    ---
    
    질문: Apple Remote 이외에도 Front Row 미디어 센터 프로그램을 제어할 수 있는 다른 장치는 무엇입니까?
    생각 1: Apple Remote가 원래 상호 작용하도록 설계된 프로그램을 이해해야 합니다.
    동작 1: Apple Remote 프로그램 검색
    관찰 1: Apple Remote는 Front Row 미디어 센터 프로그램과 상호 작용하도록 설계되었습니다.
    
    생각 2: 이제 Front Row 미디어 센터 프로그램을 제어할 수 있는 다른 장치를 찾아야 합니다.
    동작 2: Front Row 미디어 센터 프로그램을 제어할 수 있는 장치 검색
    관찰 2: Apple은 Front Row를 중단했지만 iPhone, iPad 및 일부 타사 원격 제어 장치가 이를 제어할 수 있습니다.
    
    생각 3: Front Row 미디어 센터 프로그램을 제어할 수 있는 다른 장치로 iPhone, iPad 및 일부 타사 원격 제어 장치가 있습니다.
    동작 3: 완료 - iPhone, iPad, 일부 타사 원격 제어 장치
    ```
    

### ReAct Prompting 예시

- 프롬프트의 모범 예시
    
    ```python
    질문 콜로라도 조산 운동의 동쪽 구역이 확장되는 지역의 표고 범위는 얼마이니?
    생각 1 콜로라도 조산 운동을 검색하여, 콜로라도 조산 운동의 동쪽 구역이 확장되는 지역을 찾은 다음, 그 지역의 표고 범위를 찾아야 해.
    행동 1 검색하기[콜로라도 조산 운동]
    관찰 1 콜로라도 조산 운동은 콜로라도와 그 주변 지역에서 산이 형성되는 과정(조산 운동)을 말해.
    생각 2 동부에 대한 언급이 없어. 그래서 동부 섹터를 찾아봐야겠어.
    행동 2 찾아보기[동부 섹터]
    관찰 2 (결과 1 / 1) 동쪽 섹터는 고원 지대까지 뻗어 있고 중앙 평원 조산 운동이라고 불려.
    생각 3 콜로라도 조산 운동의 동쪽 섹터는 고원 지대까지 뻗어 있어. 따라서 고원 지대를 검색하여 해발 범위를 찾아야 해.
    행동 3 검색[고원 지대]
    관찰 3 고원 지대는 두 개의 다른 지대 중 하나를 가르켜.
    생각 4 대신 고원 지대(미국)를 검색해야해.
    행동 4 검색[고원 지대 (미국)]
    관찰 4 고원 지대는 대평원\(the Great Plains\)의 일부 지역이야. 동쪽에서 서쪽으로, 고원 지대는 약 1,800피트에서 7,000피트(550~2,130m)까지 고도가 높아져.[3]
    생각 5 고원 지대의 해발 고도는 약 1,800~7,000피트이므로, 정답은 1,800~7,000피트야.
    행동 5 완료[1,800~7,000피트]
    ...
    ```
    

1. 트레이닝 세트(예: HotPotQA)에서 사례를 선택, ReAct 형식의 궤적(`trajectories`) 구성
    1. `trajectories`는 예시와 같이 생각-행동-관찰 순으로 작동한다.
2. 이 트레이닝 세트들을 퓨샷(few-shot) 견본으로 사용.

### 다른 방법과 비교
- CoT와 비교했을 때, ReAct는 서로 다른 평가 방법에서 차이가 발생함.
- 발생 원인은 다음과 같다.
    - CoT suffers from fact hallucination
    - ReAct's structural constraint reduces its flexibility in formulating reasoning steps.(ReAct의 구조적 제약으로 인한, 유연성 낮음)
    - ReAct depends a lot on the information it's retrieving; non-informative search results derails the model reasoning and leads to difficulty in recovering and reformulating thoughts(ReAct의 검색 정보에 크게 의존하는 형태)
- 논문에서는 ReAct 와 CoT + Self consistency 의 결합을 지원하는 프롬프팅 방법은 일반적으로 모든 프롬프팅 방법들보다 성능이 뛰어났음.

- 참고 자료

[ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629)

---

## Reflexion
- 언어 피드백을 통해 언어 기반 에이전트를 강화
- According to [Shinn et al. (2023)](https://arxiv.org/pdf/2303.11366.pdf), "Reflexion is a new paradigm for ‘verbal‘ reinforcement that parameterizes a policy as an agent’s memory encoding paired with a choice of LLM parameters."
- Reflexion은 환경에서 오는 언어적 피드백(free-form language 또는 scalar)을 LLM Agent에 추가하여 다음 단계에 포함시킴.
    - 이는 이 에이전트가 빠르고 효과적으로 이전 실수를 배우고, 성능을 향상시키는데 기여함.

### Reflexion의 구조
- Reflexion은 3개의 다른 모델을 사용함.
    1. Actor
        - Observation을 기반으로 텍스트와 행동을 생성.
        - Actor는 환경 내에서 행동 한 후, 궤적을 남기는 관찰 대상.
        - CoT와 ReAct가 Actor 모델 생성.
        - 에이전트에 추가적 맥락을 제공하기 위한 메모리 컴포넌트 추가됨.
    2. Evaluator
        - Actor가 생성한 출력 평가
        - 생성된 경로(단기 메모리)를 imput으로 받아 보상 점수 출력.
        - 작업에 따라 여러가지 보상 함수 사용됨.
            
            (LLMs and rule-based heuristics are used for decision-making tasks).
            
    3. Self-Reflection
        - Actor가 자기 개선을 위한 언어적 강화 신호 생성
        - LLM에 의해 수행, 향후 실험에 대한 가치 있는 피드백 제공.
        - Self Reflection 모델은 보상 신호, 현재 경로, 지속적 메모리를 통해 구체적이고, 관련성 높은 피드백 제공. → 메모리에 저장됨.
            
            → 에이전트가 의사 결정 능력을 신속하게 향상시키는데 도움됨.
            

> ### Reflextion을 사용할 수 있는 경우(gpt-4 답변 참조)
    Reflexion 프레임워크는 언어 기반 에이전트가 과거 실수를 돌아보고 미래의 결정을 개선하기 위해 그 지식을 활용할 수 있도록 돕는 구조입니다. Reflexion을 사용하기에 적합한 경우는 다음과 같습니다:

    - **시도와 오류로부터 학습해야 하는 경우**:
    Reflexion은 에이전트가 과거 실수를 반성하고 그 지식을 향후 의사결정에 적용하여 성능을 개선하도록 설계되었습니다. 이는 의사결정, 추론, 프로그래밍과 같이 에이전트가 시도와 오류를 통해 학습해야 하는 작업에 적합합니다.
    - **전통적인 강화 학습 방법이 비실용적인 경우**:
    전통적인 강화 학습(RL) 방법은 종종 광범위한 훈련 데이터와 값비싼 모델 미세 조정을 요구합니다. Reflexion은 언더라이닝 언어 모델을 미세 조정할 필요가 없는 경량 대안을 제공하며, 데이터와 계산 자원을 더 효율적으로 활용할 수 있습니다.
    - **미세한 피드백이 필요한 경우**:
    Reflexion은 전통적인 RL에서 사용되는 스칼라 보상보다 더 미세하고 구체적인 언어적 피드백을 활용합니다. 이를 통해 에이전트는 자신의 실수를 더 잘 이해하고 다음 실험에서 더 목표 지향적인 개선을 이룰 수 있습니다.
    - **해석 가능성과 명시적 메모리가 중요한 경우**:
    Reflexion은 전통적인 RL 방법에 비해 더 해석 가능하고 명시적인 에피소드 메모리를 제공합니다. 에이전트의 자기 반성은 메모리에 저장되어, 학습 과정의 분석과 이해를 쉽게 해줍니다.

    Reflexion이 효과적인 작업에는 다음이 포함됩니다:

    - **순차적 의사결정**:
    Reflexion 에이전트는 다양한 환경을 탐색하고 다단계 목표를 완료하는 AlfWorld 작업에서 성능을 개선했습니다.
    - **추론**:
    Reflexion은 여러 문서를 기반으로 추론이 필요한 질문-응답 데이터셋인 HotPotQA에서 에이전트의 성능을 개선했습니다.
    - **프로그래밍**:
    Reflexion 에이전트는 HumanEval 및 MBPP와 같은 벤치마크에서 더 나은 코드를 작성했으며, 일부 경우에는 최첨단 결과를 달성했습니다.

    그러나 Reflexion에는 몇 가지 제한 사항이 있습니다:

    - **자기 평가 능력 의존**:
    Reflexion은 에이전트가 자신의 성능을 정확하게 평가하고 유용한 자기 반성을 생성할 수 있는 능력에 의존합니다. 이는 특히 복잡한 작업에서 도전적일 수 있지만, 모델의 능력이 향상됨에 따라 Reflexion의 성능도 개선될 것으로 예상됩니다.
    - **장기 메모리 제한**:
    Reflexion은 최대 용량이 있는 슬라이딩 윈도우를 사용하지만, 더 복잡한 작업의 경우 벡터 임베딩 또는 SQL 데이터베이스와 같은 고급 구조를 사용하는 것이 유리할 수 있습니다.
    - **코드 생성 제한**:
    정확한 입력-출력 매핑을 지정하는 테스트 기반 개발의 한계(예: 비결정적 생성 함수 및 하드웨어에 영향을 받는 함수 출력)가 있을 수 있습니다.

    ## **(GPT 4 답변)**

    Reflexion은 언어 기반 에이전트가 언어적 피드백을 통해 자기 개선을 이루는 데 유용한 프레임워크입니다. 다양한 작업에 적용할 수 있으며, 다음과 같은 활용 방안을 고려해 볼 수 있습니다:

    - **학습 과정 최적화**:
    Reflexion을 통해 에이전트는 과거 실수를 돌아보고 이를 기반으로 학습합니다. 이를 통해 에이전트의 학습 속도를 높이고 더 나은 결과를 얻을 수 있습니다.
    - **의사결정 능력 향상**:
    Reflexion은 에이전트가 스스로 평가하고 반성하도록 돕기 때문에 의사결정 작업에 적합합니다. 이를 통해 에이전트가 복잡한 의사결정 작업에서 실수를 줄이고 더 효과적인 결정을 내릴 수 있습니다.
    - **프로그래밍 교육**:
    프로그래밍 작업에서 Reflexion을 활용하면 에이전트가 코드 작성 과정에서 발생하는 오류를 파악하고 개선할 수 있습니다. 이를 통해 에이전트는 더 나은 코드를 작성하고, 프로그래밍 기술을 발전시킬 수 있습니다.
    - **지식 기반 시스템 강화**:
    Reflexion을 사용하여 지식 기반 시스템을 강화할 수 있습니다. 에이전트가 스스로 반성하고 지식을 확장하여 더 정확한 정보를 제공할 수 있도록 합니다.
    - **지속적인 개선을 위한 프레임워크 구축**:
    Reflexion은 에이전트가 지속적으로 개선할 수 있는 구조를 제공합니다. 이를 통해 시스템이 시간이 지남에 따라 향상되고 더 정확한 결과를 제공할 수 있습니다.

    이러한 활용 방안은 Reflexion을 사용하여 에이전트의 성능을 향상시키고, 더 나은 학습과 의사결정을 가능하게 합니다. 이를 통해 복잡한 작업에서도 에이전트의 효율성을 높일 수 있습니다.

    ### Reflexion의 한계

    - **자기 평가 능력 의존**:
    Reflexion은 에이전트가 자신의 성능을 정확하게 평가하고 유용한 자기 반성을 생성할 수 있는 능력에 의존합니다. 이는 특히 복잡한 작업에서 도전적일 수 있지만, 모델의 능력이 향상됨에 따라 Reflexion의 성능도 개선될 것으로 예상됩니다.
    - **장기 메모리 제한**:
    Reflexion은 최대 용량이 있는 슬라이딩 윈도우를 사용하지만, 더 복잡한 작업의 경우 벡터 임베딩 또는 SQL 데이터베이스와 같은 고급 구조를 사용하는 것이 유리할 수 있습니다.
    - **코드 생성 제한**:
    정확한 입력-출력 매핑을 지정하는 테스트 기반 개발의 한계(예: 비결정적 생성 함수 및 하드웨어에 영향을 받는 함수 출력)가 있을 수 있습니다.

---

## **Multimodal CoT Prompting**

[Zhang et al. (2023](https://arxiv.org/abs/2302.00923)은 최근 멀티모달 생각의 사슬 프롬프팅(multimodal chain-of-thought prompting) 접근 방식을 제안했습니다. 기존의 CoT는 언어 양식(language modality)에 중점을 둡니다. 반면, 멀티모달 CoT는 텍스트와 이미지를 2단계 프레임워크에 통합합니다. 첫 번째 단계에서는 멀티모달 정보를 기반으로 근거 생성(rationale generation)을 포함합니다. 그 다음에는 두 번째 단계인 답변 추론이 이어지며, 이 단계에서는 생성된 정보적 근거들(informative generated rationales)을 활용하여 답변을 도출합니다.

멀티모달 CoT 모델(1B)은 ScienceQA 벤치마크에서 GPT-3.5보다 성능이 뛰어났습니다.


- 관련 논문

[Language Is Not All You Need: Aligning Perception with Language Models](https://arxiv.org/abs/2302.14045)

[Multimodal Chain-of-Thought Reasoning in Language Models](https://arxiv.org/abs/2302.00923)

---

# 참고자료
## 프롬프트 엔지니어링 자료

- LLM의 현주소(2023.04)
    
    [거대언어모델(LLM)의 현주소](https://brunch.co.kr/@brunchgpjz/49)
    

- **개발자를 위한 ChatGPT 프롬프트 엔지니어링**
    
    [개발자를 위한 ChatGPT 프롬프트 엔지니어링](https://wikidocs.net/book/9886)
    

- **Learn Prompting docs**
    
    [Learn Prompting: Your Guide to Communicating with AI](https://learnprompting.org/ko/docs/intro)
    

- **Prompt Engineering Guide(번역본, 영문)**
    
    [프롬프트 엔지니어링 가이드 – Nextra](https://www.promptingguide.ai/kr)
    
    [Prompt Engineering Guide – Nextra](https://www.promptingguide.ai/)
    

## 프롬프트 엔지니어링 논문

- Zero Shot & Few shot
    - Zero-Shot lerning 관련 논문
        - [**FINETUNED LANGUAGE MODELS ARE ZERO-SHOT LEARNERS(2022)**](https://arxiv.org/pdf/2109.01652.pdf)
    - 사람의 피드백을 통한 AI 강화 학습
        - [**Deep Reinforcement Learning from Human Preferences(2017)**](https://arxiv.org/pdf/1706.03741.pdf)
    - Few-shot learning 관련 논문
        - [**Language Models are Few-Shot Learners(2020)**](https://arxiv.org/pdf/2005.14165.pdf)

- CoT(Chain of Thought)
    - CoT 관련 논문(Chain of Thought)
        - [**Chain-of-Thought Prompting Elicits Reasoning in Large Language Models(2022)**](https://arxiv.org/pdf/2201.11903.pdf)
    - Zero-shot CoT 논문
        - **[Large Language Models are Zero-Shot Reasoners(2022)](https://arxiv.org/pdf/2205.11916.pdf)**
    - Auto-CoT 논문
        - **[Automatic Chain of Thought Prompting in Large Language Models(2022)](https://arxiv.org/pdf/2210.03493.pdf)**

- Self-Consistency
    - [**Self-Consistency Improves Chain of Thought Reasoning in Language Models(2022)**](https://arxiv.org/pdf/2203.11171.pdf)

- Generated Knowledge Prompting
    - [**Generated Knowledge Prompting for Commonsense Reasoning(2022)**](https://arxiv.org/pdf/2110.08387.pdf)

- Retrieval-Augmented Generation
    - **[Retrieval-Augmented Generation for Large Language Models: A Survey](https://arxiv.org/abs/2312.10997)**

- Automatic multi-step Reasoning and Tool-use for large language models(ART)
    - **[ART: Automatic multi-step reasoning and tool-use for large language models](https://arxiv.org/abs/2303.09014)**

[Top](#prompt-engineering)