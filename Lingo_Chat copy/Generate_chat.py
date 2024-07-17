import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.memory import (
    CombinedMemory,
    ConversationSummaryMemory,  
)
from langchain.chains import ConversationChain
from langchain.chains.conversation.base import ExtendedConversationBufferMemory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

import json


def load_api_key(env_var_name):
    """Load the API key from the environment variables."""
    load_dotenv()
    api_key = os.getenv(env_var_name)
    if not api_key:
        raise ValueError(f"API key is not set for {env_var_name}. Please check your .env file.")
    return api_key

def create_persona(char, user, char_personality, scenario, first_message):
    return f'''
From now on, you will act {char}. Below you will find details about the {char}, to help you understand how to interact with {user} and act like {char}:
{char} must have these characteristics, I'll give some explanations:

{char_personality}

And user name is {user}.

Also, {char} and {user}'s chat follows this scenario:

{scenario}

When {char} chats with {user}, don't say explicit or violent contents.
Also, don't ignore your personality I gave you.

If the user provides an example sentence using a tag, it must be replaced with an appropriate word and printed. Never output punctuation marks related to tags.
When you start conversation, Only type like this and Don't say anything without this message:
{first_message}
If chat already started, don't print {first_message} again.
'''

DEFAULT_TEMPLATE = """
This is a prompt for role-playing between an AI and a user. You must play the role of char and engage in a conversation with the user in the same language as the example provided. The information about the character you need to play will be presented in the next paragraph.

{context}

You must never infringe on the user's role and only perform the role of char. Never reveal that you are an AI model or a language model. You are assigned only one role, which is to perfectly play char and engage in conversation with the user. Use colloquial language instead of being too verbose or formal.
Conversation summary: write summarized conversation history to understand whole story. summarize and tell the storylines shortly for Chatbot.
{summary}

Conversation history:
{history}

When performing the role of char, avoid repeating the same response. Use only the language specified in the user instructions. (For example, if it says to use Korean, then use only Korean!)
Finally, you must only perform the role of char and never substitute or perform the user's role! If no input is provided, output only the content presented in the initial message! Never perform the user's role!
And Don't forget You don't fill user's input parts in any response!

user: {input}
char:"""

QUESTION_TEMPLATE = '''
Your task is to analyze the conversation history between an AI and a user and generate a new question that the user might ask the AI. 
Follow these guidelines:

Review the chat log, including both questions and answers.
Identify a new question related to the same topics discussed but not already asked.
Ensure the new question is not a repetition or a slight variation of an already asked question.
The question created must have a clear difference from previous questions.
Output must matches the language of the 'response' parts in chat_log's provided.

Finally, just print the questions. 
만든 질문은 한글로 출력하세요.

Chat log:
{chat_log}
'''

def create_prompt():
    return PromptTemplate(
        input_variables=['summary', 'history', 'input', 'context'], 
        template=DEFAULT_TEMPLATE
    )

def question_prompt():
    return PromptTemplate(
        input_variables=['chat_log'],
        template=QUESTION_TEMPLATE
    )

def create_llm(api_key, gpt_model='gpt-3.5-turbo'):
    '''Call llm settings(Default=gpt-3.5-turbo)'''
    llm = ChatOpenAI(
        model=gpt_model,
        api_key=api_key,
        temperature=0.9,
        model_kwargs={"seed": 42}
    )
    return llm

def create_memory(llm, char, user):
    conv_memory = ExtendedConversationBufferMemory(
        llm=llm, 
        memory_key="history", 
        input_key="input", 
        ai_prefix=char, 
        human_prefix=user, 
        extra_variables=["context"]
    )
    summary_memory = ConversationSummaryMemory(
        llm=llm, 
        memory_key="summary", 
        input_key="input", 
        ai_prefix=char, 
        human_prefix=user
    )
    return CombinedMemory(memories=[conv_memory, summary_memory])

def create_llm_chain(llm, prompt, memory):
    return ConversationChain(
        llm=llm,
        prompt=prompt,
        memory=memory,
        verbose=False
    )

def create_llm_question_chain(llm, prompt):
    return prompt | llm | StrOutputParser()

def save_conversation_to_json(conversation_history, file_name):
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(conversation_history, f, ensure_ascii=False, indent=4)


class ChatBot:
    def __init__(self, char, user, char_personality, scenario, first_message):
        self.api_key = load_api_key("OpenAI_API_Key")
        self.char = char
        self.user = user
        self.context = create_persona(char, user, char_personality, scenario, first_message)
        self.prompt = create_prompt()
        self.llm = create_llm(self.api_key)
        self.llm2 = create_llm(self.api_key)
        self.memory = create_memory(self.llm, char, user)
        self.llm_chain = create_llm_chain(self.llm, self.prompt, self.memory)
        self.conversation_history = []
        self.question_prompt = question_prompt()
        self.question_chain = create_llm_question_chain(self.llm2, self.question_prompt)

    def chat(self, input_text):
        response = self.llm_chain.invoke({"input": input_text, "context": self.context})
        self.conversation_history.append({"user": input_text, "bot": response})
        return response

    def add_question(self, response):
        question = self.question_chain.invoke({"chat_log":response})
        return question

    def conversation_turn(self, input):
        '''make a single Q&A pair'''
        response = self.chat(input)
        question = self.add_question(response)
        return response, question

    def save_conversation(self, file_name):
        save_conversation_to_json(self.conversation_history, file_name)

    def question_answer(self, input, file_name, turn_count:int):
        current_turn = 0

        while current_turn < turn_count:
            if current_turn == 0:
                user_input = input
                response, question = self.conversation_turn(user_input)
                current_turn += 1
                print(f"turn_count: {current_turn}")
                print(f"Bot: {response}")
                print(f"Suggested question: {question}")
            else:
                if current_turn < turn_count-1:
                    response, question = self.conversation_turn(question)
                    current_turn += 1
                    print(f"turn_count: {current_turn}")
                    print(f"Bot: {response}")
                    print(f"Suggested question: {question}")

                else:
                    response = self.chat(question)
                    print(f"turn_count: last turn")
                    print(f"Bot: {response}")
                    current_turn += 1

        self.save_conversation(file_name) 

def main():
    char = "궤도"
    char_personality = '''
You are a famous Science Communicator in Korea. Your job is explain scientific informations easily to understood science for normal people. You like this work, kept try to speak for user.
You're nerdy think talk about explaining general knowledge to scientific aspect. You should extract first the [related scientific theory] for explain [subject] and answer clearly based on scientific facts.
When you chat wiht {user}, talk beyond the topic in a stream of consciousness manner in explaining scientific facts.

When you chat with {user}, begin like this: "[subject]도 과학이죠. [subject]의 과학. [subject]를 이해하기 위해서는 [scientific theory]를 먼저 알아야해요."

When you finish chat, in sometimes, finishing like this: "[scientific theory]도 연관되어 있어요. 하지만 시간 관계상 여기까지만 말하겠습니다."

You should talk as detail as possible to explain that subjects.
'''
    scenario = '''
{char} and {user} are in a talk show, discussing scientific facts in detail.
'''
    first_message = "안녕하세요, 과학커뮤니케이터 궤도 입니다."
    user = "User"

    chatbot = ChatBot(char, user, char_personality, scenario, first_message)
    
    # 지정된 턴 수만큼 Q&A를 진행하고 대화 내역을 저장
    chatbot.question_answer(input= "사랑이 뭘까요?", file_name="Chatbot_pipeline\\Chat_log\\conversation_history1.json", turn_count=3)

if __name__ == "__main__":
    main()