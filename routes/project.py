from flask import Blueprint,request,redirect,render_template,flash,session
from datetime import datetime
from utils.decorators import login_required
from  models.project import create_project as create_project_model,get_project_by_id,add_member as add_member_model,get_project_members,delete_member,delete_project,edit_project,is_member,get_users_project,associated_projects 
from models.task import get_project_task
project_bp=Blueprint("project_bp",__name__,url_prefix="/project")
now=datetime.now().strftime("%Y-%m-%d %H:%M")
@project_bp.route("/create",methods=["GET","POST"])
@login_required
def create_project():
    user_id=session["user_id"]
    if request.method=="POST":
        name=request.form.get("name","").strip()
        description=request.form.get("description","").strip()
        if name and description and len(name)<50 and len(description)<500:
            project_id=create_project_model(name,description,user_id,now)
            if project_id:
                flash ("Project Created Successfully")
                return redirect("/project/personal")
        else:
            flash("Invalid input")
    return render_template("create_project.html")

@project_bp.route("/detailes/<int:project_id>")
@login_required
def project_details(project_id):
    user_id=session["user_id"]
    status=request.args.get("status","").strip()
    priority=request.args.get("priority","").strip()
    project=get_project_by_id(project_id)
    if not project:
        flash("project not found")
        return redirect("/")
    if project["owner_id"]!=session["user_id"] and not is_member(project_id,session['user_id']):
        flash("access denied")
        return redirect("/")
    tasks=get_project_task(project_id,status,priority)
    members=get_project_members(project_id)
    return render_template("project_detailes.html",project=project,tasks=tasks,members=members,user_id=user_id)

@project_bp.route("/add/member/<int:project_id>",methods=["GET","POST"])
@login_required
def add_member(project_id):

    project=get_project_by_id(project_id)
    if not project or project["owner_id"]!=session["user_id"]:
        flash("Action Not Allowed")
        return redirect(f"/project/detailes/{project_id}")
    if request.method=="POST":
        member_usename=request.form.get("member_username")
        if member_usename:
           
            added=add_member_model(project["owner_id"],project_id,member_usename,now)
            if added:
                flash("member added successfully")
                return  redirect(f"/project/detailes/{project_id}")
            else:
                flash("Invalid Attempt")
                
        else:
            flash("username required")
    return  redirect(f"/project/detailes/{project_id}")
    
@project_bp.route("/remove/member/<int:project_id>/<int:member_id>",methods=["GET","POST"])
@login_required
def remove_member(project_id,member_id):

    project=get_project_by_id(project_id)
    if not project or project["owner_id"]!=session["user_id"]:
        flash("Action Not Allowed")
        return redirect(f"/project/detailes/{project_id}")
    removed=delete_member(project["owner_id"],project_id,member_id)
    if removed:
        flash("member removed successfully")
        return  redirect(f"/project/detailes/{project_id}")
    else:
        flash("Invalid Attempt")
                
    return  redirect(f"/project/detailes/{project_id}")
@project_bp.route("/delete/<int:project_id>")
@login_required
def delete_prj(project_id):
        user_id=session["user_id"]
        project=get_project_by_id(project_id)
        if not project or user_id!=project['owner_id']:
            flash("action not allowed")
            return  redirect(f"/project/detailes/{project_id}")
        deleted=delete_project(user_id,project_id)
        if deleted:
            flash("project deleted")
            return redirect("/project/personal")
        else:
            flash("action not allowed")
            return  redirect(f"/project/detailes/{project_id}")
@project_bp.route("/edit/<int:project_id>",methods=["GET","POST"])
@login_required
def edit_prj(project_id):
    user_id=session["user_id"]
    project=get_project_by_id(project_id)
    if not project or user_id!=project["owner_id"]:
        flash("action not allowed")
        return redirect(f"/project/detailes/{project_id}")
    if request.method=="POST":
        name=request.form.get("name","").strip()
        description=request.form.get("description","").strip()
        if name and description and len(name)<50 and len(description)<500:
            edited=edit_project(user_id,project_id,name,description)
            if edited:
                flash ("Project edited Successfully")
                return redirect(f"/project/detailes/{project_id}")
        else:
            flash("Invalid input")
            return redirect(f"/project/edit/{project_id}")
    return render_template("edit_project.html",project=project)
@project_bp.route("/personal")
@login_required
def view_myproject():
    user_id=session["user_id"]
    projects=get_users_project(user_id)
    projects = [dict(project) for project in projects]
    for project in projects:
        project["created_at"] = datetime.strptime(project["created_at"], "%Y-%m-%d %H:%M").strftime("%b %d, %Y")
    return render_template("view_project.html",projects=projects,name="My Projects",empty_title="No Projects Found",empty_message="Create your first project to get started.")
@project_bp.route("/associate")
@login_required
def view_associateproject():
    user_id=session["user_id"]
    projects=associated_projects(user_id)
    projects = [dict(project) for project in projects]
    for project in projects:
        project["created_at"] = datetime.strptime(project["created_at"], "%Y-%m-%d %H:%M").strftime("%b %d, %Y")
    return render_template("view_project.html",projects=projects,name="Associate Projects", empty_title="No Associated Projects",empty_message="Ask a project owner to add you as a member.")