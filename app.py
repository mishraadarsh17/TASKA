import os
from dotenv import load_dotenv
load_dotenv()
from flask import Flask,render_template,session,redirect
from routes.auth import auth_bp
from routes.project import project_bp 
from routes.task import task_bp 
from utils.decorators import login_required
from models.project import total_projects
from models.task import recent_tasks,total_tasks
app=Flask(__name__)
app.register_blueprint(auth_bp)
app.register_blueprint(project_bp)
app.register_blueprint(task_bp)
import init_db
app.secret_key = os.getenv("SECRET_KEY")
@app.route("/")
@login_required
def home():
    if "user_id" in session:
        return redirect("/dashboard")
    return redirect("/login")
    
@app.route("/dashboard")
@login_required
def dashboard():
    user_id=session["user_id"]
    user_name=session["username"]
    total_project=total_projects(user_id)
    total_personal_task,\
    total_assigned_task,\
    total_pending_task,\
    total_completed_task = total_tasks(user_id)
    total_task_number=total_personal_task+total_assigned_task
    my_recent_tasks=recent_tasks(user_id,user_id)
    return render_template("dashboard.html",total_project=total_project,total_personal_task=total_personal_task,total_assigned_task=total_assigned_task,total_pending_task=total_pending_task,total_completed_task=total_completed_task,my_recent_tasks=my_recent_tasks,total_task_number=total_task_number,username=user_name)

@app.errorhandler(404)
def page_not_found(error):

    if "user_id" not in session:
        return redirect("/login")

    return render_template("404.html"),404

@app.errorhandler(500)
def internal_server_error(error):

    if "user_id" not in session:
        return redirect("/login")

    return render_template("500.html"),500


if __name__=="__main__":
    app.run(debug=True)
