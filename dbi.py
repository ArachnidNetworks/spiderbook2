import hashlib, datetime
import psycopg2

# Password hasher
def hashpass(password):
    return hashlib.sha1(password.encode()).hexdigest()[:24]

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
    c.execute("SELECT * FROM users WHERE email = %s AND pass = %s", (e, p))
    res = c.fetchall()
    if res:
        return True
    else:
        return False
