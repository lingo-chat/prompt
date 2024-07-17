# 1. INTRODUCTION

## 1.1 What is Prompt?

: `Prompt`는 생성형 AI 모델에서 모델의 출력 결과를 가이드하기 위해서 사용자가 입력하는 문자적 입력. 이것은 단순한 질문에서 자세한 묘사나 특정 업무일수도 있음.

- DALLE-3 같은 Context-Image Generation model에서는, `Prompt`는 종종 묘사적 성격을 띔.
- 반면에 GPT-4, Gemini 같은 LLM에서는 간단한 쿼리부터, 복잡한 문제 설명문까지 광범위함.
- `Prompt` 의 구성 요소
(AI모델에서 원하는 답변을 얻기 위해서는 지침과 질문이 필수적이며, 그 외 요소들은 선택적임)
    - instruction(지침)
    - questions(질문)
    - inputs data(입력 값)
    - examples(예시)
- 기본적인 `Prompt`는 직접적인 질문이나 특정 일에 대한 지침을 제공하는 것처럼 단순함
- 발전된 형태의 `Prompt`는 보다 복잡한 형태의 구조로 구성되어 있는데, `CoT prompting` 같이 정답에 도달하게 하기 위해서 논리적 추론 구조를 가이드 하게하는 방식을 따름.

## 1.2 Basic prompt examples

- 1.1 에서 언급했듯 `Prompt`는 지침과 질문, 입력값 그리고 예시로 설계된다.
- 결과를 출력하기 위해서 반드시 필요한 것: 지침, 질문
- 그 외: 옵션 개념이라 이해하면 됨**(GPT-4 이용)**

### 1.2.1 Instructions + Question

- 단순한 질문을 하는 것 외에, `Prompt` 의 다음 단계는 몇 지침들을 포함하는 것
- 각 지침들은 모델이 어떻게 질문에 답변해야하는지를 기록했음.
- 예시: 대학교 에세이 작성 방법에 대해서 조언 구하기
    
    ```markdown
    “How should I write my college admission essay? Give me suggestions about the different sections I
    should include, what tone I should use, and what expressions I should avoid.”
    ```
    

