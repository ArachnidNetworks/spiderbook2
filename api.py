from psycopg2 import connect
from random import randint
from hashlib import sha512
from traceback import print_exc

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

def format_for_query(s):
    """ Removes single quotes and the comma
    next to the last parenthesis, if there
    is one. """
    s = s.replace("'", '')
    if s[-2] == ',':
        s = list(s)
        s.pop(-2)
        s = "".join(s)
    return s

def insert(data, restriction=False):
    try:
        table = data['table']
        data.pop('table')
        cols = str(tuple(data.keys()))
        cols = format_for_query(cols)
        value_placeholders = iterable_to_s(data.keys(), '%s')
        values = tuple(data.values())
        
        query = "INSERT INTO " + table + " " + cols + " VALUES " + value_placeholders
        c.execute(query, values)
        conn.commit()
        return True
    except:
        print_exc()
        return False

insert(
    {
        'table': 'idnumbers',
        'idn': 8
    }
)

c.close()
conn.close()
