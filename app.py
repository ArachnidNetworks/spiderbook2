#!/usr/bin/env python
import os
# from traceback import print_exc
from flask import Flask, request, redirect, make_response, render_template, \
                  url_for, jsonify, abort, flash, Response
from API import api

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ["SECRET"]

UNPROC_ENTITY = 422
SERVER = 500
NOT_FOUND = 404
FORBBIDEN = 403


@app.route('/')
def root():
    return "Hello!"
