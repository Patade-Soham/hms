import os
from contextlib import contextmanager

import mysql.connector
from flask import current_app, g


def get_db_config() -> dict:
    return {
        "host": os.getenv("DB_HOST", "127.0.0.1"),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", ""),
        "database": os.getenv("DB_NAME", "hms"),
        "port": int(os.getenv("DB_PORT", "3306")),
        "autocommit": False,
    }


def get_db():
    if "db_conn" not in g:
        g.db_conn = mysql.connector.connect(**get_db_config())
    return g.db_conn


def close_db(e=None):
    conn = g.pop("db_conn", None)
    if conn is not None and conn.is_connected():
        conn.close()


@contextmanager
def get_cursor(dictionary: bool = True):
    cursor = get_db().cursor(dictionary=dictionary)
    try:
        yield cursor
    finally:
        cursor.close()


def fetch_one(query: str, params: tuple = ()):
    with get_cursor(dictionary=True) as cursor:
        cursor.execute(query, params)
        return cursor.fetchone()


def fetch_all(query: str, params: tuple = ()):
    with get_cursor(dictionary=True) as cursor:
        cursor.execute(query, params)
        return cursor.fetchall()


def execute(query: str, params: tuple = (), *, commit: bool = True):
    conn = get_db()
    with get_cursor(dictionary=False) as cursor:
        cursor.execute(query, params)
        lastrowid = cursor.lastrowid
    if commit:
        conn.commit()
    return lastrowid


def execute_many(query: str, seq_params, *, commit: bool = True):
    conn = get_db()
    with get_cursor(dictionary=False) as cursor:
        cursor.executemany(query, seq_params)
    if commit:
        conn.commit()


def rollback():
    conn = get_db()
    conn.rollback()


def init_app(app):
    app.teardown_appcontext(close_db)
