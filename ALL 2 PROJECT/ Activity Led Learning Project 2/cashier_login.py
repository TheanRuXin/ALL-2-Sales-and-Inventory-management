# --- cashier_login.py ---

import customtkinter as ctk
from tkinter import messagebox, StringVar
from PIL import Image
import sqlite3
import bcrypt

from Forget_password import ForgetPasswordPage
from cashier_dashboard import CashierDashboard  # ✅ Import added

class CashierLogin(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.width, self.height = 1574, 800
        self.allowed_roles = ["Cashier"]

        background_image = ctk.CTkImage(Image.open(r"cashier login.png"), size=(self.width, self.height))
        background_label = ctk.CTkLabel(self, image=background_image, text="")
        background_label.place(x=0, y=0)

        self.initialize_db()
        self.setup_ui()

    def initialize_db(self):
        conn = sqlite3.connect("Trackwise.db")
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            role TEXT NOT NULL,
            email TEXT, phone TEXT, dob TEXT,
            password TEXT NOT NULL, photo_path TEXT)''')
        conn.commit()
        conn.close()

    def login(self):
        username = self.username.get()
        password = self.password.get()

        conn = sqlite3.connect("Trackwise.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, password, role FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user:
            user_id, stored_hashed_password, role = user

            if bcrypt.checkpw(password.encode(), stored_hashed_password):

                if role == "Cashier":
                    messagebox.showinfo("Login Successful", f"Welcome {role.capitalize()}!")

                    self.controller.logged_in_user_id = user_id

                    # ✅ Dynamically create and register CashierDashboard
                    dashboard = CashierDashboard(parent=self.controller, controller=self.controller)
                    dashboard.place(x=0, y=0, relwidth=1, relheight=1)
                    self.controller.frames["CashierDashboard"] = dashboard
                    self.controller.show_frame("CashierDashboard")

                else:
                    messagebox.showerror("Access Denied", f"You cannot login here as {role}!")
                    self.controller.show_frame("MainPage")
            else:
                messagebox.showerror("Error", "Invalid Username or Password")
        else:
            messagebox.showerror("Error", "Invalid Username or Password")

    def forget_password(self):
        ForgetPasswordPage(parent=self, controller=self.controller)

    def new_account(self):
        messagebox.showinfo("Help", "Please contact your Manager")

    def back(self):
        self.controller.show_frame("MainPage")

    def setup_ui(self):
        username_label = ctk.CTkLabel(self, text="Username:", font=("Inter", 22), bg_color="#D9D9D9", text_color="Black")
        username_label.place(x=150 / 1920 * self.width, y=380 / 974 * self.height)

        self.username = StringVar()
        username_entry = ctk.CTkEntry(self, width=395 / 1536 * self.width, height=45 / 864 * self.height,
                                      bg_color="#D9D9D9", textvariable=self.username)
        username_entry.place(x=148 / 1920 * self.width, y=418 / 974 * self.height)

        password_label = ctk.CTkLabel(self, text="Password:", font=("Inter", 22), bg_color="#D9D9D9", text_color="black")
        password_label.place(x=152 / 1920 * self.width, y=490 / 974 * self.height)

        self.password = StringVar()
        password_entry = ctk.CTkEntry(self, width=395 / 1536 * self.width, height=45 / 864 * self.height,
                                      bg_color="#D9D9D9", textvariable=self.password, show="*")
        password_entry.place(x=148 / 1920 * self.width, y=528 / 974 * self.height)

        forgot_label = ctk.CTkLabel(self, text="Forgot Password?", font=("Inter", 15), bg_color="#D9D9D9", text_color="Blue")
        forgot_label.place(x=451 / 1920 * self.width, y=580 / 974 * self.height)
        forgot_label.bind("<Button-1>", lambda e: self.forget_password())

        login_button = ctk.CTkButton(self, text="Login", bg_color="#D9D9D9", fg_color="Blue", text_color="white",
                                     border_color="#1572D3", width=160, height=44, font=("Inter", 18), command=self.login)
        login_button.place(x=273 / 1920 * self.width, y=645 / 974 * self.height)

        account_label = ctk.CTkLabel(self, text="Don't have an account?", font=("Inter", 15),
                                     bg_color="#D9D9D9", fg_color="#D9D9D9", text_color="black")
        account_label.place(x=285 / 1920 * self.width, y=715 / 974 * self.height)

        new_label = ctk.CTkLabel(self, text="Create a New Account", font=("Arial", 17), bg_color="#D9D9D9", text_color="#5885F0")
        new_label.place(x=266 / 1920 * self.width, y=740 / 974 * self.height)
        new_label.bind("<Button-1>", lambda e: self.new_account())

        back_button = ctk.CTkButton(self, text="Back", bg_color="#D9D9D9", fg_color="Blue", text_color="white",
                                    border_color="#1572D3", width=129, height=35, font=("Iter", 14), command=self.back)
        back_button.place(x=866 / 1920 * self.width, y=800 / 974 * self.height)

        admin_button = ctk.CTkButton(self, text="Trackwise", bg_color="#D9D9D9", fg_color="Blue",
                                     text_color="white", border_color="#1572D3", width=129, height=35, font=("Inter", 14))
        admin_button.place(x=1623 / 1920 * self.width, y=800 / 974 * self.height)

        self.controller.bind("<Return>", lambda event: self.login())
