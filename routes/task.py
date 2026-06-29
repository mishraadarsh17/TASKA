from flask import Blueprint,request,redirect,render_template,flash,session
from datetime import datetime
from utils.decorators import login_required
from  models.project import get_project_by_id,get_project_members,search_projects
from models.task import create_task as create_task_model,get_task_by_id,delete_task as delete,update_task as update,search_tasks,recent_tasks,personal_tasks,assigned_tasks,get_filtered_tasks
task_bp=Blueprint("task_bp",__name__,url_prefix="/task")

valid_status = ["Pending", "In Progress", "On Hold", "Completed"]
valid_priority = ["Low", "Medium", "High"]
@task_bp.route("/create/<int:project_id>",methods=["GET","POST"])
@login_required
def create_task(project_id):
    user_id=session["user_id"]
    project=get_project_by_id(project_id)
    if not project or user_id!=project["owner_id"]:
        flash ("access denied")
        return redirect("/")
    if request.method=="POST":
        title=request.form.get("title","").strip()
        description=request.form.get("description","").strip()
        priority=request.form.get("priority","").strip()
        status=request.form.get("status","").strip()
        due_date=request.form.get("due_date","")
        now=datetime.now().strftime("%Y-%m-%d %H:%M")
        member_id=request.form.get("member_id","").strip()
        if not member_id:
            member_id=None
        if title and priority and status and len(title)<50 and len(description)<500 and status  in valid_status and priority  in valid_priority:
            task=create_task_model(title,description,priority,status,project["owner_id"],now,member_id,project_id,due_date)
            if task:
                flash("task added successfully")
                return redirect(f"/project/detailes/{project_id}")
        else:
            flash("invalid input")
    members=get_project_members(project_id)
    return render_template ("task.html",project=project,members=members)
@task_bp.route("/delete/<int:task_id>")
@login_required
def delete_task(task_id):
    user_id=session["user_id"]
    next_page = request.args.get("next", "/task/personal")
    task=get_task_by_id(task_id)
    if not task or user_id!=task["created_by"] :
        flash("Action not Allowed")
        return redirect("/")
    deleted=delete(task_id,user_id)
    if deleted:
        flash("task deleted")
    else:
        flash("Action not Allowed")
    if task["project_id"] is None:
        return redirect(next_page)
    else:
        return redirect(f"/project/detailes/{task['project_id']}")  
    
@task_bp.route("/update/<int:task_id>",methods=["GET","POST"])
@login_required
def update_task(task_id):
    user_id=session["user_id"]
    next_page = request.args.get("next", "/project/personal")
    task=get_task_by_id(task_id)
    if not task:
        flash("task not found")
        return redirect("/")
    if user_id != task["created_by"] and user_id != task["assigned_to"]:
        flash("Access denied.")
        return redirect(next_page)
    assigned_only = (user_id == task["assigned_to"] and user_id != task["created_by"])
    if request.method=="POST":
        title=request.form.get("title","").strip()
        description=request.form.get("description","").strip()
        priority=request.form.get("priority","").strip()
        status=request.form.get("status","").strip()
        due_date=request.form.get("due_date","")
        now=datetime.now().strftime("%Y-%m-%d %H:%M")
        member_id=request.form.get("member_id","").strip()
        if not member_id:
            member_id=None
        if assigned_only:
            if status in valid_status:
                if status in valid_status:
                    updated = update(user_id,task_id,"","","",status,"",None,now)
                    if updated:
                        flash("task updated successfully")
                    else:
                        flash("action not allowed")
                    if task["project_id"] is None:
                        return redirect(f"/task/details/{task_id}")
                    else:
                        return redirect(f"/project/detailes/{task['project_id']}")
                else:
                    flash("Invalid status.")
                    return redirect(f"/task/update/{task_id}")
        else:
            if title and priority and status and len(title)<50 and len(description)<500 and status  in valid_status and priority  in valid_priority:
                updated=update(user_id,task_id,title,description,priority,status,due_date,member_id,now)
                if updated:
                    flash("task updated successfully")
                else:
                    flash("action not allowed")
                if task["project_id"] is None:
                    return redirect(f"/task/details/{task_id}")
                else:
                    return redirect(f"/project/detailes/{task['project_id']}")
            else:
                flash("invalid input")
                return redirect(f"/task/update/{task_id}")
    members=get_project_members(task['project_id'])
    if assigned_only:
        flash("You can only update the task status.")
    return render_template("update_task.html",task=task,members=members,next_page=next_page,assigned_only=assigned_only)
