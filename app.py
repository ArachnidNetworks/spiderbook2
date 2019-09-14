from flask import Flask, request, redirect, make_response, render_template, url_for, jsonify, abort
import os, time, re, datetime
import dbi

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ["SECRET"]

def get_image_url(image):
    name = image.filename
    image.save(f'images/{name}')
    return name

def get_curtimestamp():
    return datetime.datetime.utcnow()

@app.route('/')
def root():
    try:
        return redirect(url_for('home', page=1))
    except:
        return abort(500)

@app.route("/page/<page>")
def home(page):
    try:
        page = int(page)
        if page < 1: return redirect(url_for('home', page=1))
        page = page-1
        limit = 3
        off = int(page)*limit
        print(off)
        posts = dbi.get_posts("ORDER BY postts DESC OFFSET %s LIMIT %s", (off, limit))
        return jsonify(posts)
    except:
        return abort(500)

@app.route("/cat/<category>")
def catpost(category):
    try:
        posts = dbi.get_posts("WHERE category = %s", (category,))
        for post in posts:
            post.pop('pid')
            post.pop('category')
        return jsonify(posts)
    except:
        return abort(500)

@app.route("/post", methods=['GET', 'POST'])
def create_post():
    try:
        if request.method == 'POST':
            post_data = dict(request.form)
            data = {}
            data['author'] = re.escape(post_data.get('author'))
            if not data['author']: data['author'] = 'Anonymous'
            data['category'] = re.escape(post_data.get('category'))
            data['title'] = re.escape(post_data.get('title'))
            data['body'] = re.escape(post_data.get('body'))
            data['postts'] = get_curtimestamp()
            data['poster_ip'] = dbi.hash_str(str(request.environ['REMOTE_ADDR']))
            image = request.files.get('imgbin')
            if image:
                data['imgurl'] = get_image_url(image)
            else:
                data['imgurl'] = None
            data['table'] = 'posts'
            dbi.insert_row(data)
            return "Post created!" 
        else:
            return "Create post"
    except:
        return abort(500)

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
