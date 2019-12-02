from psycopg2 import connect
from random import randint
from hashlib import sha512
from traceback import print_exc
import datetime

def dt_now():
    datetime.datetime.utcnow()
    return datetime.datetime.utcnow().replace(microsecond=0)

def dbsetup(db, user, password):
    """ Connects to a database """
    conn = connect(f"dbname={db} user={user} password={password}")
    c = conn.cursor()
    return conn, c
conn, c = dbsetup(db="spiderbook", user="postgres", password="postgres")

def get_idns(restriction=False, arguments=()):
    """ Returns all ID 'root' numbers with an optional
    restriction and arguments. """
    query = "SELECT idn FROM idnumbers"
    if restriction:
        # if a restriction is imposed, such as a WHERE clause, add it to
        # the query, else execute it
        query += " " + restriction
    c.execute(query, arguments)
    # Return everything, in the form of a list of tuples
    return c.fetchall()

def new_idn():
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

def new_uid(chars=16):
    """ Returns a new hashed ID with the
    character limit being the parameter chars.
    The default value for chars is 16. """
    idn = new_idn()
    return sha512(bytes(idn)).hexdigest()[:chars]

def iterable_to_s(iterable, s):
    """ Returns a list of s in the format
    (%s, %s, %s, ...) with as many s's as
    items in the iterable """
    iters = []
    for _ in iterable:
        iters.append(s)
    return "(" + ", ".join(iters) + ")"

def remove_last_comma(string_as_list):
    if string_as_list[-2] == ',':
        # Remove last comma, if it's there
        string_as_list.pop(-2)
    return string_as_list

def format_for_query(s, single_quotes=False, comma=False, par=False):
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

def insert(data):
    """ Inserts data into a PostgreSQL database.
    It's dynamic, using the 'table' key as the table
    and considering any other key:value pair a
    column:value pair. """
    try:
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
    except:
        print_exc()
        return False

def update(data):
    try:
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
    except:
        print_exc()
        return False

def cr_to_dict(rows, cols):
    """ Returns a tuple of dictionaries, with
    each dictionary being a single row, having
    the columns as keys. """
    result_table = ()
    for row in rows:
        result_table += ({cols[i]: row[i] for i in range(len(cols))},)
    return result_table

def select(data, restriction=''):
    try:
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
        query += " FROM " + table + " " + restriction
        # Execute the query and extract the rows
        c.execute(query)
        rows = c.fetchall()
        # Format the results into a dictionary format
        return cr_to_dict(rows, cols)
    except:
        print_exc()
        return False

def add_post(request):
    """ Adds a post based on the Flask request's data. """
    try:
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
    except:
        print_exc()
        return False

def reply(request):
    """ Replies to a post """
    try:
        reply_uid = new_uid(32)
        reply_post(request, reply_uid)
        reply_update(request, reply_uid)
        return True
    except:
        print_exc()
        return False

def reply_post(request, reply_uid):
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

def reply_update(request, reply_uid):
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

def get_posts(limit=100, category='all'):
    try:
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
    except:
        print_exc()
        return False

def get_post(request):
    uid = request.args['uid']
    restriction = f'WHERE uid = \'{uid}\''
    post = select({
        'table': 'posts',
        'cols': ['uid', 'title', 'category', 'body_text', 'body_file_url', 'dt', 'reply_uids']
    }, restriction)
    if len(post) > 0:
        return post
    else:
        return False

def get_replies(post, limit=100):
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

def get_post_and_replies(request, reply_limit):
    try:
        post = get_post(request)
        if post:
            replies = get_replies(post, reply_limit)
        else:
            return False
    except:
        print_exc()
        return False
