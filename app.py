from flask import Flask, request, redirect, make_response, render_template, url_for
import os, time
import dbi

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ["SECRET"]

def get_binary_image(image):
    name = image.filename
    image.save(name)
    with open(name, 'rb') as f:
        return f.read()
    os.delete(name)

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
        data = dict(request.form)
        category = data.get('category')
        if not category: category = None
        author = 'admin'
        title = data.get('title')
        if not title: title = None
        body = data.get('body')
        if not body: body = None
        image = request.files.get('img')
        if image:
            imgbin = get_binary_image(image)
        else:
            imgbin = None
        return data
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
