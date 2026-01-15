from flask import render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash
from db import execute_update, execute_query

def register_routes(app):

    ## GET: Show register page ##
    @app.route("/register", methods=["GET"])
    def register_get():
        return render_template("register.html")

    ## POST: Create user ##
    @app.route("/register", methods=["POST"])
    def register_post():
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            flash("Email and password are required")
            return redirect(url_for("register_get"))

        ##  Check if user already exists and i want to same in order  ##
        email = email.strip().lower()
        existing_user = execute_query(
            "SELECT id FROM users WHERE email = %s",
            (email,)
        )

        if existing_user:
            flash("User already exists")
            return redirect(url_for("register_get"))

        hashed_password = generate_password_hash(password)

        execute_update(
            """
            INSERT INTO users (email, password)
            VALUES (%s, %s)
            """,
            (email, hashed_password)
        )

        flash("Registration successful. Please login.")
        return redirect(url_for("login"))
