from flask import Flask, jsonify, request
from flask_cors import CORS
from controllers import main_controller

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Apply CORS to all routes and all domains


app.add_url_rule('/chat', 'chat', main_controller.chat, methods=['GET', 'POST'])


