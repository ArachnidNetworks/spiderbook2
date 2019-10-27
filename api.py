from psycopg2 import connect

def dbsetup(db, user, password):
    conn = connect(f"dbname={db} user={user} password={password}")
    c = conn.cursor()
    return conn, c
conn, c = dbsetup(db="spiderbook", user="postgres", password="postgres")

def new_uid():
    pass

def get_uid():
    pass

c.close()
conn.close()
