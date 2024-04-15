from flask import Flask, jsonify, request
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

from langchain_openai import ChatOpenAI
from langchain.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
import os
# Set the OpenAI API key
# Set up the chat model
llm = ChatOpenAI(temperature=0.5, max_tokens = 100)

# Set up the memory
memory = ConversationBufferMemory(memory_key="chat_history")



# class Joke(BaseModel):
#     component_status: bool = Field(description="answer to wether the user requires data to be retrieved from the database. if it doesn't require data from database return False else if it requirers then return True (look for keywords like recommend)")
#     keywords: List[str] = Field(description="list of keywords tot use for search")
#     response: str = Field(description="respond normally here whether component_status is true or false")

    

# parser = JsonOutputParser(pydantic_object=Joke)




# prompt = PromptTemplate(
#     template="Answer the user query.\n{format_instructions}\n{query}\n",
#     input_variables=["query"],
#     partial_variables={"format_instructions": parser.get_format_instructions()},
# )

# chain = prompt | model | parser

prompt = ChatPromptTemplate(
    messages=[
        SystemMessagePromptTemplate.from_template(
            "You are a nice chatbot having a conversation with a human and your job is to help them to make their life more sustainable."
        ),
        # The `variable_name` here is what must align with memory
        MessagesPlaceholder(variable_name="chat_history"),
        HumanMessagePromptTemplate.from_template("{question}")
    ]
)
# Notice that we `return_messages=True` to fit into the MessagesPlaceholder
# Notice that `"chat_history"` aligns with the MessagesPlaceholder name.
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
conversation = LLMChain(
    llm=llm,
    prompt=prompt,
    verbose=True,
    memory=memory
)



@app.route("/chat", methods=["GET", "POST"])
def hello_world():
    json_data = request.json

    joke_query = json_data["messages"][-1]["content"]

    # joke_query = "Good Morning"
    x = conversation({"question": joke_query})
    x = x["chat_history"][-1].content
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
                        'component_status': False,
                        'component_content': "https://www.arloandolive.com/cdn/shop/products/DSC00727copy_1100x.jpg?v=1631835048", 
                        "content": x
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