@task_bp.route("/create/personal",methods=['GET','POST'])
@login_required
def create_task_personal():
    user_id=session["user_id"]
    if request.method=="POST":
        title=request.form.get("title","").strip()
        description=request.form.get("description","").strip()
        priority=request.form.get("priority","").strip()
        status=request.form.get("status","").strip()
        due_date=request.form.get("due_date","")
        now=datetime.now().strftime("%Y-%m-%d %H:%M")
        if title and priority and status and len(title)<50 and len(description)<500 and status  in valid_status and priority  in valid_priority:
            task=create_task_model(title,description,priority,status,user_id,now,None,None,due_date)
            if task:
                flash("task added successfully")
                
            else:
                flash("invalid input")
        else:
            flash("invalid input")
        return redirect("/task/personal")
    return render_template("create_personal_task.html")


@task_bp.route("/search")
@login_required
def search():
    user_id=session["user_id"]
    query=request.args.get("query","").strip()
    tasks=[]
    projects=[]
    if query:
        tasks=search_tasks(user_id,query)
        projects = search_projects(query, user_id)
    return render_template("search.html",tasks=tasks,query=query,projects=projects)
@task_bp.route("/details/<int:task_id>")
@login_required
def task_details(task_id):
    user_id = session["user_id"]
    task = get_task_by_id(task_id)
    next_page = request.args.get("next", "/task/personal")
    if not task:
        flash("Task not found")
        return redirect("/")
    if user_id != task["created_by"] and user_id != task["assigned_to"]:
        flash("Access denied")
        return redirect("/")
    return render_template("task_details.html",task=task,next_page=next_page )
    
@task_bp.route("/recents")
@login_required
def recents():
    user_id=session["user_id"]
    tasks=recent_tasks(user_id,user_id)
    tasks = [dict(task) for task in tasks]
    for task in tasks:
        task["created_at"] = datetime.strptime(task["created_at"],"%Y-%m-%d %H:%M").strftime("%b %d, %Y")
    return render_template("view_task.html", tasks=tasks,title="Recent",empty_title="No Tasks Found",empty_message="Create your first task to get started.")
@task_bp.route("/personal")
@login_required
def view_personal_tasks():
    user_id=session["user_id"]
    tasks=personal_tasks(user_id)
    tasks = [dict(task) for task in tasks]
    for task in tasks:
        task["created_at"] = datetime.strptime(task["created_at"],"%Y-%m-%d %H:%M").strftime("%b %d, %Y")
    return render_template("view_task.html", tasks=tasks,title="Personal",empty_title="No Tasks Found",empty_message="Create your first task to get started.")
@task_bp.route("/assigned")
@login_required
def view_assigned_tasks():
    user_id=session["user_id"]
    tasks=assigned_tasks(user_id)
    tasks = [dict(task) for task in tasks]
    for task in tasks:
        task["created_at"] = datetime.strptime(task["created_at"],"%Y-%m-%d %H:%M").strftime("%b %d, %Y")
    return render_template("view_task.html", tasks=tasks,title="Assigned",empty_title="No Tasks Found",empty_message="You don't have any assigned task. ")
@task_bp.route("/filter")
@login_required
def filter_tasks():
    user_id=session["user_id"]
    status=request.args.get("status","").strip()
    priority=request.args.get("priority","").strip()
    tasks=get_filtered_tasks(user_id,status,priority)
    return render_template("view_task.html",tasks=tasks,title=status or priority,empty_title="No Tasks Found",empty_message="No task for this filter. Try another")