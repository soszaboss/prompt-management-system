# tests/test_db.py
from psycopg import OperationalError
import pytest
from app.db import get_db, close_db

def test_get_close_db(app):
    with app.app_context():
        db = get_db()
        assert db is get_db()
        print("Connection before closing:", db.closed)
        close_db()  # Explicitly close the connection
        print("Connection after closing:", db.closed)

    # Attempt to use the connection outside the app context should raise an error
    with pytest.raises(OperationalError) as e:
        db.execute('SELECT 1')

    assert 'closed' in str(e.value).lower()
