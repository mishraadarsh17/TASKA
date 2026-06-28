from utils.db import get_db_connection
from models.project import get_project_by_id,get_member
def create_task(title,description,priority,status,created_by,now,assigned_to,project_id,due_date):
    if not project_id and assigned_to:
        return False
    if project_id:  
        project=get_project_by_id(project_id)
        if not project:
            return False
    if assigned_to:
        member=get_member(project_id,assigned_to) 
        if not member:
            return False
    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute("""INSERT INTO tasks (title,description,priority,status,created_by,created_at,assigned_to,project_id,due_date)
                    values(?,?,?,?,?,?,?,?,?)""",(title,description,priority,status,created_by,now,assigned_to,project_id,due_date))
    conn.commit()
    task_id=cursor.lastrowid
    conn.close()
    return task_id
def get_task_by_id(task_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""SELECT tasks.*, users.username AS assigned_username, projects.name AS project_name FROM tasks LEFT JOIN users
           ON tasks.assigned_to = users.id LEFT JOIN projects ON tasks.project_id = projects.id WHERE tasks.id = ? """, (task_id,))
    task = cursor.fetchone()
    conn.close()
    return task
def get_project_task(project_id,status="",priority=""):
    project=get_project_by_id(project_id)
    if not project:
        return False
    conn=get_db_connection()
    cursor=conn.cursor()
   
    query="""SELECT tasks.*,users.username AS assigned_username  
                   FROM tasks LEFT JOIN users ON tasks.assigned_to=users.id WHERE project_id=? """
    params=[project_id]
    if status:
        query+=" AND status=?"
        params.append(status)
    if priority:
        query+=" AND priority=?"
        params.append(priority)
    query+=" ORDER BY created_at DESC"
    cursor.execute(query,params)
    # cursor.execute("""SELECT tasks.*,users.username AS assigned_username  
    #                FROM tasks LEFT JOIN users ON tasks.assigned_to=users.id WHERE project_id=?""",(project_id,))
    tasks=cursor.fetchall()
    conn.close()
    return tasks

def assigned_tasks(user_id):
    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE  assigned_to=? ORDER BY created_at DESC",(user_id,))
    tasks=cursor.fetchall()
    conn.close()
    return tasks
def personal_tasks(user_id):
    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE project_id IS NULL AND created_by=? ORDER BY created_at DESC",(user_id,))
    tasks=cursor.fetchall()
    conn.close()
    return tasks
def update_task(user_id,task_id,title,description,priority,status,due_date,assigned_to,updated_at):
    task=get_task_by_id(task_id)
    if not task or user_id not in(task["created_by"],task["assigned_to"]):
        return False
    conn=get_db_connection()
    cursor=conn.cursor()
    if task["created_by"]==user_id:
        cursor.execute("""UPDATE tasks SET title=?,description=?,priority=?,status=?,due_date=?,assigned_to=?,updated_at=? 
                       WHERE id=?""",(title,description,priority,status,due_date,assigned_to,updated_at,task_id))
    elif task["assigned_to"]==user_id:
        cursor.execute("UPDATE tasks SET status=?,updated_at=? WHERE id=?",(status,updated_at,task_id))
    else:
        return False
    conn.commit()
    conn.close()
    return True
def delete_task(task_id,user_id):
    task=get_task_by_id(task_id)
    if not task or task["created_by"]!=user_id: 
        return False
    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id=?",(task_id,))
    conn.commit()
    conn.close()
    return True
def recent_tasks(user_id,created_by):
    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE  assigned_to=? OR (project_id IS NULL AND created_by=?) ORDER BY created_at DESC",(user_id, created_by))
    tasks=cursor.fetchall()
    conn.close()
    return tasks
def total_tasks(user_id):
    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute("SELECT COUNT (*) FROM tasks WHERE project_id IS NULL AND created_by=?",(user_id,))
    total_personal_task=cursor.fetchone()[0]
    cursor.execute("SELECT COUNT (*) FROM tasks WHERE assigned_to=?",(user_id,))
    total_assigned_task=cursor.fetchone()[0]
    cursor.execute("SELECT COUNT (*) FROM tasks WHERE (assigned_to=?  OR (project_id IS NULL AND created_by=?)) AND status=?",(user_id,user_id,"Pending"))
    total_pending_task=cursor.fetchone()[0]
    cursor.execute("SELECT COUNT (*) FROM tasks WHERE (assigned_to=?  OR (project_id IS NULL AND created_by=?)) AND status=?",(user_id,user_id,"Completed",))
    total_completed_task=cursor.fetchone()[0]
    conn.close()
    return total_personal_task,total_assigned_task,total_pending_task,total_completed_task
def search_tasks(user_id,query):
    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute("""SELECT * FROM tasks WHERE (assigned_to=? OR (project_id IS NULL AND created_by=?)) AND (title LIKE ? OR description LIKE ?
    OR priority LIKE ? OR status LIKE ?) ORDER BY created_at DESC""",(user_id,user_id,f"%{query}%",f"%{query}%",f"%{query}%",f"%{query}%"))
    tasks=cursor.fetchall()
    conn.close()
    return tasks
def get_filtered_tasks(user_id,status,priority):

    conn=get_db_connection()
    cursor=conn.cursor()
    query="""SELECT * FROM tasks WHERE (assigned_to=? OR (project_id IS NULL AND created_by=?))"""
    params=[user_id,user_id]
    if status:
        query+=" AND status=?"
        params.append(status)
    if priority:
        query+=" AND priority=?"
        params.append(priority)
    query+=" ORDER BY created_at DESC"
    cursor.execute(query,params)
    tasks=cursor.fetchall()
    conn.close()
    return tasks