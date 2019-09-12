import hashlib, datetime, random
import psycopg2

# Password hasher
def hashpass(password):
    return hashlib.sha1(str(password).encode()).hexdigest()[:24]

# Delete the last element in a string
def del_last(t):
    t = list(t)
    t.pop()
    return ''.join(t)

# Connect to PostgreSQL
conn = psycopg2.connect("dbname=spiderbook user=postgres")
c = conn.cursor()

# Get posts with an optional category filter
def get_posts(category=None):
    if not category:
        c.execute("SELECT * FROM posts")
    else:
        c.execute("SELECT * FROM posts WHERE category = %s", (category,))

    # Make a list of dicts with the keys being the rows and each row from c.fetchall() being
    # the values
    els = []
    rows = c.fetchall()
    colnames = [desc.name for desc in c.description]
    for row in rows:
            els.append(dict(zip(colnames, list(row))))
    return els

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
def get_new_pid():
    c.execute("SELECT * FROM ids ORDER BY v DESC LIMIT 1")
    last_id = c.fetchone()[0]
    uhs_new_pid = last_id + random.randint(1, 9)
    c.execute("INSERT INTO ids (v) VALUES (%s)", (uhs_new_pid,))
    conn.commit()
    return hashpass(uhs_new_pid)

def get_cols(data):
    cols = [str(key) for key in data.keys()]
    scols = str(cols).replace('[', '').replace(']', '').replace("'", '')
    return cols, scols

def create_vals(data, pid, cols):
    vals = (pid,)
    for col in cols:
        vals += (data[col],)
    return vals

def get_val_placeholders(data):
    val_placeholders = ''
    for _ in range(len(data.keys())+1):
        val_placeholders += '%s, '
    return val_placeholders

def insert_row(data):
    new_pid = get_new_pid()
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
    print(query)
    print(vals)
    c.execute(query, vals)
    conn.commit()
