from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash
from db import execute_query

login_bp = Blueprint("login", __name__)

## GET: Show login page ##
@login_bp.route("/login", methods=["GET"])
def login_get():
    return render_template("login.html")

## POST: validate login form input ##
@login_bp.route("/login", methods=["POST"])
def login_post():
    email = request.form.get("email")
    password = request.form.get("password")

    if not email or not password:
        flash("Email and password are required")
        return redirect(url_for("login.login_get"))
    
    ## Normalize email ##    
    email = email.strip().lower()

    users = execute_query(
        "SELECT id, email, hashed_password FROM users WHERE email = %s",
        (email,)
    )

    ## it tells about if the user was invalid email or password stay in login page ##
    if not users:
        flash("Invalid email or password")
        return redirect(url_for("login.login_get"))

    user = users[0]

    if not check_password_hash(user["hashed_password"], password):
        flash("Invalid email or password")
        return redirect(url_for("login.login_get"))

    session["user_id"] = user["id"]
    session["user_email"] = user["email"]

    flash("Login successful")
    return redirect(url_for("main.index"))

