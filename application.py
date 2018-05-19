import os
import time

from flask import Flask, jsonify, render_template, request, redirect, url_for, jsonify
from flask_cors import CORS

from config import Config
from modules.handlers.hello_handler import HelloHandler
from modules.handlers.blockpass_handler import BlockpassHandler

app = Flask(__name__)
CORS(app)
app.config.update(DEBUG=False)

@app.route("/")
def hello():
  return HelloHandler.hello(endpoint="/")

@app.route("/blockpass/api/status", methods=['POST'])
def bp_status():
  return BlockpassHandler.status(endpoint="/blockpass/api/status")

@app.route("/blockpass/api/login", methods=['POST'])
def bp_login():
  return BlockpassHandler.create_record(endpoint="/blockpass/api/login")

@app.route("/blockpass/api/register", methods=['POST'])
def bp_register():
  return BlockpassHandler.create_record(endpoint="/blockpass/api/register")

@app.route("/blockpass/api/uploadData", methods=['POST'])
def bp_upload():
  return BlockpassHandler.upload(endpoint="/blockpass/api/uploadData")

def main(environ=None, start_response=None):
  if __name__ == '__main__':
    app.run(host='0.0.0.0', port=Config.PORT, debug=False)
  else:
    return app(environ, start_response)

if __name__ == '__main__':
  main()
