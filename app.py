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
    return str(posts)

@app.route("/<category>")
def catpost(category):
    posts = dbi.get_posts(category)
    return str(posts)

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
        data['table'] = 'posts'
        dbi.insert_row(data)
        return "Post created!"
    else:
        return "Create post"

@app.route("/user/signin", methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        login_data = dict(request.form)
        email = login_data.get('email')
        password = dbi.hash_str(str(login_data.get('pass')))

        if dbi.login(email, password):
            return "Signed in"
        else:
            return "No"
    else:
        return "Login page"

@app.route("/user/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        user_data = dict(request.form)
        data = {}
        data['username'] = user_data.get('username')
        data['email'] = user_data.get('email')
        data['pass'] = dbi.hash_str(str(user_data.get('pass')))
        data['bio'] = user_data.get('bio')
        data['table'] = 'users'
        dbi.insert_row(data)
        return "User created!"
    else:
        return "Sign up"

if __name__ == "__main__":
    app.run (
        host="localhost",
        port=8000,
        debug=True
    )
