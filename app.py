from flask import Flask, request, redirect, make_response, render_template, url_for, jsonify, abort
from flask import send_from_directory, flash
import api
import os, traceback

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ["SECRET"]

UNPROC_ENTITY = 422
SERVER = 500
NOT_FOUND = 404
FORBBIDEN = 403

@app.route('/')
def root():
    return "Hello!"

@app.route('/test/post', methods=['POST'])
def test_post():
    api.add_post(request)
    return "Success!", 200

@app.route('/test/reply', methods=['POST'])
def test_reply():
    api.reply(request)
    return "Success!", 200
