import unittest
from unittest.mock import patch, MagicMock
import db


class TestDB(unittest.TestCase):
    @patch("psycopg2.connect")
    def test_get_connection(self, mock_connect):
        db.get_connection()
        mock_connect.assert_called_once()

    @patch("psycopg2.connect")
    def test_create_tables_success(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        db.create_tables()

        self.assertEqual(mock_cursor.execute.call_count, 4)
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch("psycopg2.connect", side_effect=Exception("DB Error"))
    def test_create_tables_exception(self, mock_connect):
        db.create_tables()
