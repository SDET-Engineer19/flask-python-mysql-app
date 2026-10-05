import pytest
import os
from playwright.sync_api import sync_playwright
import mysql.connector

FLASK_URL = os.getenv('FLASK_URL', 'http://localhost:5000')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', 3306))
DB_USER = os.getenv('DB_USER', 'emp_app')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', 'employee_db')

# Handle missing/empty JOB_COMPLETION_INDEX
JOB_COMPLETION_INDEX = os.getenv('JOB_COMPLETION_INDEX', '0') or '0'
try:
    SHARD_NUMBER = int(JOB_COMPLETION_INDEX) + 1
except (ValueError, TypeError):
    SHARD_NUMBER = 1

TOTAL_SHARDS = 4

@pytest.fixture(scope="session", autouse=True)
def log_test_config():
    print(f"\n{'='*70}")
    print(f"🚀 TEST CONFIGURATION (HEADLESS MODE)")
    print(f"{'='*70}")
    print(f"🌐 Flask URL:     {FLASK_URL}")
    print(f"💾 DB Host:       {DB_HOST}:{DB_PORT}")
    print(f"📦 DB Name:       {DB_NAME}")
    print(f"👤 DB User:       {DB_USER}")
    print(f"🎭 Browser Mode:  HEADLESS (no GUI)")
    print(f"📊 SHARD:         {SHARD_NUMBER}/{TOTAL_SHARDS}")
    print(f"{'='*70}\n")

@pytest.fixture
def browser():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-gpu",
            ]
        )
        yield browser
        browser.close()

@pytest.fixture
def page(browser):
    context = browser.new_context(viewport={"width": 1920, "height": 1080}, ignore_https_errors=True)
    page = context.new_page()
    page.on("console", lambda msg: print(f"🔵 Browser console: {msg.text}"))
    page.on("pageerror", lambda exc: print(f"🔴 Page error: {exc}"))
    yield page
    page.close()
    context.close()

@pytest.fixture(scope="session")
def mysql_client():
    connection = None
    try:
        connection = mysql.connector.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, database=DB_NAME, autocommit=True)
        print(f"\n✅ MySQL Connected: {DB_HOST}:{DB_PORT}/{DB_NAME}")
        yield connection
    except mysql.connector.Error as err:
        print(f"\n❌ MySQL Connection Error: {err}")
        yield None
    finally:
        if connection and connection.is_connected():
            connection.close()

@pytest.fixture
def db_cleanup(mysql_client):
    yield
    if mysql_client:
        try:
            cursor = mysql_client.cursor()
            cursor.execute("DELETE FROM employees WHERE employee_id LIKE 'TEST_%'")
            mysql_client.commit()
            cursor.close()
        except Exception as e:
            print(f"⚠️  Cleanup error: {e}")

@pytest.fixture(scope="function", autouse=True)
def test_logger(request):
    print(f"\n▶️  Starting: {request.node.name}")
    yield
    print(f"✅ Completed: {request.node.name}")
