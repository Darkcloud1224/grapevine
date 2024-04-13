import os
from langchain.agents import initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List

from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
# Set the OpenAI API key
os.environ['OPENAI_API_KEY'] = "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"

# Set up the chat model
model = ChatOpenAI(temperature=0.5)

# Set up the memory
memory = ConversationBufferMemory(memory_key="chat_history")



class Joke(BaseModel):
    requires: bool = Field(description="answer to wether the user requires data to be retrieved from the database. if it doesn't require data from database return False else if it requirers then return True (look for keywords like recommend)")
    keywords: List[str] = Field(description="list of keywords tot use for search")
    response: str = Field(description="response if user doesn't require data from database")

    

parser = JsonOutputParser(pydantic_object=Joke)

# Define the personality prompt
persona_prompt = PromptTemplate(
    template="Answer the user query.\n{format_instructions}\n{query}\n",
    input_variables=["query"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)


joke_query = "Good Morning, Can you recommend a black shirt for me?"


prompt = PromptTemplate(
    template="Answer the user query.\n{format_instructions}\n{query}\n",
    input_variables=["query"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

chain = prompt | model | parser

x= chain.invoke({"query": joke_query})
print(x)