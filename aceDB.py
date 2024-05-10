import psycopg2
import bcrypt
import os

db_pass = ""
conn = ""
cur = ""

def connect_database():
    global conn, cur, db_pass
    db_pass = os.environ.get('YOUR_DB_KEY')
    conn = psycopg2.connect(
        dbname="your_database",
        user="your_username",
        password=db_pass,
        host="your_host",
        port="your_port"
    )
    cur = conn.cursor()

def save_userSettings(uname,voice,volume,theme):
    connect_database()
    query = '''INSERT INTO user_settings(username,voice_preference,volume,theme) VALUES (%s,%s,%s,%s)
            ON CONFLICT (username) DO UPDATE SET voice_preference = EXCLUDED.voice_preference,
            volume = EXCLUDED.volume, theme = EXCLUDED.theme;'''
    cur.execute(query,(uname,voice,volume,theme))
    conn.commit()
    conn.close()
    
def save_userData(uname,content):
    connect_database()
    query = '''INSERT INTO user_data(username,content) VALUES (%s,%s)
            ON CONFLICT (username) DO UPDATE SET content = EXCLUDED.content;'''
    cur.execute(query,(uname,content))
    conn.commit()
    conn.close()

def get_userSettings(uname):
    connect_database()
    query = '''SELECT voice_preference, volume, theme FROM user_settings WHERE username=%s;'''
    cur.execute(query,(uname,))
    result = cur.fetchone()
    conn.close()
    
    return result
    
def get_userData(uname):
    connect_database()
    query = '''SELECT content from user_data WHERE username=%s;'''
    cur.execute(query,(uname,))
    results = cur.fetchall()
    conn.close()
    
    return results

def logOut(uname,voice,volume,theme,content):
    global conn
    connect_database()
    save_userData(uname,content)
    save_userSettings(uname,voice,volume,theme)
    
    conn.close()

def checkUser(uname):
    try:
        connect_database()
        query = '''SELECT * FROM userlogin WHERE username=%s;'''
        cur.execute(query,(uname,))
        result = cur.fetchone()
        conn.close()
        
        if result:
            return True
        else:
            return False
    except Exception:
        return False
    
def login_user(uname,pword):
    try:
        connect_database()
        query = '''SELECT password FROM userlogin WHERE username=%s;'''
        cur.execute(query,(uname,))
        result = cur.fetchone()[0]
        conn.close()
    
        hashed_pass = result.tobytes()
        new_pword = bytes(pword, encoding='utf-8')
    
        if(not(bcrypt.checkpw(new_pword, hashed_pass))):
            return False
        
        return True
    except Exception:
        return False
          
def hash_pass(pword):
    pw_bytes = bytes(pword,encoding='utf-8')
    hashed = bcrypt.hashpw(pw_bytes,bcrypt.gensalt())
    return(hashed)

def add_user(uname,pword):
    try:
        connect_database()
        new_pass = hash_pass(pword)
        query = '''INSERT INTO userlogin(username,password) VALUES (%s,%s);'''
        cur.execute(query,(uname,new_pass))        
        conn.commit()
        conn.close()
        
        return True
    except psycopg2.errors.UniqueViolation as e:
        return False
