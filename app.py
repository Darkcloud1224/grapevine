from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/")
def hello_world():
    data = {"date": "2024-04-13"}
    # Convert the dictionary to JSON and return
    return jsonify(data)