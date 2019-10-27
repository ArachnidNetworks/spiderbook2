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

if __name__ == "__main__":
    app.run(
        host="localhost",
        port=8000,
        debug=True
    )
