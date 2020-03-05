#!/usr/bin/env python
from psycopg2 import connect
from random import randint
from hashlib import sha512
import datetime

# Raw database functions


class DBInterface:
    def __init__(self, db: str, user: str, password: str):
        self.setup(db, user, password)

    def setup(self, db: str, user: str, password: str):
        """Connects to a database"""
        self.conn = connect(f"dbname={db} user={user} password={password}")
        self.c = self.conn.cursor()

    def get_idns(self, restriction: str = '', arguments=()):
        """Returns all ID 'root' numbers with an optional restriction and arguments."""
        query = "SELECT idn FROM idnumbers"
        query += " " + restriction
        self.c.execute(query, arguments)
        # Return everything, in the form of a list of tuples
        return self.c.fetchall()

    def new_idn(self) -> int:
        """Adds a new number to the idnumbers table and returns it.
        The new number is the last plus a random value between 1 and 9."""
        # get the latest (biggest) id number
        last_id = self.get_idns(restriction="ORDER BY idn DESC")[0][0]
        # add a random value between 1 and 10 to it
        new = last_id + randint(1, 10)
        query = "INSERT INTO idnumbers (idn) VALUES (%s)"
        arguments = (new,)
        self.c.execute(query, arguments)
        self.conn.commit()
        # return the latest idn
        return new

    def new_uid(self, chars: int = 16) -> str:
        """Returns a new hashed ID with the character limit being the parameter chars.
        The default value for chars is 16."""
        idn = self.new_idn()
        return secure_hash(str(idn), chars)

    def insert(self, data: dict) -> bool:
        """Inserts data into a PostgreSQL database.
        It's dynamic, using the 'table' key as the table
        and considering any other key:value pair a
        column:value pair."""
        table = data['table']
        data.pop('table')
        cols = str(tuple(data.keys()))
        cols = format_for_query(cols, par=True)
        value_placeholders = iterable_to_s(data.keys(), '%s')
        values = tuple(data.values())

        query = "INSERT INTO " + table + " " + cols + " VALUES " + value_placeholders
        self.c.execute(query, values)
        self.conn.commit()
        return True

    def update(self, data: str) -> bool:
        """Updates a PostgreSQL database."""
        table = data['table']
        data.pop('table')
        restriction = data.get('restriction')
        if restriction:
            data.pop('restriction')
        else:
            restriction = ''
        column = tuple(data.keys())[0]
        new_value = data[column]
        query = f'UPDATE {table} SET {column} = %s {restriction}'
        print(query)
        print((new_value,))
        self.c.execute(query, (new_value,))
        self.conn.commit()
        return True

    def delete(self, data: str) -> bool:
        """Deletes a row from a PostgreSQL database"""
        table = data['table']
        data.pop('table')
        restriction = data.get('restriction')
        if restriction:
            data.pop('restriction')
        else:
            restriction = ''
        query = f'DELETE FROM {table} * {restriction}'
        self.c.execute(query)
        self.conn.commit()
        return True

    def select(self, data: str, restriction: str = '') -> tuple:
        """Selects rows from a PostgreSQL database"""
        table = data['table']
        data.pop('table')
        # Start the query
        query = "SELECT "
        # If columns weren't specified, add a * to the query,
        # else add the formatted columns
        cols = data.get('cols')
        if cols is None:
            query += '*'
        else:
            cols = tuple(cols)
            query += format_for_query(str(cols))
        # Add the table and restriction to the query
        query += f" FROM {table} {restriction}"
        # Execute the query an`d extract the rows
        self.c.execute(query)
        rownames = self.c.fetchall()
        colnames = list(map(lambda column: column[0], self.c.description))
        # Format the results into a dictionary format and put them in a tuple
        result = cr_to_dict(rownames, colnames)
        return result if len(result) > 0 else False

# Utility


def dt_now() -> datetime.datetime:
    return datetime.datetime.utcnow().replace(microsecond=0)


def dt_plus_hour(hours: int):
    return dt_now() + datetime.timedelta(hours=hours)


def iterable_to_s(iterable, s: str) -> str:
    """Returns a list of s in the format
    (%s, %s, %s, ...) with as many s's as
    items in the iterable"""
    iters = []
    for _ in iterable:
        iters.append(s)
    return "(" + ", ".join(iters) + ")"


def remove_last_comma(string_as_list: list) -> list:
    if string_as_list[-2] == ',':
        # Remove last comma, if it's there
        string_as_list.pop(-2)
    return string_as_list


def format_for_query(s, single_quotes: bool = False, comma: bool = False, par: bool = False) -> str:
    """Removes, optionally, single quotes, the comma
    next to the last parenthesis, if there
    is one, and the parenthesis
    themselves."""
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
    """Returns a tuple of dictionaries, with
    each dictionary being a single row, having
    the columns as keys."""
    result_table = ()
    for row in rows:
        result_table += ({cols[i]: row[i] for i in range(len(cols))},)
    return result_table


def secure_hash(data: str, chars: int = 16) -> str:
    hashed = data
    for _ in range(500):
        hashed = sha512(hashed.encode("utf-8")).hexdigest()
    return hashed[:chars]
