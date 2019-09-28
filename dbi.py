import hashlib, random, base64, os
from datetime import datetime
import psycopg2

# Hasher
def hash_str(s, limit=None):
    if not limit: limit = 40
    return hashlib.sha1(s.encode()).hexdigest()[:limit]

# Delete the last element in a string
def del_last(t):
    t = list(t)
    t.pop()
    return ''.join(t)

# Turn a tuple of values from PostgreSQL into a dictionary with column names as keys
def row_to_dict(row, c):
    colnames = [desc.name for desc in c.description]
    return dict(zip(colnames, list(row)))

# Connect to PostgreSQL
conn = psycopg2.connect("dbname=spiderbook user=postgres")
c = conn.cursor()

# Resets connection in case of errors
def reset_con():
    global conn
    global c
    conn = psycopg2.connect("dbname=spiderbook user=postgres")
    c = conn.cursor()

# Get posts with an optional category filter
def get_posts(fter=None, values=None):
    if not fter:
        c.execute("SELECT * FROM posts")
    else:
        c.execute("SELECT * FROM posts " + str(fter), values)

    # Make a list of dicts with the keys being the rows and each row from c.fetchall() being
    # the values
    frows = c.fetchall()
    rows = []
    for row in frows:
        rows.append(row_to_dict(row, c))
    return rows

# Get all categories
def format_cat(rows):
    cats = {}
    for row in rows:
        category = row['category']
        count = row['count']
        cats[category] = count
    return cats

def cats_query(query, limit=None, values=None, d=None):
    if limit:
        query += " LIMIT %s"
        if values: values += (limit,)
        else: values = (limit,)
    if values: c.execute(query, values)
    else: c.execute(query)
    if d:
        frows = c.fetchall()
        rows = []
        for row in frows:
            rows.append(row_to_dict(row, c))
        return format_cat(rows)
    else:
        return c.fetchall()

def get_popular_cats(limit):
    cats = cats_query("""SELECT category, COUNT(category) FROM posts
    GROUP BY category ORDER BY COUNT DESC""", limit)
    popular = []
    for cat, count in cats:
        popular.append(cat)
    return popular

def get_hot_cats(limit):
    hot = []
    curdate = datetime.now().date()
    cats = cats_query("""SELECT category, COUNT(category) FROM posts
        WHERE curdate = %s GROUP BY category""", values=(curdate,), d=True)
    ns = list(cats.values())
    ns.sort(reverse=True)
    amm = len(ns)
    if amm >= limit:
        amm = limit
    for x in range(amm):
        for cat, count in cats.items():
            if cats[cat] == ns[x]:
                hot.append(cat)
    return hot

# Sign in to a user
def login(e, p):
    print(e, p)
    c.execute("SELECT * FROM users WHERE email = %s AND pass = %s", (e, p))
    res = c.fetchall()
    if res:
        return True
    else:
        return False

# Create a post with the form data harvested at the view function
def get_new_pid(create_new):
    c.execute("SELECT * FROM ids ORDER BY v DESC LIMIT 1")
    last_id = c.fetchone()[0]
    uhs_new_pid = last_id + random.randint(1, 9)
    if create_new:
        c.execute("INSERT INTO ids (v) VALUES (%s)", (uhs_new_pid,))
        conn.commit()
    return hash_str(str(uhs_new_pid), 25)

def get_cols(data):
    cols = [str(key) for key in data.keys()]
    scols = str(cols).replace('[', '').replace(']', '').replace("'", '')
    return cols, scols

def create_vals(data, pid, cols):
    vals = (pid,)
    for col in cols:
        if data[col] == 'None': data[col] = None
        vals += (data[col],)
    return vals

def get_val_placeholders(data):
    val_placeholders = ''
    for _ in range(len(data.keys())+1):
        val_placeholders += '%s, '
    return val_placeholders

def find_cat(category):
    c.execute("SELECT category FROM posts WHERE category = %s", (category,))
    if len(c.fetchall()) < 1:
        return False
    else:
        return True

def insert_row(data):
    new_pid = get_new_pid(True)
    table = data['table']
    data.pop('table')
    # cols is a list of the columns from the data, and scols is that list
    # converted to a formatted string
    cols, scols = get_cols(data)
    # val_placeholders store the specific amount of keys+1 in a string made
    # up of multiple '%s, ', with 2 del_last() being called to remove the
    # last space and comma.
    val_placeholders = del_last(del_last(get_val_placeholders(data)))
    query = f"""INSERT INTO {table} (pid, {scols}) VALUES ({val_placeholders})"""
    vals = create_vals(data, new_pid, cols)
    try:
        c.execute(query, vals)
        conn.commit()
        return True
    except Exception as e:
        reset_con()
        raise e
