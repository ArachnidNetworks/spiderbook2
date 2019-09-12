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
        post_data = dict(request.form)
        data = {}
        data['author'] = 'admin'
        data['category'] = post_data.get('category')
        data['title'] = post_data.get('title')
        data['body'] = post_data.get('body')
        image = request.files.get('img')
        if image:
            data['imgbin'] = get_binary_image(image)
        else:
            data['imgbin'] = None
        dbi.create_post(data)
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
