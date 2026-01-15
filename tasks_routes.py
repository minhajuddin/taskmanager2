from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import execute_query, execute_update
import psycopg2

tasks_bp = Blueprint('tasks', __name__, url_prefix='/tasks')


def validate_task_form(form_data):
    """
    Validate task form data.

    Returns:
        (errors_dict, cleaned_data_dict) tuple
    """
    errors = {}
    title = form_data.get('title', '').strip()
    description = form_data.get('description', '').strip()

    # Validate title
    if not title:
        errors['title'] = 'Title is required'
    elif len(title) > 255:
        errors['title'] = 'Title must be 255 characters or less'

    # Validate description
    if description and len(description) > 255:
        errors['description'] = 'Description must be 255 characters or less'

    return errors, {'title': title, 'description': description}


@tasks_bp.route('/new', methods=['GET'])
def new_task():
    """Display task creation form."""
    return render_template('tasks/new.html')


@tasks_bp.route('/', methods=['POST'])
def create_task():
    """Handle task creation."""
    # Validate form data
    errors, cleaned_data = validate_task_form(request.form)

    if errors:
        for field, error_msg in errors.items():
            flash(error_msg, 'error')
        return render_template(
            'tasks/new.html',
            errors=errors,
            form_data=request.form
        ), 400

    try:
        # Insert task into database
        query = """
            INSERT INTO tasks (title, description)
            VALUES (%s, %s)
            RETURNING id, title, description, completed_at, created_at, updated_at
        """
        params = (cleaned_data['title'], cleaned_data['description'] or None)
        result = execute_update(query, params)

        if result:
            flash('Task created successfully!', 'success')
            return redirect(url_for('tasks.list_tasks'))
        else:
            flash('Failed to create task', 'error')
            return render_template('tasks/new.html', errors={'db': 'Failed to create task'}), 500

    except psycopg2.Error as db_error:
        flash('Database error: Unable to create task', 'error')
        return render_template('tasks/new.html', errors={'db': str(db_error)}), 500


@tasks_bp.route('/', methods=['GET'])
def list_tasks():
    """Display all tasks."""
    try:
        query = """
            SELECT id, title, description, completed_at, created_at, updated_at
            FROM tasks
            ORDER BY created_at DESC
        """
        tasks = execute_query(query)
        return render_template('tasks/index.html', tasks=tasks)

    except psycopg2.Error:
        flash('Database error: Unable to load tasks', 'error')
        return render_template('tasks/index.html', tasks=[]), 500

@tasks_bp.route('/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    try:
        query = "DELETE FROM tasks WHERE id = %s"
        rows_affected = execute_update(query, (task_id,))

        if rows_affected == 0:
            return {"error": "Task not found"}, 404

        return {"message": "Task deleted successfully"}, 200

    except Exception as e:
        return {"error": "Database error while deleting task"}, 500
