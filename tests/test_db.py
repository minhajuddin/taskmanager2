"""Unit tests for database utilities."""
import pytest
from unittest.mock import patch, MagicMock
from contextlib import contextmanager
import psycopg2
from psycopg2.extras import DictCursor

import db


class TestGetConnection:
    """Test suite for get_connection function."""

    @patch('db.psycopg2.connect')
    def test_get_connection_success(self, mock_connect):
        """Test get_connection returns a valid connection."""
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection

        result = db.get_connection()

        assert result == mock_connection
        mock_connect.assert_called_once()

    @patch('db.psycopg2.connect')
    def test_get_connection_uses_database_url(self, mock_connect):
        """Test get_connection uses DATABASE_URL environment variable."""
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection

        db.get_connection()

        # Verify that connect was called with the DATABASE_URL
        mock_connect.assert_called_once()
        called_url = mock_connect.call_args[0][0]
        assert 'postgresql' in called_url


class TestGetCursor:
    """Test suite for get_cursor context manager."""

    @patch('db.get_connection')
    def test_get_cursor_success(self, mock_get_conn):
        """Test get_cursor yields a cursor."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        with db.get_cursor() as cursor:
            assert cursor == mock_cursor

        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('db.get_connection')
    def test_get_cursor_rollback_on_error(self, mock_get_conn):
        """Test get_cursor rolls back on database error."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        with pytest.raises(psycopg2.Error):
            with db.get_cursor() as _:
                raise psycopg2.Error('Test error')

        mock_conn.rollback.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('db.get_connection')
    def test_get_cursor_no_commit_when_false(self, mock_get_conn):
        """Test get_cursor does not commit when commit=False."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        with db.get_cursor(commit=False) as cursor:
            assert cursor == mock_cursor

        mock_conn.commit.assert_not_called()
        mock_conn.close.assert_called_once()

    @patch('db.get_connection')
    def test_get_cursor_closes_connection_on_error(self, mock_get_conn):
        """Test get_cursor closes connection even when error occurs."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        try:
            with db.get_cursor() as _:
                raise ValueError('Non-database error')
        except ValueError:
            pass

        # Connection should still be closed even for non-database errors
        mock_conn.close.assert_called_once()

    @patch('db.get_connection')
    def test_get_cursor_uses_dict_cursor(self, mock_get_conn):
        """Test get_cursor uses DictCursor factory."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        with db.get_cursor() as _:
            pass

        # Verify cursor_factory was set to DictCursor
        mock_conn.cursor.assert_called_once_with(cursor_factory=DictCursor)


class TestExecuteQuery:
    """Test suite for execute_query function."""

    @patch('db.get_cursor')
    def test_execute_query_success(self, mock_get_cursor):
        """Test execute_query returns query results."""
        mock_cursor = MagicMock()
        mock_results = [{'id': 1, 'title': 'Task 1'}, {'id': 2, 'title': 'Task 2'}]
        mock_cursor.fetchall.return_value = mock_results

        @contextmanager
        def mock_cursor_context(*args, **kwargs):
            yield mock_cursor

        mock_get_cursor.side_effect = mock_cursor_context

        result = db.execute_query("SELECT * FROM tasks")

        assert result == mock_results
        mock_cursor.execute.assert_called_once_with("SELECT * FROM tasks", ())

    @patch('db.get_cursor')
    def test_execute_query_with_params(self, mock_get_cursor):
        """Test execute_query passes parameters correctly."""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [{'id': 1}]

        @contextmanager
        def mock_cursor_context(*args, **kwargs):
            yield mock_cursor

        mock_get_cursor.side_effect = mock_cursor_context

        db.execute_query("SELECT * FROM tasks WHERE id = %s", (1,))

        mock_cursor.execute.assert_called_once_with("SELECT * FROM tasks WHERE id = %s", (1,))

    @patch('db.get_cursor')
    def test_execute_query_empty_result(self, mock_get_cursor):
        """Test execute_query handles empty results."""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []

        @contextmanager
        def mock_cursor_context(*args, **kwargs):
            yield mock_cursor

        mock_get_cursor.side_effect = mock_cursor_context

        result = db.execute_query("SELECT * FROM tasks WHERE id = %s", (999,))

        assert result == []

    @patch('db.get_cursor')
    def test_execute_query_does_not_commit_by_default(self, mock_get_cursor):
        """Test execute_query does not commit by default."""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []

        @contextmanager
        def mock_cursor_context(*args, **kwargs):
            yield mock_cursor

        mock_get_cursor.side_effect = mock_cursor_context

        db.execute_query("SELECT * FROM tasks")

        # Verify commit=False is passed to get_cursor
        mock_get_cursor.assert_called_once_with(commit=False)


class TestExecuteUpdate:
    """Test suite for execute_update function."""

    @patch('db.get_cursor')
    def test_execute_update_insert_with_returning(self, mock_get_cursor):
        """Test execute_update handles INSERT with RETURNING clause."""
        mock_cursor = MagicMock()
        mock_result = [{'id': 1, 'title': 'New Task'}]
        mock_cursor.description = True  # Indicates results are available
        mock_cursor.fetchall.return_value = mock_result

        @contextmanager
        def mock_cursor_context(*args, **kwargs):
            yield mock_cursor

        mock_get_cursor.side_effect = mock_cursor_context

        result = db.execute_update(
            "INSERT INTO tasks (title) VALUES (%s) RETURNING id, title",
            ('New Task',)
        )

        assert result == mock_result

    @patch('db.get_cursor')
    def test_execute_update_delete_without_returning(self, mock_get_cursor):
        """Test execute_update handles DELETE without RETURNING."""
        mock_cursor = MagicMock()
        mock_cursor.description = None  # No RETURNING clause
        mock_cursor.fetchall.return_value = []

        @contextmanager
        def mock_cursor_context(*args, **kwargs):
            yield mock_cursor

        mock_get_cursor.side_effect = mock_cursor_context

        result = db.execute_update(
            "DELETE FROM tasks WHERE id = %s",
            (1,)
        )

        assert result == []

    @patch('db.get_cursor')
    def test_execute_update_always_commits(self, mock_get_cursor):
        """Test execute_update always commits."""
        mock_cursor = MagicMock()
        mock_cursor.description = None

        @contextmanager
        def mock_cursor_context(*args, **kwargs):
            yield mock_cursor

        mock_get_cursor.side_effect = mock_cursor_context

        db.execute_update("DELETE FROM tasks")

        # Verify commit=True is passed to get_cursor
        mock_get_cursor.assert_called_once_with(commit=True)

    @patch('db.get_cursor')
    def test_execute_update_with_params(self, mock_get_cursor):
        """Test execute_update passes parameters correctly."""
        mock_cursor = MagicMock()
        mock_cursor.description = None

        @contextmanager
        def mock_cursor_context(*args, **kwargs):
            yield mock_cursor

        mock_get_cursor.side_effect = mock_cursor_context

        db.execute_update(
            "UPDATE tasks SET title = %s WHERE id = %s",
            ('Updated Title', 1)
        )

        mock_cursor.execute.assert_called_once_with(
            "UPDATE tasks SET title = %s WHERE id = %s",
            ('Updated Title', 1)
        )

    @patch('db.get_cursor')
    def test_execute_update_no_params(self, mock_get_cursor):
        """Test execute_update handles queries without parameters."""
        mock_cursor = MagicMock()
        mock_cursor.description = None

        @contextmanager
        def mock_cursor_context(*args, **kwargs):
            yield mock_cursor

        mock_get_cursor.side_effect = mock_cursor_context

        db.execute_update("DELETE FROM tasks")

        mock_cursor.execute.assert_called_once_with("DELETE FROM tasks", ())
