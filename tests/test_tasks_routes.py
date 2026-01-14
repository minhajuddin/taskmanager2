"""Unit tests for tasks routes."""
from unittest.mock import patch
import psycopg2
from datetime import datetime


class TestTaskRoutes:
    """Test suite for task-related Flask routes."""

    def test_new_task_get(self, client):
        """Test GET /tasks/new returns the task creation form."""
        response = client.get('/tasks/new')

        assert response.status_code == 200
        assert b'new.html' in response.data or b'task' in response.data.lower()

    @patch('tasks_routes.execute_update')
    @patch('tasks_routes.execute_query')
    def test_list_tasks_success(self, mock_execute_query, mock_execute_update, client):
        """Test GET /tasks returns list of tasks successfully."""
        mock_tasks = [
            {'id': 1, 'title': 'Task 1', 'description': 'Desc 1', 'completed_at': None, 'created_at': datetime(2024, 1, 1), 'updated_at': datetime(2024, 1, 1)},
            {'id': 2, 'title': 'Task 2', 'description': 'Desc 2', 'completed_at': None, 'created_at': datetime(2024, 1, 2), 'updated_at': datetime(2024, 1, 2)},
        ]
        mock_execute_query.return_value = mock_tasks

        response = client.get('/tasks/', follow_redirects=True)

        assert response.status_code == 200
        assert b'Task 1' in response.data
        assert b'Task 2' in response.data
        mock_execute_query.assert_called_once()

    @patch('tasks_routes.execute_query')
    def test_list_tasks_empty(self, mock_execute_query, client):
        """Test GET /tasks returns empty list when no tasks exist."""
        mock_execute_query.return_value = []

        response = client.get('/tasks/', follow_redirects=True)

        assert response.status_code == 200
        mock_execute_query.assert_called_once()

    @patch('tasks_routes.execute_query')
    def test_list_tasks_database_error(self, mock_execute_query, client):
        """Test GET /tasks handles database errors gracefully."""
        mock_execute_query.side_effect = psycopg2.Error('Database connection failed')

        response = client.get('/tasks/', follow_redirects=True)

        assert response.status_code == 500

    @patch('tasks_routes.execute_update')
    def test_create_task_success(self, mock_execute_update, client):
        """Test POST /tasks creates a task successfully."""
        mock_result = [{'id': 1, 'title': 'New Task', 'description': 'A task', 'completed_at': None, 'created_at': datetime(2024, 1, 1), 'updated_at': datetime(2024, 1, 1)}]
        mock_execute_update.return_value = mock_result

        response = client.post('/tasks/', data={
            'title': 'New Task',
            'description': 'A task'
        })

        assert response.status_code == 302  # Redirect after successful creation
        mock_execute_update.assert_called_once()

    def test_create_task_missing_title(self, client):
        """Test POST /tasks fails when title is missing."""
        response = client.post('/tasks/', data={
            'title': '',
            'description': 'A task'
        })

        assert response.status_code == 400
        assert b'Title is required' in response.data

    def test_create_task_title_too_long(self, client):
        """Test POST /tasks fails when title exceeds 255 characters."""
        long_title = 'a' * 256
        response = client.post('/tasks/', data={
            'title': long_title,
            'description': 'A task'
        })

        assert response.status_code == 400
        assert b'Title must be 255 characters or less' in response.data

    def test_create_task_description_too_long(self, client):
        """Test POST /tasks fails when description exceeds 255 characters."""
        long_description = 'b' * 256
        response = client.post('/tasks/', data={
            'title': 'Valid Title',
            'description': long_description
        })

        assert response.status_code == 400
        assert b'Description must be 255 characters or less' in response.data

    @patch('tasks_routes.execute_update')
    def test_create_task_database_error(self, mock_execute_update, client):
        """Test POST /tasks handles database errors gracefully."""
        mock_execute_update.side_effect = psycopg2.Error('Database error')

        response = client.post('/tasks/', data={
            'title': 'New Task',
            'description': 'A task'
        })

        assert response.status_code == 500

    @patch('tasks_routes.execute_update')
    def test_create_task_without_description(self, mock_execute_update, client):
        """Test POST /tasks creates task with only title (description is optional)."""
        mock_result = [{'id': 1, 'title': 'New Task', 'description': None, 'completed_at': None, 'created_at': datetime(2024, 1, 1), 'updated_at': datetime(2024, 1, 1)}]
        mock_execute_update.return_value = mock_result

        response = client.post('/tasks/', data={
            'title': 'New Task',
            'description': ''
        })

        assert response.status_code == 302
        mock_execute_update.assert_called_once()

    def test_home_page(self, client):
        """Test GET / returns home page."""
        response = client.get('/')

        assert response.status_code == 200
        assert b'home' in response.data.lower() or b'html' in response.data.lower()
