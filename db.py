import sqlite3
import argparse
import os

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        create_db(conn)
    except Error as e:
        print(e)
    return conn

def create_db(conn):
    createExtractionTable="""CREATE TABLE IF NOT EXISTS extraction (
            id integer PRIMARY KEY,
            domain text NOT NULL,
            time text NOT NULL,
            ip text NOT NULL);"""
    try:
        c = conn.cursor()
        c.execute(createExtractionTable)
    except Error as e:
        print(e)

    createLinkTable="""CREATE TABLE IF NOT EXISTS link (
            id integer PRIMARY KEY,
            extraction_id INTEGER NOT NULL,
            content_id INTEGER,
            url text NOT NULL,
            link text NOT NULL,
            text text NOT NULL,
            content blob,
            FOREIGN KEY(extraction_id) REFERENCES extraction(id)
            FOREIGN KEY(content_id) REFERENCES content(id)
            );"""
    try:
        c = conn.cursor()
        c.execute(createLinkTable)
    except Error as e:
        print(e)

    createContentTable="""CREATE TABLE IF NOT EXISTS content (
            id integer PRIMARY KEY,
            extraction_id INTEGER NOT NULL,
            url text NOT NULL,
            content blob,
            FOREIGN KEY(extraction_id) REFERENCES extraction(id)
            );"""
    try:
        c = conn.cursor()
        c.execute(createContentTable)
    except Error as e:
        print(e)

    createScriptTable="""CREATE TABLE IF NOT EXISTS script (
            id integer PRIMARY KEY,
            extraction_id INTEGER NOT NULL,
            url text NOT NULL,
            src text NOT NULL,
            content blob,
            FOREIGN KEY(extraction_id) REFERENCES extraction(id)
            );"""
    try:
        c = conn.cursor()
        c.execute(createScriptTable)
    except Error as e:
        print(e)

    createFormTable="""CREATE TABLE IF NOT EXISTS form (
            id integer PRIMARY KEY,
            extraction_id INTEGER NOT NULL,
            url text NOT NULL,
            action text NOT NULL,
            method text NOT NULL,
            content blob,
            FOREIGN KEY(extraction_id) REFERENCES extraction(id)
            );"""
    try:
        c = conn.cursor()
        c.execute(createFormTable)
    except Error as e:
        print(e)

    createInputTable="""CREATE TABLE IF NOT EXISTS input (
            id integer PRIMARY KEY,
            extraction_id INTEGER NOT NULL,
            form_id INTEGER NOT NULL,
            name text NOT NULL,
            type text NOT NULL,
            value text NOT NULL,
            placeholder text NOT NULL,
            content blob,
            FOREIGN KEY(extraction_id) REFERENCES extraction(id)
            FOREIGN KEY(form_id) REFERENCES form(id)
            );"""
    try:
        c = conn.cursor()
        c.execute(createInputTable)
    except Error as e:
        print(e)

    createCookieTable="""CREATE TABLE IF NOT EXISTS cookie (
            id integer PRIMARY KEY,
            extraction_id INTEGER NOT NULL,
            content blob,
            FOREIGN KEY(extraction_id) REFERENCES extraction(id)
            );"""
    try:
        c = conn.cursor()
        c.execute(createCookieTable)
    except Error as e:
        print(e)

    createBrowserTable="""CREATE TABLE IF NOT EXISTS browser (
            id integer PRIMARY KEY,
            extraction_id INTEGER NOT NULL,
            name text, 
            full_version text, 
            major_version text, 
            navigator_appname text,
            navigator_appversion text,
            navigator_useragent text,
            plugin_list blob,
            os text,
            FOREIGN KEY(extraction_id) REFERENCES extraction(id)
            );"""
    try:
        c = conn.cursor()
        c.execute(createBrowserTable)
    except Error as e:
        print(e)

def get_or_insert_extraction(conn, domain, time, ip):
    sql = """SELECT id 
              FROM extraction 
              WHERE domain = ? and time = ? and ip = ?
              """
    cur = conn.cursor()
    cur.execute(sql, (domain, time, ip, ))
    rows = cur.fetchall()

    if (len(rows) > 0):
        return rows[0][0]
    else:
        sql = ''' INSERT INTO extraction(domain,time,ip)
                VALUES(?,?,?) '''
        cur = conn.cursor()
        cur.execute(sql, (domain, time, ip, ))
        return cur.lastrowid

def insert_content(conn, content):
    sql = ''' INSERT INTO content(extraction_id,url,content)
              VALUES(?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, content)
    return cur.lastrowid

def insert_cookie(conn, content):
    sql = ''' INSERT INTO cookie(extraction_id,content)
              VALUES(?,?) '''
    cur = conn.cursor()
    cur.execute(sql, content)
    return cur.lastrowid

def insert_link(conn, content):
    sql = ''' INSERT INTO link(extraction_id,url,link,text,content)
              VALUES(?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, content)
    return cur.lastrowid

def insert_script(conn, content):
    sql = ''' INSERT INTO script(extraction_id,url,src,content)
              VALUES(?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, content)
    return cur.lastrowid

def insert_form(conn, content):
    sql = ''' INSERT INTO form(extraction_id,url,action,method,content)
              VALUES(?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, content)
    return cur.lastrowid

def insert_input(conn, content):
    sql = ''' INSERT INTO input(extraction_id,form_id,name,type,value,placeholder,content)
              VALUES(?,?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, content)
    return cur.lastrowid

def insert_browser(conn, content):
    sql = ''' INSERT INTO browser(extraction_id,name,full_version,major_version,navigator_appname,navigator_appversion,navigator_useragent,plugin_list,os)
              VALUES(?,?,?,?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, content)
    return cur.lastrowid

def build_content_to_link_relationships(conn, extraction_id):
    # TODO: Loop through all the `link` table entries and check if value of the `link` column is 
    # equal to `url` of `content` table. If so, store the ID of `content` table under `content_id` 
    # column of the `link` table. 
    pass

def get_content(conn, location):
    sql = """SELECT content 
              FROM content 
              WHERE location = ? 
              """
    cur = conn.cursor()
    cur.execute(sql, location)
    row = cur.fetchone()
    return row[0]
