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

# View functions

@app.route('/')
def root():
    return "Hello!"

@app.route('/api/post', methods=['POST'])
def add_post():
    try:
        result = api.add_post(request)
    finally:
        if result:
            return make_response(("Success", 200))
        else:
            return make_response(("aaaa", 500))

@app.route('/api/reply', methods=['POST'])
def reply():
    try:
        result = api.reply(request)
    finally:
        if result:
            return make_response(("Success", 200))
        else:
            return make_response(("aaaa", 500))

@app.route('/api/signup', methods=['POST'])
def signup():
    try:
        result = api.signup(request)
    finally:
        if result:
            return make_response(("Success", 200))
        else:
            return make_response(("aaaa", 500))

@app.route('/api/login', methods=['POST'])
def login():
    try:
        result = api.login(request)
    finally:
        if result:
            return make_response(("Success", 200))
        else:
            return make_response(("aaaa", 500))

@app.route('/api/su/removepost', methods=['POST'])
def remove_post():
    try:
        result = api.remove_post(request)
    finally:
        if result:
            return make_response(("Success", 200))
        else:
            return make_response(("aaaa", 500))

@app.route('/api/su/ban', methods=['POST'])
def ban_ip():
    try:
        result = api.ban_ip(request)
    finally:
        if result:
            return make_response(("Success", 200))
        else:
            return make_response(("aaaa", 500))

