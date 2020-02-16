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

