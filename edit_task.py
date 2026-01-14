# edit_task.py
from flask import render_template, request, redirect, url_for, flash
from tasks_routes import tasks_bp
from db import execute_query, execute_update
import psycopg2
from tasks_routes import validate_task_form


@tasks_bp.route('/<int:task_id>/edit', methods=['GET'])
def edit_task(task_id):
    query = "SELECT id, title, description FROM tasks WHERE id=%s"
    task = execute_query(query, (task_id,), fetch_one=True)

    if not task:
        flash("Task not found", "error")
        return redirect(url_for("tasks.list_tasks"))

    return render_template("tasks/edit.html", task=task)


@tasks_bp.route('/<int:task_id>/edit', methods=['POST'])
def update_task(task_id):
    errors, cleaned_data = validate_task_form(request.form)

    if errors:
        return render_template(
            "tasks/edit.html",
            task={"id": task_id, **cleaned_data},
            errors=errors
        )

    query = """
        UPDATE tasks
        SET title=%s, description=%s, updated_at=NOW()
        WHERE id=%s
    """
    execute_update(query, (
        cleaned_data['title'],
        cleaned_data['description'],
        task_id
    ))

    flash("Task updated successfully", "success")
    return redirect(url_for("tasks.list_tasks"))
