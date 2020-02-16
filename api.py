#!/usr/bin/env python
from psycopg2 import connect
from random import randint
from hashlib import sha512
from decorator import decorator
from typing import Literal
from re import match
import datetime

def dbsetup(db:str, user:str, password:str):
    """ Connects to a database """
    conn = connect(f"dbname={db} user={user} password={password}")
    c = conn.cursor()
    return conn, c
    conn, c = dbsetup(db="spiderbook", user="postgres", password="postgres")

# Utility Functions

def dt_now() -> datetime.datetime:
    datetime.datetime.utcnow()
    return datetime.datetime.utcnow().replace(microsecond=0)

def iterable_to_s(iterable, s:str) -> str:
    """ Returns a list of s in the format
    (%s, %s, %s, ...) with as many s's as
    items in the iterable """
    iters = []
    for _ in iterable:
        iters.append(s)
    return "(" + ", ".join(iters) + ")"

def remove_last_comma(string_as_list:list) -> list:
    if string_as_list[-2] == ',':
        # Remove last comma, if it's there
        string_as_list.pop(-2)
    return string_as_list

def format_for_query(s, single_quotes:bool=False, comma:bool=False, par:bool=False) -> str:
    """ Removes, optionally, single quotes, the comma
    next to the last parenthesis, if there
    is one, and the parenthesis
    themselves. """
    if not single_quotes:
        s = s.replace("'", '')
    s = list(s)
    if not comma:
        remove_last_comma(s)
    if not par:
        # Remove parenthesis
        s.pop(0)
        s.pop(-1)
    s = "".join(s)
    return s

def cr_to_dict(rows: tuple, cols: tuple) -> tuple:
    """ Returns a tuple of dictionaries, with
    each dictionary being a single row, having
    the columns as keys. """
    result_table = ()
    for row in rows:
        result_table += ({cols[i]: row[i] for i in range(len(cols))},)
    return result_table

def secure_hash(data: str, chars: int=16) -> str:
    hashed = data
    for _ in range(1000):
        hashed = sha512(hashed.encode("utf-8")).hexdigest()
    return hashed[:chars]

# Database Interaction

def get_idns(restriction: str = '', arguments=()):
    """ Returns all ID 'root' numbers with an optional
    restriction and arguments. """
    query = "SELECT idn FROM idnumbers"
    query += " " + restriction
    c.execute(query, arguments)
    # Return everything, in the form of a list of tuples
    return c.fetchall()

def new_idn() -> int:
    """ Adds a new number to the idnumbers table and returns
    it. The new number is the last plus a random value
    between 1 and 9. """
    # get the latest (biggest) id number
    last_id = get_idns(restriction="ORDER BY idn DESC")[0][0]
    # add a random value between 1 and 10 to it
    new = last_id + randint(1, 10)
    query = "INSERT INTO idnumbers (idn) VALUES (%s)"
    arguments = (new,)
    c.execute(query, arguments)
    conn.commit()
    # return the latest idn
    return new

def new_uid(chars: int = 16) -> str:
    """ Returns a new hashed ID with the
    character limit being the parameter chars.
    The default value for chars is 16. """
    idn = new_idn()
    return secure_hash(str(idn), chars)

def insert(data:str) -> bool:
    """ Inserts data into a PostgreSQL database.
    It's dynamic, using the 'table' key as the table
    and considering any other key:value pair a
    column:value pair. """
    table = data['table']
    data.pop('table')
    cols = str(tuple(data.keys()))
    cols = format_for_query(cols, par=True)
    value_placeholders = iterable_to_s(data.keys(), '%s')
    values = tuple(data.values())
    
    query = "INSERT INTO " + table + " " + cols + " VALUES " + value_placeholders
    c.execute(query, values)
    conn.commit()
    return True

def update(data:str) -> bool:
    table = data['table']
    data.pop('table')
    restriction = data.get('restriction')
    if restriction:
        data.pop('restriction')
    else:
        restriction = ''
    column = tuple(data.keys())[0]
    new_value = data[column]
    query = f'UPDATE {table} SET {column} = {new_value} {restriction}'
    c.execute(query)
    conn.commit()
    return True

def delete(data:str) -> bool:
    table = data['table']
    data.pop('table')
    restriction = data.get('restriction')
    if restriction:
        data.pop('restriction')
    else:
        restriction = ''
    query = f'DELETE FROM {table} * {restriction}'
    c.execute(query)
    conn.commit()
    return True

def select(data:str, restriction:str=''):
    table = data['table']
    data.pop('table')
    # Start the query
    query = "SELECT "
    # If columns weren't specified, add a * to the query,
    # else add the formatted columns
    cols = data.get('cols')
    if cols == None:
        query += '*'
    else:
        cols = tuple(cols)
        query += format_for_query(str(cols))
    # Add the table and restriction to the query
    query += f" FROM {table} {restriction}"
    # Execute the query an`d extract the rows
    c.execute(query)
    rows = c.fetchall()
    # Format the results into a dictionary format
    return cr_to_dict(rows, cols)

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

