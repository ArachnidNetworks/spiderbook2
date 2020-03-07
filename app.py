#!/usr/bin/env python
import os
# from traceback import print_exc
from flask import Flask, request
# redirect, make_response, render_template, url_for, jsonify, abort, flash
# Response
from api import APImgr
from dbint import DBInterface

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ["SECRET"]

UNPROC_ENTITY = 422
SERVER = 500
NOT_FOUND = 404
FORBBIDEN = 403

db = DBInterface("spiderbook", "postgres", "postgres")
api = APImgr(db)


@app.route('/')
def root():
    return "Hello!"


@app.route('/add/post', methods=['POST'])
def add_post():
    fd = request.form
    data = {"title": fd.get("title"), "parent": fd.get("parent"),
            "body": fd.get("body")}
    # try:
    api.add(data)
    # except:
    # print_exc()