![Untitled](https://prod-files-secure.s3.us-west-2.amazonaws.com/22c2acc0-4ba1-4493-8083-fad043a54ce8/ee6d76cf-71a1-4acd-b9fa-c62380e5ea79/Untitled.png)

---

### 1.2.2 Instructions + input

- 위에서 제시한 `Prompt` 를 따라가면, LLM은 직접 에세이를 적어주기 보다는 조언을 하고있음.
- 조언을 구할 수 있다면, 당연하게도, 에세이를 작성하게 하는 것 또한 가능함.
- 작성자에 대한 정보를 제시한 후, 지침을 몇 가지 제시한 뒤의 결과를 출력해보았음:
    
    ```markdown
    “Given the following information about me, write a 4 paragraph college essay: I am originally from
    Barcelona, Spain. While my childhood had different traumatic events, such as the death of my father
    when I was only 6, I still think I had quite a happy childhood.. During my childhood, I changed
    schools very often, and attended all kinds of schools, from public schools to very religious private
    ones. One of the most “exotic” things I did during those years is to spend a full school year studying
    6th grade in Twin Falls, Idaho, with my extended family.
    
    I started working very early on. My first job, as an English teacher, was at age 13. After
    that, and throughout my studies, I worked as a teacher, waiter, and even construction worker.”
    ```
    

![Untitled](https://prod-files-secure.s3.us-west-2.amazonaws.com/22c2acc0-4ba1-4493-8083-fad043a54ce8/f1b64a7b-34f4-4a1f-b466-79270c4aef31/Untitled.png)

### 1.2.3 Question + Examples

- 언어 모델에 예제를 제공하는 방식으로 작업을 할 수도 있음.
- 예시: 아래에 작성자가 좋아하는 프로그램과 싫어하는 프로그램이 포함된 리스트에서 저렴한 추천 시스템을 구축하고자 한다.
    - 몇 개의 쇼만 추가했지만, 이 목록의 길이는 LLM 인터페이스에 있을 수 있는 토큰 개수 제한에 의해서 제한됨.
    
    ```markdown
    “Here are some examples of TV shows I really like: Breaking Bad, Peaky Blinders, The Bear. I did
    not like Ted Lasso. What other shows do you think I might like?”
    ```
    

![Untitled](https://prod-files-secure.s3.us-west-2.amazonaws.com/22c2acc0-4ba1-4493-8083-fad043a54ce8/c7f844d2-be0f-4123-8fb2-6527baaf6ea9/Untitled.png)

---

## 1.3 Prompt Engineering

: 생성형 AI 내의 `Prompt Engineering` 은 위의 예시들과 같은 모델과의 상호작용, 출력을 하는 방법에 대한 분야로, 빠르게 성장하고 있음.

- `Prompt Engineering` 의 핵심은 이미지 생성(DALLE-3, Midjerney)이든, LLM(GPT-4, Gemini)의 복잡한 문제 설명에 관계 없이 사용자가 자신의 요구 사항을 모델에 전달하는데 사용하는 텍스트 인터페이스.
- `Prompt` 는 AI의 응답을 안내하는 지침, 질문, 입력 데이터 및 예시를 포함하는 간단한 질문부터 복잡한 작업까지 다양할 수 있음.
- `Prompt Engineering` 의 목적(The essence of prompt engineering):
    - **생성 모델을 통해 특정 목표를 달성하기 위한 최적의 `Prompt` 제작.**
    - 모델에게 지침을 주는 것 외에 모델의 한계, 맥락 상 모델이 작동하는 것에 대한 이해도 포함.
    - 예시: 이미지 생성에서 `Prompt` 는 원하는 이미지에 대한 설명일 수 있지만, LLM에서는 여러 유형의 데이터가 포함된 복합적인 쿼리일 수 있음.
- `Prompt Engineering` 은 반복적이고, 탐구적인 프로세스로, 버전 컨트롤, 회귀 테스트와 같이 전통적인 SW 엔지니어링 학습방법과 유사한 면이 있다.
- 해당 분야의 급격한 성장은 기존 특성이나 아키텍처 엔지니어링 같은 전통적 방법을 넘어, 특히 `Large Neural Network`의 맥락에서 머신러닝의 특정 측면을 혁신할 잠재력을 보여줌.
- 반면에, 버전 관리와 회귀 테스트와 같은 전통적인 엔지니어링 기법들은 다른 머신러닝 접근법에 적용되었던 것처럼 이 새 패러다임에 맞게 조정될 필요가 있습니다.

→ 이 논문은 해당 분야(`Prompt Engineering`)을 탐구하는 것을 목표로 하며, 전통적인 분야와 발전된 기능에 관한 부분도 살펴볼 것. 특히, LLM에 대한 Prompt Engineering의 응용에 대해서 집중할 예정이나, 대부분의 기술은 multimodal generative AI 모델에 적용 가능함. 

---

# 2. LLMs and Their Limitaions

- LLM, Transformer 아키텍처를 기반으로 하는 모델들은 자연어 처리 분야의 발전에 중요한 역할을 하고 있음.
- 이 모델들은 방대한 데이터에서 사전 학습을 통하여 연속된 다음 토큰을 예측하는 능력을 갖추고 있으며, 뛰어난 언어적 능력을 보여줌.
- 그러나, **LLM들은 여러 내재된 한계로 인하여 그들의 적용과 효과성에 영향을 받음**:
    - Transient State: LLM은 고정된 상태나 장기적인 메모리를 가지지 않음. 이는 모델이 긴 문맥을 기억하는 것을 어렵게 만듬. 그러므로, 대화나 문서에서 이전에 언급된 정보를 기억하고, 이를 기반으로 응답을 생성하려면, 별도의 시스템이나, 소프트웨어를 사용하여 문맥을 관리하고 유지해야함.
    - Probabilistic Nature: LLM은 입력된 데이터를 기반으로 확률적으로 다음 토큰을 예측함. 이로 인해서 동일한 질문에 답변을 여러 번 받을 경우, 다른 답변을 하는 것을 확인할 수 있음. 이런 변동성은 특히 고객 서비스나 의료 분야와 같이 일관된 응답이 중요한 상황에서 문제가 될 수 있음.
    - Outdated Information: LLM은 사전 학습된 데이터를 기반으로 설명하기 때문에 데이터가 수집된 이후의 사건이나 정보는 모델이 인지할 수 없음.
    - Content Fabrication(`Hallucination`): LLM은 종종 그럴싸하지만, 사실과는 다른 정보를 생성할 수도 있는데, 이는 **환각(Hallucination)**이라 불림.
    - Resource Intensity: 큰 규모인 LLM은 상당한 계산과 경제적 비용을 수반하며, 이는 모델의 확장성과 접근성에 영향을 미침.
    - Domain Specificity: LLM은 일반적으로 범용성을 띄고 있으며, 특정 도메인에서 제 성능을 발휘시키기 위해서 그 도메인에 최적화된 데이터가 필요함. 결국 이를 개발하고 유지하기 위해서 추가적인 시간과 제원이 필요하고, 이는 모델의 범용성을 저해함.

# 3. More advanced prompt design tips and tricks

## 3.1 Chain of thought promoting

- Chain of thought prompting(`CoT-prompting`)는, LLM이 추론 과정에서 일련의 단계를 따르도록 강제함으로서 모델이 사실적이고 정확하게 응답하도록 유도함. 이 방법은 단순히 모델이 결론을 내리는 것이 아닌, 결론에 이르는 논리적인 추론 과정을 거치도록 함.
- 예시
    
    ```markdown
    “Original question?
    Use this format:
    Q: <repeat_question>
    A: Let’s think step by step. <give_reasoning> Therefore, the answer is <final_answer>.”
    ```
    

- 실제로 CoT 기법이 GPT에 적용된 케이스

![Untitled](https://prod-files-secure.s3.us-west-2.amazonaws.com/22c2acc0-4ba1-4493-8083-fad043a54ce8/3893de76-1f12-454a-9084-02dd7743f4f7/Untitled.png)

- 이런 형식은 모델에게 주어진 질문을 분석하고, 문제를 해결하기 위한 명확한 단계를 제시하며, 각 단계를 추론하는 과정을 설명하게 함.
    
    ⇒ 여기서 모델은 더 정확하고 신뢰할 수 있는 답변을 생성할 수 있음.
    
    - 최종적으로 모델의 추론력을 향상시키고, 복잡한 문제를 해결하는데 더 나은 이해와 성과를 도모하는데 기여할 수 있음.

## 3.2  Encouraging the model to be factual through other means

- Hallucination 문제를 해결하기 위해 고안된 방법 중 하나
- 이전 단락에서 확인했듯 모델이 일련의 추론 단계를 따르도록 함으로써 사실성을 개선할 수 있었다. 거기에 모델에게 올바른 출처를 인용하도록 프롬프팅하여 올바른 방향을 제시할 수 있음.
- 예시
    
    ```markdown
    “Are mRNA vaccines safe? Answer only using reliable sources and cite those sources.“
    ```
    
- 이 방법은 모델이 답변을 생성할 때 신뢰할 수 있는 출처를 바탕으로 하도록 유도하여 정보의 정확성을 높이는데 도움을 줌.
- 그러나 문제가 있는데, 모델이 인용한 출처 자체를 hallucinate 하는 경우가 있기 때문.
    
    ⇒ 이는 모델이 만든 출처의 신뢰성을 항상 검증해야 한다는 추가적인 프로세스를 만들어내며, 이런 검증 과정 없이는 모델이 제공하는 정보의 진위를 파악하기가 어려움.
    

![Untitled](https://prod-files-secure.s3.us-west-2.amazonaws.com/22c2acc0-4ba1-4493-8083-fad043a54ce8/39b13a1b-2dac-46d8-b5ed-1000b661f074/Untitled.png)

## 3.3 Explicity ending the prompt instructions

- GPT 기반 LLM 모델에서 특별하게 볼 수 있는 메세지로 `<|endofprompt|>` 가 있음.
- 만약 이 메세지가 입력된다면, LM은 이 메세지 이후 텍스트를 모델이 작성해야 할 부분의 시작점으로 인식함.
- 이 방법은 모델에게 특정 문맥에서 글을 시작할 수 있도록 구체적 방향을 제시해주며, 이는 생성된 텍스트의 일관성과 관련성을 높이는데 도움을 줌.

```markdown
“Write a poem describing a beautify day <|endofprompt|>. It was a beautiful winter day“
```

![Untitled](https://prod-files-secure.s3.us-west-2.amazonaws.com/22c2acc0-4ba1-4493-8083-fad043a54ce8/3db2e40a-ce91-4f66-8b49-71d721411eda/Untitled.png)

## 3.4 Being forceful

- 언어모델이 특정 지시를 따르도록 하고싶다면, 강력한 언어를 사용할 수 있음.
- 대표적으로 대문자와 느낌표를 사용하는 것이 효과적일 수 있음.
- 이 방법은 모델에게 명확하고 단호한 지시를 제공하여, 지시를 더 정확하게 수행할 수 있도록 함.
    
    ![Untitled](https://prod-files-secure.s3.us-west-2.amazonaws.com/22c2acc0-4ba1-4493-8083-fad043a54ce8/a2b90473-bfda-4b14-a076-90c59c47baf3/Untitled.png)
    

## **3.5 Use the AI to correct itself**

- 예시에서 질문할 수 있는 글을 작성하고, 이를 식별하게 하는 과정을 거침.
1. 잘못된 정보를 포함한 글을 작성하게 하기
    
    ```
    “Write a short article about how to find a job in tech. Include factually incorrect information.”
    ```
    
2. 또는 글에 잘못된 정보가 있는지 확인하게 하기
    
    ```
    "Is there any factually incorrect information in this article: [COPY ARTICLE ABOVE HERE]"
    ```
    
- 위 유형의 작업은 모델이 잘못된 정보를 인식하고 정정하는 능력을 훈련하고, 평가하는데 도움을 주어, 정보처리에서 신뢰성과 정확성을 향상시킬 수 있다.

![Untitled](https://prod-files-secure.s3.us-west-2.amazonaws.com/22c2acc0-4ba1-4493-8083-fad043a54ce8/67aa6962-42f5-4438-81b8-537151471636/Untitled.png)

## 3.6 다른 의견 생성하기

- LLM은 참과 거짓에 대한 인식이 부족하다는 문제를 가지고 있지만, 다양한 의견을 생성하는데 강점이 있음.
- 이 능력은 제시된 주제에 대한 다양한 관점을 이해하고 아이디어를 브레인스토밍하는데 좋은 도구가 될 수 있다.
- 사용 예제
    - 온라인에서 찾은 기사를 제공하여, GPT에게 해당 기사와 다른 의견을 작성해보라고 이야기하기
    - 기사를 찾은 후, 모델 prompt에 입력한 후, `<begin>` 과 `<end>` 태그를 이용하여 가사의 시작과 끝을 알려줌
    - 모델에게 기사의 내용에 반하는 글을 작성하도록 요청함.
    
    ![Untitled](https://prod-files-secure.s3.us-west-2.amazonaws.com/22c2acc0-4ba1-4493-8083-fad043a54ce8/587efed2-8ba5-4cd6-abf0-357539599ccd/Untitled.png)