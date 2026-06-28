from models.user import create_user,get_user_by_username
from flask import Blueprint,request,redirect,render_template,flash,session
from datetime import datetime
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
auth_bp=Blueprint("auth_bp",__name__)
@auth_bp.route("/register",methods=["GET","POST"])
def register():
    if "user_id" in session:
        return redirect("/")
    if request.method=="POST":
        username=request.form.get("username","").strip()
        email=request.form.get("email","").strip()
        password=request.form.get("password","").strip()
        hash_password=generate_password_hash(password)
        now=datetime.now().strftime("%Y-%m-%d %H:%M")
        if username and email and password and len(username)<50:
            result=create_user(username,email,hash_password,now)
            if result:
                flash("Registration Successful")
                return redirect("/login")
            else:
                flash("User Already Exists")
        else:
            flash("Invalid Input")
    return render_template("register.html")
@auth_bp.route("/login",methods=["GET","POST"])
def login():
    if "user_id" in session:
        return redirect("/")
    if request.method=="POST":
        username=request.form.get("username","").strip()
        password=request.form.get("password","").strip()
        user=None
        if username and password and len(username)<50:
            user=get_user_by_username(username)
        if user:
            stored_password=user["password"]
            if check_password_hash(stored_password,password):
                session["user_id"]=user["id"]
                session["username"]=user["username"]
                flash("Login Successfull")
                return redirect("/")
            else:
                flash("Invalid Credential")
        else:
            flash("Invalid Credential")
    return render_template("login.html")
@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/login")
