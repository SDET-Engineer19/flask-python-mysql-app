"""MySQL access layer for the employee form app."""
import os
from contextlib import contextmanager

import mysql.connector
from mysql.connector import pooling

_pool = None


def get_pool():
    """Create the connection pool lazily, from environment variables."""
    global _pool
    if _pool is None:
        _pool = pooling.MySQLConnectionPool(
            pool_name="emp_pool",
            pool_size=5,
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "3306")),
            user=os.getenv("DB_USER", "emp_app"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "employee_db"),
        )
    return _pool


@contextmanager
def get_connection():
    conn = get_pool().get_connection()
    try:
        yield conn
    finally:
        conn.close()  # returns the connection to the pool


class DuplicateEmployeeError(Exception):
    """Raised when the employee ID already exists."""


def insert_employee(emp: dict) -> None:
    sql = (
        "INSERT INTO employees (employee_id, employee_name, salary, designation, city) "
        "VALUES (%s, %s, %s, %s, %s)"
    )
    values = (
        emp["employee_id"],
        emp["employee_name"],
        emp["salary"],
        emp["designation"],
        emp["city"],
    )
    with get_connection() as conn:
        cur = conn.cursor()
        try:
            cur.execute(sql, values)  # parameterised: safe from SQL injection
            conn.commit()
        except mysql.connector.IntegrityError as exc:
            conn.rollback()
            if exc.errno == 1062:  # ER_DUP_ENTRY
                raise DuplicateEmployeeError(emp["employee_id"]) from exc
            raise
        finally:
            cur.close()


def list_employees(limit: int = 50) -> list[dict]:
    sql = (
        "SELECT employee_id, employee_name, salary, designation, city, created_at "
        "FROM employees ORDER BY created_at DESC LIMIT %s"
    )
    with get_connection() as conn:
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute(sql, (limit,))
            return cur.fetchall()
        finally:
            cur.close()
