from flask import Flask, request, redirect, make_response, render_template, url_for
import os, time
import api

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ["SECRET"]

@app.route("/")
def home():
    return "<h1>Home</h1>"

@app.route("/posts")
def posts():
    posts = api.get_posts()
    return "<h1>Posts</h1>"

@app.route("/posts/<category>")
def catpost(category):
    posts = api.get_posts(category)
    return f"<h1>'{category}' posts</h1>"

@app.route("/posts/create", methods=['GET', 'POST'])
def create_post():
    return "<h1>Create post</h1>"

@app.route("/user/signin")
def signin():
    email = 'admin@email.com'
    password = 'securepassword'
    if api.login(email, password):
        return "<h1>Signed in</h1>"
    else:
        return "<h1>No</h1>"

@app.route("/user/signup")
def signup():
    return "<h1>Sign up</h1>"

if __name__ == "__main__":
    app.run(
        host="localhost",
        port=8000,
        debug=True
    )
