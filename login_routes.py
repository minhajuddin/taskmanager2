from flask import render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash
from db import execute_query


def register_routes(app):

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            email = request.form.get("email")
            password = request.form.get("password")

            if not email or not password:
                flash("Email and password are required")
                return redirect(url_for("login"))

            users = execute_query(
                "SELECT * FROM users WHERE email = %s",
                (email,)
            )

            if users:
                user = users[0]

                if check_password_hash(user["password"], password):
                    session["user_id"] = user["id"]
                    session["user_email"] = user["email"]

                    flash("Login successful")
                    return redirect(url_for("index"))

            flash("Invalid email or password")

        return render_template("login.html")
