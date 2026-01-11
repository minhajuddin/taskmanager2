import os
import psycopg2
from psycopg2.extras import DictCursor
from contextlib import contextmanager

# TODO: Don't hardcode credentials
DATABASE_URL = os.environ.get(
    'DATABASE_URL',
    'postgresql://taskmanager:taskmanager@localhost/taskmanager_dev'
)


def get_connection():
    """Create and return a database connection."""
    return psycopg2.connect(DATABASE_URL)


@contextmanager
def get_cursor(commit=True):
    """
    Context manager for database cursor.
    Handles connection, cursor creation, and cleanup.
    Automatically commits or rolls back based on errors.
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=DictCursor)
        yield cursor
        if commit:
            conn.commit()
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()


def execute_query(query, params=None, commit=False):
    """
    Execute a SELECT query and return results.

    Args:
        query: SQL query string
        params: Query parameters (tuple or list)
        commit: Whether to commit (usually False for SELECT)

    Returns:
        List of result rows as dictionaries
    """
    with get_cursor(commit=commit) as cursor:
        cursor.execute(query, params or ())
        return cursor.fetchall()


def execute_update(query, params=None):
    """
    Execute an INSERT, UPDATE, or DELETE query.
    Automatically commits the transaction.

    Args:
        query: SQL query string
        params: Query parameters (tuple or list)

    Returns:
        List of returned rows (from RETURNING clause) or empty list
    """
    with get_cursor(commit=True) as cursor:
        cursor.execute(query, params or ())
        if cursor.description:
            return cursor.fetchall()
        return []
