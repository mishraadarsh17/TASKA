from utils.db import get_db_connection
def get_user_by_username(username):
    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=?",(username,))
    user=cursor.fetchone()
    conn.close()
    return user
def get_user_by_email(email):
    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email=?",(email,))
    user=cursor.fetchone()
    conn.close()
    return user
def get_user_by_id(user_id):
    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id=?",(user_id,))
    user=cursor.fetchone()
    conn.close()
    return user
def create_user(username,email,password,now):
    existing_user=get_user_by_username(username)
    existing_email=get_user_by_email(email)
    if existing_user or existing_email:
        return False
    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute("INSERT INTO users (username,email,password,created_at) VALUES(?,?,?,?)",(username,email,password,now))
    conn.commit()
    user_id=cursor.lastrowid
    conn.close()
    return user_id
def update_user(user_id,username,email):
    user=get_user_by_id(user_id)
    if not user:
        return  False
    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute("UPDATE users SET username=?, email=? WHERE id=?",(username,email,user_id))
    conn.commit()
    conn.close()
    return True
def update_password(user_id,password):
    user=get_user_by_id(user_id)
    if not user:
        return  False
    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute("UPDATE users SET password=? WHERE id=?",(password,user_id))
    conn.commit()
    conn.close()
    return True


 