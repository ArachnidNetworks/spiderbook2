#!/usr/bin/env python
import os
from traceback import print_exc
from typing import Callable
from flask import Flask, request, redirect, make_response, render_template, url_for, jsonify, abort
from flask import send_from_directory, flash, Response
from werkzeug.local import LocalProxy
import api

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ["SECRET"]

UNPROC_ENTITY = 422
SERVER = 500
NOT_FOUND = 404
FORBBIDEN = 403

# Utility functions

def view_template(request: LocalProxy, api_function: Callable[[LocalProxy], bool], success: tuple, failure: tuple) -> Response:
    try:
        result = api_function(request)
    finally:
        if result:
            return make_response(success)
        else:
            return make_response(failure)

# View functions

@app.route('/')
def root():
    return "Hello!"

@app.route('/api/post', methods=['POST'])
def add_post():
    return view_template(request, api.add_post, ("Success", 200), ("aaaa", 500))

@app.route('/api/reply', methods=['POST'])
def reply():
    return view_template(request, api.reply, ("Success", 200), ("aaaa", 500))

@app.route('/api/signup', methods=['POST'])
def signup():
    return view_template(request, api.signup, ("Success", 200), ("aaaa", 500))

@app.route('/api/login', methods=['POST'])
def login():
    return view_template(request, api.login, ("Success", 200), ("aaaa", 500))

@app.route('/api/su/removepost', methods=['POST'])
def remove_post():
    return view_template(request, api.remove_post, ("Success", 200), ("aaaa", 500))

@app.route('/api/su/ban', methods=['POST'])
def ban_ip():
    return view_template(request, api.ban_ip, ("Success", 200), ("aaaa", 500))

