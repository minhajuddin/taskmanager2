from flask import render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash
from db import execute_update


def register_routes(app):

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            email = request.form.get("email")
            password = request.form.get("password")

            if not email or not password:
                flash("Email and password are required")
                return redirect(url_for("register"))

            hashed_password = generate_password_hash(password)

            try:
                execute_update(
                    """
                    INSERT INTO users (email, password)
                    VALUES (%s, %s)
                    """,
                    (email, hashed_password)
                )

                flash("Registration successful. Please login.")
                return redirect(url_for("login"))

            except Exception:
                flash("User already exists")

        return render_template("register.html")
