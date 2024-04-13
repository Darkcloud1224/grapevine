from flask import Flask, jsonify
from flask_cors import CORS


app = Flask(__name__)
CORS(app)


@app.route("/chat", methods=["GET", "POST"])
def hello_world():
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
                        "content": "The Los Angeles Dodgers won the World Series in 2020."
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
    return response
