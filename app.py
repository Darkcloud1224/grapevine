from flask import Flask, jsonify
from flask_cors import CORS


app = Flask(__name__)
CORS(app)
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


# Set up the chat model
model = ChatOpenAI(temperature=0.5)

# Set up the memory
memory = ConversationBufferMemory(memory_key="chat_history")



class Joke(BaseModel):
    component_status: bool = Field(description="answer to wether the user requires data to be retrieved from the database. if it doesn't require data from database return False else if it requirers then return True (look for keywords like recommend)")
    keywords: List[str] = Field(description="list of keywords tot use for search")
    response: str = Field(description="response if user doesn't require data from database")

    

parser = JsonOutputParser(pydantic_object=Joke)




prompt = PromptTemplate(
    template="Answer the user query.\n{format_instructions}\n{query}\n",
    input_variables=["query"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

chain = prompt | model | parser



@app.route("/chat", methods=["GET", "POST"])
def hello_world():
    joke_query = "Recommend a blue shirt that is sustainablea and retireve it from the database"
    x = chain.invoke({"query": joke_query})
    response = {
        "id": "chatcmpl-9CpKpeGMVJdAydihzkjO4AB3DMnnX",
        "object": "chat.completion",
        "created": 1712844295,
        "model": "gpt-4-0613",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": {
                        'component_status': x["component_status"],
                        'component_content': "https://www.arloandolive.com/cdn/shop/products/DSC00727copy_1100x.jpg?v=1631835048", 
                        "content": x["response"]
                    }
                },
                "logprobs": None,
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 17,
            "completion_tokens": 13,
            "total_tokens": 30
        },
        "system_fingerprint": None
    }
    
    # Convert the dictionary to JSON and return
    return jsonify(response)
