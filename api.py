from psycopg2 import connect
from random import randint
from hashlib import sha512
from traceback import print_exc

def dbsetup(db, user, password):
    conn = connect(f"dbname={db} user={user} password={password}")
    c = conn.cursor()
    return conn, c
conn, c = dbsetup(db="spiderbook", user="postgres", password="postgres")

def get_idns(restriction=False, arguments=()):
    query = "SELECT idn FROM idnumbers"
    if restriction:
        # if a restriction is imposed, such as a WHERE clause, add it to
        # the query, else execute it
        query += " " + restriction
    c.execute(query, arguments)
    # Return everything, in the form of a list of tuples
    return c.fetchall()

def new_idn():
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

def new_uid(chars):
    idn = new_idn()
    return sha512(bytes(idn)).hexdigest()[:chars]

def insert(data):
    try:
        table = data['table']
    except:
        print_exc()
c.close()
conn.close()
