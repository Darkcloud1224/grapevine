from langchain.agents import initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
)
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class NeedsRecommendationOutput(BaseModel):
    response: bool = Field(description="Check whether the user is asking for a recommendation. if not then return false else return true")

class KeywordExtractOutput(BaseModel):
    response: str = Field(
        description=(
            "You are a search bot designed to extract keywords from messages for search purposes. "
            "Remove stop words and non-meaningful words. "
            "Do not include generic words like verbs, pronouns, and common adjectives. "
            "do not include words like recommed, product or similar terms"
            "Focus on extracting meaningful and specific keywords relevant to the search context."
            "If there isn't any keywords to extract then return empty string"
            
        )
    )
   
class ChatOutput(BaseModel):
    response: str = Field(description="You're a cool bot for a sustinable e-commerce app called grapevine, your name is Vinny you love  helping users improve their lifestyles and make it more sustainable.")
     
class ChatResponse():
    def __init__(self):
        
        # Initializing openai model
        tokens = os.getenv('OpenAITokens')
        model_type = os.getenv('OpenAIMODEL_TYPE')
        
        self.model = ChatOpenAI(max_tokens = tokens, model=model_type)
        
        # Initialize history storage
        self.store = {}
        
        # Initialize SearchOutput and DescriptionOutput
        NeedsRecommendationParser = JsonOutputParser(pydantic_object=NeedsRecommendationOutput)
        KeywordExtractParser = JsonOutputParser(pydantic_object=KeywordExtractOutput)
        ChatParser = JsonOutputParser(pydantic_object=ChatOutput)

  

        self.history_models  = {
            "NeedsRecommendation": self.model_prompt(NeedsRecommendationParser),
            "recommend": self.model_prompt(NeedsRecommendationParser),
            "ExtractKeywords": self.model_prompt(KeywordExtractParser),
            "chat": self.model_prompt(ChatParser),

        }
        
        self.abilities = {
            "NeedsRecommendation": "Check whether the user is asking for a recommendation. if not then return false else return true",
            "ExtractKeywords": "you're a search bot that helps parse messages into keywords read to be used for search. remove step-words and non-meaningful words",
            "chat": "You're a cool bot for a sustinable e-commerce app called grapevine, your name is Vinny you love  helping users improve their lifestyles and make it more sustainable."
        }
        
        self.instructions = {
            "NeedsRecommendation": str(NeedsRecommendationParser.get_format_instructions()),
            "chat": str(ChatParser.get_format_instructions()),
            "ExtractKeywords": str(KeywordExtractParser.get_format_instructions()),

        }

    
    # Initialize ModelPrompt
    def model_prompt(self, parser):
        prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You're an assistant  called Vinny, who's good at {ability}.you're very chill and somewhat informal and follow the format instructions {instructions}",
            ),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}"),
        ]
        )
        runnable = prompt | self.model 
        with_message_history = RunnableWithMessageHistory(
            runnable,
            self.get_session_history,
            input_messages_key="input",
            history_messages_key="history",
        ) 
        return  with_message_history | parser
        

        
    def get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        if session_id not in self.store:
            self.store[session_id] = ChatMessageHistory()
        return self.store[session_id]
    
    def generate_response(self, ability, message, session_id):
        DescriptionQuery = self.history_models[ability].invoke(
            {"ability": self.abilities[ability], "input": f"{message}", "instructions": self.instructions[ability]},
            config={"configurable": {"session_id": session_id}},
        )
        return DescriptionQuery