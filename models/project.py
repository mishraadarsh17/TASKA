from utils.db import get_db_connection
from models.user import get_user_by_username
def create_project(name,description,owner_id,now):
    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute("INSERT INTO projects (name,description,owner_id,created_at) values(?,?,?,?)",(name,description,owner_id,now))
    conn.commit()
    project_id=cursor.lastrowid
    conn.close()
    return project_id
def get_users_project(user_id):
    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute("""SELECT projects.*,
    COUNT(DISTINCT tasks.id) as task_count,
    COUNT(DISTINCT project_members.member_id) as member_count

    FROM projects

    LEFT JOIN tasks
    ON projects.id = tasks.project_id

    LEFT JOIN project_members
    ON projects.id = project_members.project_id

    WHERE projects.owner_id=?

    GROUP BY projects.id ORDER BY created_at DESC
    """,(user_id,))
    projects=cursor.fetchall()
    conn.close()
    return projects
def get_project_by_id(project_id):
    conn=get_db_connection() 
    cursor=conn.cursor()
    cursor.execute("SELECT *,users.username as owner_name FROM projects JOIN users ON projects.owner_id=users.id WHERE projects.id=?",(project_id,))
    project=cursor.fetchone()
    conn.close()
    return project
def edit_project(user_id,project_id,name,description):
    project=get_project_by_id(project_id)
    if not project or project["owner_id"]!=user_id:
        return False
    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute("UPDATE projects SET name=?, description=? WHERE id=?",(name,description,project_id,))
    conn.commit()
    conn.close()
    return True
def delete_project(user_id,project_id):
    project=get_project_by_id(project_id)
    if not project or project["owner_id"]!=user_id:
        return False
    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute("DELETE from comments WHERE task_id IN (SELECT id FROM tasks WHERE project_id=?)",(project_id,))
    cursor.execute("DELETE from tasks WHERE project_id=?",(project_id,))
    cursor.execute("DELETE from project_members WHERE project_id=?",(project_id,))
    cursor.execute("DELETE from projects WHERE id=?",(project_id,))
    conn.commit()
    conn.close()
    return True 
def get_member(project_id,member_id):
    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute("SELECT * FROM project_members WHERE project_id=? AND member_id=?",(project_id,member_id))
    member=cursor.fetchone()
    conn.close()
    return member 
def add_member(user_id,project_id,member_username,now):
    project=get_project_by_id(project_id)
    user=get_user_by_username(member_username)
    if not user :
        return False
    member_id=user["id"]    
    if member_id == project['owner_id']:
        return False
    if not project or project["owner_id"]!=user_id:
        return False
    member=get_member(project_id,member_id)
    if member:
        return False
    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute("INSERT INTO project_members (project_id,member_id,joined_at) VALUES(?,?,?)",(project_id,member_id,now))
    conn.commit()
    conn.close()
    return True 
def get_project_members(project_id):
    project=get_project_by_id(project_id)
    if not project:
        return False
    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute("""SELECT users.id,users.username FROM project_members 
                   JOIN users ON project_members.member_id=users.id WHERE project_members.project_id=? ORDER BY joined_at DESC""",(project_id,))
    members=cursor.fetchall()
    conn.close()
    return members
def delete_member(user_id,project_id,member_id):
    project=get_project_by_id(project_id)
    if not project or project["owner_id"]!=user_id or member_id == project["owner_id"]:
        return False
    if member_id == project["owner_id"]:
        return False
    member=get_member(project_id,member_id)
    if not member:
        return False
    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute("UPDATE tasks SET assigned_to=NULL WHERE project_id=? AND assigned_to=?",(project_id, member_id))
    cursor.execute("DELETE FROM project_members WHERE project_id=? AND member_id=?",(project_id,member_id))
    conn.commit()
    conn.close()
    return True
def is_member(project_id, user_id):
    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute( """SELECT * FROM project_members WHERE project_id=? AND member_id=?""",(project_id, user_id))
    member=cursor.fetchone()
    conn.close()
    return member is not None
def associated_projects(user_id):
    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute("""SELECT projects.*,
    COUNT(DISTINCT tasks.id) as task_count,
    COUNT(DISTINCT project_members.member_id) as member_count

    FROM project_members

    JOIN projects
    ON project_members.project_id=projects.id

    LEFT JOIN tasks
    ON projects.id=tasks.project_id

    LEFT JOIN project_members pm2
    ON projects.id=pm2.project_id

    WHERE project_members.member_id=?

    GROUP BY projects.id ORDER BY created_at DESC
    """,(user_id,))    
    projects=cursor.fetchall()
    conn.close()
    return projects
def total_projects(user_id):
    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute("SELECT COUNT (*) FROM projects WHERE owner_id=?",(user_id,))
    total1=cursor.fetchone()[0]
    cursor.execute("""SELECT COUNT(*) FROM project_members JOIN projects ON project_members.project_id=projects.id WHERE project_members.member_id=? """,(user_id,))
    total2=cursor.fetchone()[0]
    conn.close()
    total=total1+total2
    return total
def search_projects(query, user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""SELECT DISTINCT projects.* FROM projects LEFT JOIN project_members ON projects.id = project_members.project_id
    WHERE (projects.owner_id=? OR project_members.member_id=?) AND (projects.name LIKE ? OR projects.description LIKE ?) ORDER BY created_at DESC""", (user_id,user_id, f"%{query}%", f"%{query}%"))
    projects = cursor.fetchall()
    conn.close()
    return projects




