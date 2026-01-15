from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from db import execute_query, execute_update

edit_task_bp = Blueprint('edit_task', __name__, url_prefix='/tasks')


def validate_task_form(form_data):
    errors = {}
    title = form_data.get('title', '').strip()
    description = form_data.get('description', '').strip()

    if not title:
        errors['title'] = 'Title is required'
    elif len(title) > 255:
        errors['title'] = 'Title must be 255 characters or less'

    if description and len(description) > 255:
        errors['description'] = 'Description must be 255 characters or less'

    return errors, {'title': title, 'description': description}


@edit_task_bp.route('/<int:task_id>/edit', methods=['GET'])
def edit_task(task_id):
    query = """
        SELECT id, title, description
        FROM tasks
        WHERE id = %s
    """
    result = execute_query(query, (task_id,))
    row = result[0] if result else None

    if not row:
        flash('Task not found', 'error')
        return redirect(url_for('tasks.list_tasks'))

    task = {
        'id': row[0],
        'title': row[1],
        'description': row[2]
    }

    return render_template('tasks/edit.html', task=task)

@edit_task_bp.route('/<int:task_id>', methods=['POST', 'PUT'])
def update_task(task_id):
    
    if request.method == 'POST' and request.form.get('_method') != 'PUT':
        abort(405)

    errors, cleaned_data = validate_task_form(request.form)
    if errors:
        return render_template(
            'tasks/edit.html',
            task={'id': task_id, **cleaned_data},
            errors=errors
        ), 400

    query = """
        UPDATE tasks
        SET title = %s,
            description = %s,
            updated_at = NOW()
        WHERE id = %s
    """
    execute_update(
        query,
        (
            cleaned_data['title'],
            cleaned_data['description'],
            task_id
        )
    )

    flash('Task updated successfully!', 'success')
    return redirect(url_for('tasks.list_tasks'))
