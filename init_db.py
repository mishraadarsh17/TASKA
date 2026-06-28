from utils.db import get_db_connection
conn=get_db_connection()
cursor=conn.cursor()
cursor.execute("""
              CREATE TABLE IF NOT EXISTS users
               (id INTEGER PRIMARY KEY AUTOINCREMENT,
               username TEXT UNIQUE NOT NULL,
               email TEXT UNIQUE NOT NULL,
               password TEXT NOT NULL,
               created_at TEXT NOT NULL
               );
            
             """)  
             
cursor.execute("""
              CREATE TABLE IF NOT EXISTS projects
               (id INTEGER PRIMARY KEY AUTOINCREMENT,
               name TEXT NOT NULL,
               description TEXT,
               owner_id INTEGER NOT NULL,
               created_at TEXT NOT NULL,
               FOREIGN KEY(owner_id)
               REFERENCES users(id)
               );

            """)
cursor.execute("""
              CREATE TABLE IF NOT EXISTS project_members
               (project_id INTEGER NOT NULL,
               member_id INTEGER NOT NULL,
               joined_at TEXT NOT NULL,  
               PRIMARY KEY (project_id,member_id),
               FOREIGN KEY(project_id)
               REFERENCES projects(id),
               FOREIGN KEY(member_id)
               REFERENCES users(id)
               );

             """) 
cursor.execute("""
              CREATE TABLE IF NOT EXISTS tasks
               (id INTEGER PRIMARY KEY AUTOINCREMENT,
               title TEXT NOT NULL,
               description TEXT,
               priority TEXT NOT NULL
               CHECK(priority IN ('Low','Medium','High')),
               status TEXT NOT NULL DEFAULT 'Pending'
               CHECK(status IN ('Pending','In Progress','On Hold','Completed')),
               due_date TEXT,
               project_id INTEGER,
               created_by INTEGER NOT NULL,
               assigned_to INTEGER,
               created_at TEXT NOT NULL,
               updated_at TEXT,
               FOREIGN KEY (project_id)
               REFERENCES projects(id),
               FOREIGN KEY (created_by)
               REFERENCES users(id),
               FOREIGN KEY (assigned_to)
               REFERENCES users(id)
               );
            """)
cursor.execute("""
              CREATE TABLE IF NOT EXISTS comments
              (id INTEGER PRIMARY KEY AUTOINCREMENT,
              task_id INTEGER NOT NULL,
              user_id INTEGER NOT NULL,
              comment TEXT NOT NULL,
              created_at TEXT NOT NULL,
              FOREIGN KEY(task_id)
              REFERENCES tasks(id),
              FOREIGN KEY(user_id)
              REFERENCES users(id)
              );
            """)
conn.commit()
conn.close()
print("Database created successfully")