"""
Database connection and utility functions
Handles MySQL connection pooling and query execution
"""

import mysql.connector
from mysql.connector import Error, pooling
from config import Config
from contextlib import contextmanager

# Create connection pool for better performance
connection_pool = None


def init_connection_pool():
    """Initialize MySQL connection pool"""
    global connection_pool
    try:
        connection_pool = pooling.MySQLConnectionPool(
            pool_name="exam_pool",
            pool_size=5,
            pool_reset_session=True,
            **Config.DB_CONFIG
        )
        print("✓ Database connection pool created successfully")
        return True
    except Error as e:
        print(f"✗ Error creating connection pool: {e}")
        return False


@contextmanager
def get_db_connection():
    """
    Context manager for database connections
    Automatically handles connection closing
    """
    connection = None
    try:
        if connection_pool is None:
            init_connection_pool()
        connection = connection_pool.get_connection()
        yield connection
    except Error as e:
        print(f"Database connection error: {e}")
        if connection:
            connection.rollback()
        raise
    finally:
        if connection and connection.is_connected():
            connection.close()


@contextmanager
def get_db_cursor(dictionary=True, buffered=True):
    """
    Context manager for database cursor
    Automatically handles connection and cursor closing
    
    Args:
        dictionary (bool): Return results as dictionaries
        buffered (bool): Use buffered cursor
    """
    connection = None
    cursor = None
    try:
        with get_db_connection() as connection:
            cursor = connection.cursor(dictionary=dictionary, buffered=buffered)
            yield cursor, connection
            connection.commit()
    except Error as e:
        if connection:
            connection.rollback()
        print(f"Database cursor error: {e}")
        raise
    finally:
        if cursor:
            cursor.close()


def execute_query(query, params=None, fetch=True):
    """
    Execute a SELECT query and return results
    
    Args:
        query (str): SQL query
        params (tuple): Query parameters
        fetch (str): 'one', 'all', or False for no fetch
    
    Returns:
        Query results or None
    """
    try:
        with get_db_cursor() as (cursor, connection):
            cursor.execute(query, params or ())
            
            if fetch == 'one':
                return cursor.fetchone()
            elif fetch == 'all':
                return cursor.fetchall()
            else:
                connection.commit()
                return cursor.lastrowid
    except Error as e:
        print(f"Query execution error: {e}")
        return None


def execute_insert(query, params=None):
    """
    Execute an INSERT query and return last inserted ID
    
    Args:
        query (str): SQL INSERT query
        params (tuple): Query parameters
    
    Returns:
        int: Last inserted row ID
    """
    try:
        with get_db_cursor() as (cursor, connection):
            cursor.execute(query, params or ())
            connection.commit()
            return cursor.lastrowid
    except Error as e:
        print(f"Insert error: {e}")
        return None


def execute_update(query, params=None):
    """
    Execute an UPDATE or DELETE query
    
    Args:
        query (str): SQL UPDATE/DELETE query
        params (tuple): Query parameters
    
    Returns:
        int: Number of affected rows
    """
    try:
        with get_db_cursor() as (cursor, connection):
            cursor.execute(query, params or ())
            connection.commit()
            return cursor.rowcount
    except Error as e:
        print(f"Update error: {e}")
        return 0


def execute_many(query, data):
    """
    Execute multiple INSERT queries efficiently
    
    Args:
        query (str): SQL INSERT query
        data (list): List of tuples containing values
    
    Returns:
        int: Number of inserted rows
    """
    try:
        with get_db_cursor() as (cursor, connection):
            cursor.executemany(query, data)
            connection.commit()
            return cursor.rowcount
    except Error as e:
        print(f"Batch insert error: {e}")
        return 0


def test_connection():
    """Test database connection"""
    try:
        with get_db_cursor() as (cursor, connection):
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if result:
                print("✓ Database connection test successful")
                return True
    except Error as e:
        print(f"✗ Database connection test failed: {e}")
        return False


# Initialize connection pool on module import
init_connection_pool()