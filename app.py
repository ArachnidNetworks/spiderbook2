from flask import Flask, request, redirect, make_response, render_template, url_for
import os, time
import dbi

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ["SECRET"]

@app.route("/")
def home():
    posts = dbi.get_posts()
    return "<h1>Posts</h1>"

@app.route("/<category>")
def catpost(category):
    posts = dbi.get_posts(category)
    return f"<h1>'{category}' posts</h1>"

@app.route("/post", methods=['GET', 'POST'])
def create_post():
    if request.method == 'POST':
        return '<h1>POST</h1>'
    return "<h1>Create post</h1>"

@app.route("/user/signin")
def signin():
    email = 'admin@email.com'
    password = 'securepassword'
    if dbi.login(email, password):
        return "<h1>Signed in</h1>"
    else:
        return "<h1>No</h1>"

@app.route("/user/signup", methods=['GET', 'POST'])
def signup():
    return "<h1>Sign up</h1>"

if __name__ == "__main__":
    app.run (
        host="localhost",
        port=8000,
        debug=True
    )
