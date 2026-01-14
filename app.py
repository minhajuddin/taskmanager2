import os
from flask import Flask, Blueprint, render_template
from tasks_routes import tasks_bp

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    # Fetch recent tasks
    tasks = Task.query.order_by(Task.id.desc()).limit(5).all()

    # Dashboard statistics
    total_tasks = Task.query.count()
    completed_tasks = Task.query.filter_by(completed=True).count()
    pending_tasks = Task.query.filter_by(completed=False).count()

    # Render dashboard template
    return render_template(
        "dashboard.html",
        tasks=tasks,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks
    )
def register_routes(app):
    app.register_blueprint(main_bp)
    app.register_blueprint(tasks_bp)

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "default")

    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    # app.config.from_object(config[config_name])

    # Initialize extensions
    # db.init_app(app)

    # Register blueprints
    register_routes(app)
    return app


# tasks
# Restful Routing
# GET /tasks     => READ of all tasks
# POST /tasks    => CREATE a task
# GET /tasks/1   => READ single task
# GET /tasks/1/edit => READ single task for edit
# PUT /tasks/1      => UPDATE single task
# PATCH /tasks/1    => UPDATE single task
# DELETE /tasks/1   => DELETE single task
# CRUD  => Create Read Update Delete
# ^
# HTTP Verbs / HTTP methods

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5001)

