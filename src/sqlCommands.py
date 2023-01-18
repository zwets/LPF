import sqlite3

def sql_execute_command(command, moss_db):
    conn = sqlite3.connect(moss_db)
    c = conn.cursor()
    c.execute(command)
    conn.commit()
    conn.close()

def sql_fetch_all(string, moss_db):
    """ Fetches query results from the database and returns them as a list of tuples"""
    conn = sqlite3.connect(moss_db)
    c = conn.cursor()
    c.execute(string)
    data = c.fetchall()
    data = [item for t in data for item in t]
    conn.close()
    return data