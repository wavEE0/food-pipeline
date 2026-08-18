"""
tests for loader.py - uses mocks to avoid needing a real database
"""
import pytest
from unittest.mock import patch, MagicMock, call
from loader import load_records


@pytest.fixture
def mock_conn():
    """a fake psycopg2 connection with a cursor"""
    conn = MagicMock()
    cursor = MagicMock()
    conn.cursor.return_value.__enter__ = MagicMock(return_value=cursor)
    conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
    return conn, cursor


class TestLoadRecords:
    def test_empty_records_returns_zero(self):
        result = load_records([])
        assert result == 0

    @patch('loader.db.get_connection')
    def test_executes_once_per_record(self, mock_get_conn, mock_conn):
        conn, cursor = mock_conn
        mock_get_conn.return_value = conn

        records = [
            {'barcode': '111', 'product_name': 'Apple', 'calories': 52.0,
             'protein': 0.3, 'carbs': 14.0, 'fat': 0.2, 'fibre': 2.4,
             'sodium': 0.0, 'category': 'fruits'},
            {'barcode': '222', 'product_name': 'Banana', 'calories': 89.0,
             'protein': 1.1, 'carbs': 23.0, 'fat': 0.3, 'fibre': 2.6,
             'sodium': 0.0, 'category': 'fruits'},
        ]

        result = load_records(records)
        assert result == 2
        assert cursor.execute.call_count == 2
        conn.commit.assert_called_once()

    @patch('loader.db.get_connection')
    def test_rollback_on_error(self, mock_get_conn, mock_conn):
        conn, cursor = mock_conn
        mock_get_conn.return_value = conn
        cursor.execute.side_effect = Exception("db error")

        with pytest.raises(Exception):
            load_records([{'barcode': '999', 'product_name': 'Thing',
                           'calories': None, 'protein': None, 'carbs': None,
                           'fat': None, 'fibre': None, 'sodium': None, 'category': None}])

        conn.rollback.assert_called_once()
