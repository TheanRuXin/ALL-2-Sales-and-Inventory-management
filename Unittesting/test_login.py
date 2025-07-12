import unittest
from unittest.mock import MagicMock, patch
import bcrypt
import sqlite3

from manager_login import LoginPage
import customtkinter as ctk

class TestLoginPage(unittest.TestCase):
    def setUp(self):
        self.root = ctk.CTk()
        self.mock_controller = MagicMock()
        self.login_page = LoginPage(parent=self.root, controller=self.mock_controller)

    @patch('sqlite3.connect')
    @patch('tkinter.messagebox.showinfo')
    @patch('tkinter.messagebox.showerror')
    def test_login_success_manager(self, mock_error, mock_info, mock_connect):
        hashed_pw = bcrypt.hashpw("correct_password".encode(), bcrypt.gensalt())

        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (1, hashed_pw, "Manager")
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        self.login_page.username.set("trackwise")
        self.login_page.password.set("correct_password")
        self.login_page.login()

        mock_info.assert_called_with("Login Successful", "Welcome Manager!")
        self.mock_controller.show_frame.assert_called_with("ManagerDashboard")

    @patch('sqlite3.connect')
    @patch('tkinter.messagebox.showerror')
    def test_login_wrong_password(self, mock_error, mock_connect):
        hashed_pw = bcrypt.hashpw("actual_pw".encode(), bcrypt.gensalt())

        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (1, hashed_pw, "Manager")
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        self.login_page.username.set("trackwise")
        self.login_page.password.set("wrong_password")
        self.login_page.login()

        mock_error.assert_called_with("Error", "Invalid Username or Password")

    @patch('sqlite3.connect')
    @patch('tkinter.messagebox.showerror')
    def test_login_user_not_found(self, mock_error, mock_connect):
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        self.login_page.username.set("not_exist")
        self.login_page.password.set("any")
        self.login_page.login()

        mock_error.assert_called_with("Error", "Invalid Username or Password")

    def tearDown(self):
        self.root.destroy()


if __name__ == '__main__':
    unittest.main()
