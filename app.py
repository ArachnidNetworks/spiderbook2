from flask import Flask, request, redirect, make_response, render_template, url_for, jsonify, abort
from flask import send_from_directory, flash
import os
import time
import re
import datetime
import dbi
import mimetypes
import traceback

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ["SECRET"]

UNPROC_ENTITY = 422
SERVER = 500
NOT_FOUND = 404
FORBBIDEN = 403

def get_image_url(image, new_pid):
    # If the image exists
    if image:
        # If it's actually an image:
        name = image.filename
        if mimetypes.guess_type(name)[0].startswith("image"):
            # Get the new name (next post's id + image's extension)
            imagename = new_pid + os.path.splitext(name)[1]
            image.save(f'static/images/{imagename}')
            return imagename
    return None

def get_curtimestamp():
    return datetime.datetime.utcnow()

@app.route('/')
def root():
    try:
        return redirect(url_for('home', category='all', page=1))
    except:
        traceback.print_exc()
        return abort(SERVER)

@app.route('/<category>')
def no_page(category):
    return redirect(url_for('home', category=category, page=1))

@app.route("/<category>/<page>")
def home(category, page):
    # Uppercase bad
    category = str(category).lower()
    try:
        # If the page number is not valid, return 404
        page = int(page)
    except:
        traceback.print_exc()
        return abort(NOT_FOUND)
    try:
        # If the category is not 'all' and it doesn't exist, return 404
        if category != 'all' and not dbi.find_cat(category):
            return abort(NOT_FOUND)
    except:
        traceback.print_exc()
        return abort(NOT_FOUND)
    # If the page number is invalid, turn it to 1
    if page < 1:
        return redirect(url_for('home', category=category, page=1))
    # Limit amount of posts per page
    limit = 8
    # Offset calculation to not get the same post per page
    off = (page-1)*limit
    # If a category is specified, look for that one only
    if category != "all":
        query = "WHERE category = %s "
        vals = (category, off, limit)
    else:
        # If not, then look for every single post
        query = " "
        vals = (off, limit)
    # Get recent posts
    try:
        posts = dbi.get_posts(query + """ORDER BY postts DESC
        OFFSET %s LIMIT %s""", vals)
        # If any image inside is not in the filesystem, set the value to none
        for post in posts:
            if not os.path.isfile(url_for('static', filename=f'images/{post["imgurl"]}')[1:]):
                print(url_for('static', filename=f'images/{post["imgurl"]}')[1:])
                post.pop('imgurl')
        return render_template("home.html", title=" Home", header=category, small=f"Page {page}",
        posts=posts)
    except:
        # If something goes wrong with the query or template, return a 500 error
        traceback.print_exc()
        return abort(SERVER)

@app.route("/post/<pid>")
def indpost(pid):
    post = dbi.get_posts("WHERE pid = %s", (pid,))[0]
    return render_template("indpost.html", pid=pid, title=post['title'],
    body=post['body'], img={'imgurl': post['imgurl']})

@app.route("/post/<pid>/comment", methods=['POST'])
def create_comment(pid):
    try:
        data = dict(request.form)
        data['author'] = str(data.get('author')).replace(" ", "")
        if not data['author']:
                data['author'] = 'Anonymous'
        data['content'] = str(data['content']).replace(" ", "")
        data['op_id'] = str(pid).replace(" ", "")
        # Get the poster's IP for... reasons... and hash it
        data['poster_ip'] = dbi.hash_str(str(request.environ['REMOTE_ADDR']))
        # Get image if it exists
        image = request.files.get('imgbin')
        # Get pid for image name and post
        new_pid = dbi.get_new_pid(True)
        # Save it on the server and return URL
        data['imgurl'] = get_image_url(image, new_pid)
        data['table'] = 'comments'
        dbi.insert_row(data, new_pid)
    except:
        traceback.print_exc()
        return abort(UNPROC_ENTITY)
    return jsonify(True)

@app.route("/createpost", methods=['POST'])
def create_post():
    try:
        post_data = dict(request.form)
        data = {}
        data['author'] = str(post_data['author']).replace(" ", "")
        if not data['author']:
            data['author'] = 'Anonymous'
        data['category'] = str(post_data['category']).replace(" ", "")
        data['title'] = str(post_data['title']).replace(" ", "")
        data['body'] = str(post_data.get('body')).replace(" ", "")
        # If the body is too big, return an error
        if len(data['body']) > 7000:
            return abort(UNPROC_ENTITY)
        # Set post timestamp to the current timestamp
        data['postts'] = get_curtimestamp()
        # Get the poster's IP for... reasons... and hash it
        data['poster_ip'] = dbi.hash_str(str(request.environ['REMOTE_ADDR']))
        # Get image if it exists
        image = request.files.get('imgbin')
        # Get pid for image name and post
        new_pid = dbi.get_new_pid(True)
        # Save it on the server and return URL
        data['imgurl'] = get_image_url(image, new_pid)
        data['table'] = 'posts'
        dbi.insert_row(data, new_pid)
        return "Post created!"
    except:
        traceback.print_exc()
    return abort(UNPROC_ENTITY)

@app.route("/search", methods=['POST'])
def search_cat():
    form_data = dict(request.form)
    category = form_data.get('category')
    prevpage = form_data.get('previouspage')
    if not dbi.find_cat(category):
        flash("Category not found")
        return redirect(prevpage)
    return redirect(url_for('home', category=category, page=1))

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
