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
    if api.reply(request):
        return "Success!", 200
    return "aaaa", 500

@app.route('/test/su/remove/post', methods=['POST'])
def remove_post():
    api.remove_post('moderator', 'IP', request)
    return "Success!", 200

@app.route('/test/su/ban', methods=['POST'])
def ban_ip():
    if api.ban_ip('moderator', 'IP', request):
        return "Success!", 200
    return "aaaa", 500

