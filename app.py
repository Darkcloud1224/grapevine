from flask import Flask, jsonify, request
from flask_cors import CORS
from algoliasearch.search_client import SearchClient
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
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
import os

# Set the OpenAI API key
# Set up the chat model
# ========================================================================================================================

apikey = "sk-proj-JjiRovdFeMXxuurc4X8iT3BlbkFJlwCB9pPGya7oQpC6LHTc"
model = ChatOpenAI(api_key=apikey,max_tokens = 4000, model="gpt-4o")

class SearchOutput(BaseModel):
    keywords: str = Field(description="remove unneeded words such as stepwords and verbs or general words like product and only keep only keep keywords with meaning for search such as product names, description, brand names, basically anything that describes the product. (words to not include: 'products', 'recommendation')")
    needs_product: bool = Field(description=" if the user is just saying hi and asking a normal request then return false")

searchParser = JsonOutputParser(pydantic_object=SearchOutput)
    
class DescriptionOutput(BaseModel):
    response: str = Field(description="talk about the product description and its material and what's it's made out of and why they're sustainable. don't provide any url")
    # response: str = Field(description="")

    
DescriptionParser = JsonOutputParser(pydantic_object=DescriptionOutput)
    
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
runnable = prompt | model 
store = {}
def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]
with_message_history = RunnableWithMessageHistory(
    runnable,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history",
) 

with_message_history_search = with_message_history | searchParser
with_message_history_describe = with_message_history | DescriptionParser

# ========================================================================================================================


# Setting up search function
# ========================================================================================================================

# Connect and authenticate with your Algolia app
applicationID = "D50DM3JZ06"
api_key = "e7c937a48f59d3e0790d63dc7f75bd71"
client = SearchClient.create(applicationID, api_key)

def search_product(query):
    # Search the index and print the results
    index = client.init_index("Product")

    results = index.search(query)
    try:
        result = results["hits"][0]
        output = {
            "ProductName": result["ProductName"],
            "ProductPath": result["objectID"],
            "ProductDescription": result["ProductDescription"],
            "ProductPrice": result["ProductPrice"],
            "BrandName": result["BrandNameText"]
            
        }
        print(output)
        return output
    except:
        return {}

# ========================================================================================================================



@app.route("/chat", methods=["GET", "POST"])
def hello_world():
    json_data = request.json

    message = json_data["messages"][-1]["content"]
    print(message)
    # joke_query = "Good Morning"
    # message = message.get('message', 'No message provided')
    try:
        searchquery = with_message_history_search.invoke(
            {"ability": "remove unneeded words such as stepwords and verbs or general words like product and only keep only keep keywords for search such as product names, descrption, brand names", "input": str(message), "instructions": str(searchParser.get_format_instructions())},
            config={"configurable": {"session_id": "abc123"}},
        )
        print(searchquery)
        print(searchquery["keywords"])
        component_status = searchquery["needs_product"]
    except:
        component_status = False
        
    if component_status:
        searchquery = searchquery["keywords"]
        
        searchquery = search_product(searchquery)
        print("product: " + str(searchquery))
        if not searchquery:
            DescriptionQuery = with_message_history_describe.invoke(
                {"ability": "Helping users improve their lifestyles and make it more sustainable. if the users message isn't clear always ask leading questions. if the user is asking for product recommendation and the product details isn't provided then assume product doesn't exist within our market and apologize", "input": f"{message}", "instructions": str(DescriptionParser.get_format_instructions())},
                config={"configurable": {"session_id": "abc123"}},
            )
            component_status = False
        else:
            DescriptionQuery = with_message_history_describe.invoke(
                {"ability": "Helping users improve their lifestyles and make it more sustainable as well as help them find the products they need", "input": f"user query: {message} product details:{searchquery}", "instructions": str(DescriptionParser.get_format_instructions())},
                config={"configurable": {"session_id": "abc123"}},
            )
    else:
        DescriptionQuery = with_message_history_describe.invoke(
                {"ability": "Helping users improve their lifestyles and make it more sustainable as well as help them find the products they need.", "input": f"{message}", "instructions": str(DescriptionParser.get_format_instructions())},
                config={"configurable": {"session_id": "abc123"}},
            )
        component_status = False


    print(searchquery)
    # x = 1
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
                        'component_status': component_status,
                        'component_content': "https://www.arloandolive.com/cdn/shop/products/DSC00727copy_1100x.jpg?v=1631835048", 
                        "content": DescriptionQuery["response"],
                        "product_path": searchquery.get("ProductPath", None),
                        "ProductName": searchquery.get("ProductName", None),
                        "ProductPrice": searchquery.get("ProductPrice", None),
                        "BrandName": searchquery.get("BrandName", None),
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
