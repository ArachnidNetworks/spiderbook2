from flask import Flask, request, redirect, make_response, render_template, url_for, jsonify
import os, time
import dbi

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ["SECRET"]

def get_image_url(image):
    name = f'images/{image.filename}'
    image.save(name)
    return name

@app.route("/")
def home():
    limit = 30
    posts = dbi.get_posts("ORDER BY curdate DESC LIMIT %s", (limit,))
    return jsonify(posts)

@app.route("/cat/<category>")
def catpost(category):
    posts = dbi.get_posts("WHERE category = %s", (category,))
    for post in posts:
        post.pop('pid')
        post.pop('category')
    return jsonify(posts)

@app.route("/post", methods=['GET', 'POST'])
def create_post():
    if request.method == 'POST':
        post_data = dict(request.form)
        data = {}
        data['author'] = post_data.get('author')
        if not data['author']: data['author'] = 'Anonymous'
        data['category'] = post_data.get('category')
        data['title'] = post_data.get('title')
        data['body'] = post_data.get('body')
        image = request.files.get('imgbin')
        print(request.files)
        if image:
            data['imgurl'] = get_image_url(image)
        else:
            data['imgurl'] = None
        data['table'] = 'posts'
        dbi.insert_row(data)
        return "Post created!"
    else:
        return "Create post"

# Login and Signup pages.
""" @app.route("/user/signin", methods=['GET', 'POST'])
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
        return "Sign up" """

if __name__ == "__main__":
    app.run (
        host="localhost",
        port=8000,
        debug=True
    )
