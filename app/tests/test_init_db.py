import unittest
from unittest.mock import patch, MagicMock
import init_db


class TestInitTables(unittest.TestCase):
    @patch("init_db.get_connection")
    @patch("init_db.USER_TABLE", "USER")
    @patch("init_db.PVZ_TABLE", "PVZ")
    @patch("init_db.RECEPTION_TABLE", "RECEPTION")
    @patch("init_db.PRODUCT_TABLE", "PRODUCT")
    def test_init_tables(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value.__enter__.return_value = mock_conn

        init_db.init_tables()

        mock_cursor.execute.assert_any_call("USER")
        mock_cursor.execute.assert_any_call("PVZ")
        mock_cursor.execute.assert_any_call("RECEPTION")
        mock_cursor.execute.assert_any_call("PRODUCT")
        mock_conn.commit.assert_called_once()
