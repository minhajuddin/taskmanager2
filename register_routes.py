from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash
from db import execute_query, execute_update

register_bp = Blueprint("register", __name__)

## GET: Show register page ##
@register_bp.route("/register", methods=["GET"])
def register_get():
    return render_template("register.html")

## POST: Create user ##
@register_bp.route("/register", methods=["POST"])
def register_post():
    email = request.form.get("email")
    password = request.form.get("password")

    if not email or not password:
        flash("Email and password are required")
        return redirect(url_for("register.register_get"))

    ## Normalize email ##
    email = email.strip().lower()

    ## Check if user already exists ##
    existing_user = execute_query(
        "SELECT id FROM users WHERE email = %s",
        (email,)
    )

    if existing_user:
        flash("User already exists")
        return redirect(url_for("register.register_get"))

    ## HASH PASSWORD CORRECTLY ##
    hashed_password = generate_password_hash(password)

    ## INSERT USING CORRECT COLUMN NAME ##
    execute_update(
        """
        INSERT INTO users (email, hashed_password)
        VALUES (%s, %s)
        """,
        (email, hashed_password)
    )

    flash("Registration successful. Please login.")
    return redirect(url_for("login.login_get"))
