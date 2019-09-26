from flask import Flask, request, redirect, make_response, render_template, url_for, jsonify, abort
from flask import send_from_directory
import os
import time
import re
import datetime
import dbi

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ["SECRET"]

UNPROC_ENTITY = 422
SERVER = 500
NOT_FOUND = 404
FORBBIDEN = 403

def get_image_url(image):
    name = image.filename
    image.save(f'static/images/{name}')
    return name

def get_curtimestamp():
    return datetime.datetime.utcnow()

@app.route('/')
def root():
    try:
        return redirect(url_for('home', category='all', page=1))
    except:
        return abort(SERVER)

@app.route('/<category>')
def no_page(category):
    return redirect(url_for('home', category=category, page=1))

@app.route("/<category>/<page>")
def home(category, page):
    category = str(category).lower()
    try:
        page = int(page)
    except:
        return abort(NOT_FOUND)
    try:
        if category != 'all':
            r = dbi.find_cat(category)
            if not r:
                return abort(NOT_FOUND)
    except:
        return abort(NOT_FOUND)
    """ try: """
    if page < 1:
        return redirect(url_for('home', category=category, page=1))
    limit = 10
    off = (page-1)*limit
    if category != "all":
        query = "WHERE category = %s "
        vals = (category, off, limit)
    else:
        query = " "
        vals = (off, limit)
    posts = dbi.get_posts(query + """ORDER BY postts DESC
    OFFSET %s LIMIT %s""", vals)
    popular = dbi.get_popular_cats(5)
    """ for post in posts:
        post[98765] = post['imgurl']
        post.pop('imgurl') """
    print(posts)
    return render_template("home.html", title=" Home", posts=posts, popular=popular,
    category=category, page=page)
    """ except Exception as e:
        print(e)
        return abort(SERVER) """

@app.route("/post/<pid>")
def indpost(pid):
    post = dbi.get_posts("WHERE pid = %s", (pid,))[0]
    return render_template("indpost.html", pid=pid, title=post['title'],
    body=post['body'], img={'imgurl': post['imgurl']})

@app.route("/create/comment", methods=['POST'])
def create_comment():
    try:
        data = dict(request.form)
        data['author'] = str(data.get('author')).replace(" ", "")
        if not data['author']:
                data['author'] = 'Anonymous'
        data['content'] = str(data['content']).replace(" ", "")
        data['op_id'] = str(data['op_id']).replace(" ", "")
        data['poster_ip'] = dbi.hash_str(str(request.environ['REMOTE_ADDR']))
        image = request.files.get('imgbin')
        if image:
            data['imgurl'] = get_image_url(image)
        else:
            data['imgurl'] = None
        data['table'] = 'comments'
        dbi.insert_row(data)
    except:
        return abort(UNPROC_ENTITY)
    return jsonify(True)

@app.route("/create/post", methods=['GET', 'POST'])
def create_post():
    if request.method == 'POST':
        try:
            post_data = dict(request.form)
            data = {}
            data['author'] = str(post_data['author']).replace(" ", "")
            if not data['author']:
                data['author'] = 'Anonymous'
            data['category'] = str(post_data['category']).replace(" ", "")
            data['title'] = str(post_data['title']).replace(" ", "")
            data['body'] = str(post_data.get('body')).replace(" ", "")
            if len(data['body']) > 7000:
                return abort(UNPROC_ENTITY)
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
        except:
            return abort(UNPROC_ENTITY)
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
    app.run(
        host="localhost",
        port=8000,
        debug=True
    )
