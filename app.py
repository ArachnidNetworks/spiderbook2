#!/usr/bin/env python
from flask import Flask, request, redirect, make_response, render_template, url_for, jsonify, abort
from flask import send_from_directory, flash
import api
import os
from traceback import print_exc

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ["SECRET"]

UNPROC_ENTITY = 422
SERVER = 500
NOT_FOUND = 404
FORBBIDEN = 403

@app.route('/')
def root():
    return "Hello!"

@app.route('/api/post', methods=['POST'])
def test_post():
    try:
        api.add_post(request)
        return "Success!", 200
    except:
        return "aaaa", 500

@app.route('/api/reply', methods=['POST'])
def test_reply():
    try:
        api.reply(request)
        return "Success!", 200
    except:
        return "aaaa", 500

@app.route('/api/signup', methods=['POST'])
def signup():
    try:
        api.signup(request)
        return "Success!", 200
    except:
        return "aaaa", 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        api.login(request)
        return "Success!", 200
    except:
        return "aaaa", 500

@app.route('/api/su/removepost', methods=['POST'])
def remove_post():
    try:
        api.remove_post(request)
        return "Success!", 200
    except:
        return "aaaa", 500

@app.route('/api/su/ban', methods=['POST'])
def ban_ip():
    try:
        api.ban_ip(request)
        return "Success!", 200
    except:
        return "aaaa", 500

