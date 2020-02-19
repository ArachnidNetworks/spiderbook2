#!/usr/bin/env python
from psycopg2 import connect
from random import randint
from hashlib import sha512
from decorator import decorator
from typing import Literal
from re import match
import datetime

# CRUD Actions

def add_post(request):
    """ Adds a post based on the Flask request's data. """
    body_text = request.form.get('body_text')
    body_file = request.files.get('body_file')
    data = {
        'table': 'posts',
        'uid': new_uid(32),
        'title': request.form['title'][:200],
        'category': request.form['category'][:80],
        'ip': request.environ['REMOTE_ADDR'][:45],
        'dt': dt_now()
    }
    if body_text:
        data['body_text'] = body_text[:1000]
    elif body_file:
        file_path = 'post_files/' + body_file.filename
        body_file.save(file_path)
        data['body_file_url'] = file_path

    insert(data)
    return True

def reply(request):
    """ Replies to a post """
    reply_uid = new_uid(32)
    reply_post(request, reply_uid)
    reply_update(request, reply_uid)
    return True

def reply_post(request, reply_uid:str):
    """ Inserts the reply data into the database """
    data = {
        'table': 'replies',
        'uid': reply_uid,
        'op_uid': request.form['op_uid'],
        'body_text': request.form['body_text'][:1000],
        'ip': request.environ['REMOTE_ADDR'][:45],
        'dt': dt_now()
    }
    body_file = request.files.get('body_file')
    if body_file:
        file_path = 'post_files/' + body_file.filename
        body_file.save(file_path)
        data['body_file_url'] = file_path

    insert(data)

def reply_update(request, reply_uid:str):
    """ Adds the reply to the original post """
    op_type = request.form['op_type']
    if op_type == 'post':
        table = 'posts'
    else:
        table = 'replies'
    update({
        'table': table,
        'restriction': f'WHERE uid = \'{request.form["op_uid"]}\'',
        'reply_uids': f"reply_uids || '{reply_uid}'::VARCHAR(32)"
    })

def get_posts(limit:int=100, category:str='all'):
    if category != 'all':
        restriction = f'WHERE category = \'{category}\' '
    restriction += f'ORDER BY dt DESC LIMIT {limit}'
    posts = select({
        'table': 'posts',
        'cols': ['uid', 'title', 'category', 'body_text', 'body_file_url']
    }, restriction)
    if len(posts) > 0:
        return posts
    else:
        return False

def get_post(request):
    uid = request.form['uid']
    restriction = f'WHERE uid = \'{uid}\''
    post = select({
        'table': 'posts',
        'cols': ['uid', 'title', 'category', 'body_text', 'body_file_url', 'ip', 'dt', 'reply_uids']
    }, restriction)
    if len(post) > 0:
        return post[0]
    else:
        return False

def get_replies(post, limit:int):
    if post:
        sql_uid_list = format_for_query(str(tuple(post["reply_uids"])),
            single_quotes=True, par=True)
        restriction = f'WHERE uid IN {sql_uid_list} ORDER BY dt DESC LIMIT {limit}'
        replies = select({
            'table': 'replies',
            'cols': ['uid', 'body_text', 'body_file_url']
        }, restriction)
        return replies
    else:
        return False

def get_post_and_replies(request, limit:int=100):
    """ Gets a single post and a tuple with it and
    limit replies, with the first item being the
    post itself, a dictionary, and the second being
    the replies, a tuple of dictionaries. """
    post = get_post(request)
    if post["reply_uids"]:
        replies = get_replies(post, limit)
    else:
        replies = ();
    return post, replies

# Superuser functions

def signup(request):
    """ Signs up a moderator/admin. Will be pending until an administrator authorizes
    the request with the authorize function.
    Returns True if it's successful, False otherwise.
    Used to signup a new superuser. """
    su_type = request.form['type']
    if su_type == 'mod' or su_type == 'moderator':
        su_type = 'MOD'
    elif su_type == 'admin' or su_type == 'administrator':
        su_type = 'ADM'
    else:
        raise Exception
    email = request.form['email']
    if match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email):
        data = { 'table': 'superusers',
            'su_id': new_uid(32),
            'su_type': su_type,
            'email': request.form['email'],
            'password': secure_hash(request.form['password']),
            'pending': True
        }
        insert(data)
        return True
    raise Exception

def superuser(fn):
    """ Superuser (admin/mod) decorator. Authenticates the user based 
    on the arguments su_type and ip.
    su_type can be either admin, or mod, and ip is any valid IPv4 address.
    If the authentication passes, it returns the function, else it returns False."""
    def wrap(*args, **kwargs):
        #if suauth(args[0]):
        if True:
            return fn(*args, **kwargs)
        else:
            raise Exception
    return wrap

@superuser
def suauth(request) - bool:
    """ Authentication function. Returns the user's rank if succeessful.
    Used to login and to verify superuser requests. """
    data = {
        'table': 'superusers',
        'cols': ['su_type']
    }
    email = request.form['email']
    password = secure_hash(request.form['password'])
    restriction = f"WHERE email = '{email}' && password = '{password}'"
    result = select(data, restriction)
    print(result)
    return True

@superuser
def authorize(request):
    """ Authorize function. Returns True if successful, and False if
    the request was denied or if the authorizer's rank is not high enough
    (moderator attempting to authorize an administrator, for example).
    Used to authorize a new moderator or administrator. """
    pass

@superuser
def remove_post(request) -> bool:
    result = get_post_and_replies(request)
    if not result:
        return False
    post, replies = result
    post_type = request.form["op_type"]
    post_uid = request.form["uid"]
    for reply in replies:
        delete({
            'table': 'replies',
            'restriction': f"WHERE uid = '{reply['uid']}'"
        })
    delete({
        'table': 'posts' if post_type == 'post' else 'replies',
        'restriction': f"WHERE uid = '{post_uid}'"
    })

@superuser
def ban_ip(request) -> bool:
    # get post ip from form argument
    ip = get_post(request).get('ip')
    # put ip in banned table
    # if a new post has that ip, make add_post return false
    return True

