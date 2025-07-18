import customtkinter as ctk
from tkinter import messagebox, StringVar
from PIL import Image
import sqlite3
import bcrypt
from Forget_password import ForgetPasswordPage

class LoginPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.width, self.height = 1574, 800
        self.allowed_roles = ["Manager","Admin","Cashier"]

        background_image = ctk.CTkImage(Image.open(r"C:\Users\User\Documents\Ruxin file\ALL 2\manager login.png"), size=(self.width, self.height))
        background_label = ctk.CTkLabel(self, image=background_image, text="")
        background_label.place(x=0, y=0)

        self.initialize_db()
        self.setup_ui()
        self.enter_key_binding_id = None

    def bind_enter_key(self):
        if self.enter_key_binding_id is None:
            self.enter_key_binding_id = self.controller.bind("<Return>", lambda event: self.login())

    def unbind_enter_key(self):
        if self.enter_key_binding_id is not None:
            self.controller.unbind("<Return>", self.enter_key_binding_id)
            self.enter_key_binding_id = None

    def initialize_db(self):
        conn = sqlite3.connect("Trackwise.db")
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            role TEXT NOT NULL,
            email TEXT, phone TEXT, dob TEXT,
            password TEXT NOT NULL, photo_path TEXT)''')

        default_username = "trackwise"
        default_password = "trackwise123"
        cursor.execute("SELECT * FROM users WHERE username = ?", (default_username,))
        if cursor.fetchone() is None:
            hashed_password = bcrypt.hashpw(default_password.encode(), bcrypt.gensalt())
            cursor.execute('''
                    INSERT INTO users (username, role, email, phone, dob, password, photo_path)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
            default_username, "Manager", "trackwise@example.com", "0123456789", "1990-01-01", hashed_password, None))

        conn.commit()
        conn.close()

    def login(self):
        username = self.username.get()
        password = self.password.get()

        conn = sqlite3.connect("Trackwise.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id,password, role FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user:
            user_id,stored_hashed_password, role = user

            if bcrypt.checkpw(password.encode(), stored_hashed_password):
                if role == "Admin":
                    messagebox.showinfo("Login Successful", f"Welcome {role.capitalize()}!")
                    self.controller.logged_in_user_id = user_id
                    self.controller.show_frame("AdminDashboard")
                elif role == "Manager":
                    messagebox.showinfo("Login Successful", f"Welcome {role.capitalize()}!")
                    self.controller.logged_in_user_id = user_id
                    self.controller.show_frame("ManagerDashboard")
                elif role == "Cashier":
                    messagebox.showinfo("Login Successful", f"Welcome {role.capitalize()}!")
                    self.controller.logged_in_user_id = user_id
                    self.controller.show_frame("CashierDashboard")
                else:
                    messagebox.showerror("Error", "Unknown role. Please contact Manager.")
            else:
                messagebox.showerror("Error", "Invalid Username or Password")
        else:
            messagebox.showerror("Error", "Invalid Username or Password")

    def forget_password(self):
        ForgetPasswordPage(parent=self, controller=self.controller)

    def new_account(self):
        messagebox.showinfo("Help","Please contact your Manager")

    def toggle_password_visibility(self):
        if self.password_entry.cget("show") == "":
            self.password_entry.configure(show="*")
            self.toggle_button.configure(text="👁")
        else:
            self.password_entry.configure(show="")
            self.toggle_button.configure(text="🙈")

    def clear_fields(self):
        self.username.set("")
        self.password.set("")

    def setup_ui(self):
        username_label = ctk.CTkLabel(self, text="Username:", font=("Inter", 22), bg_color="#CFEAFA", text_color="Black")
        username_label.place(x=150 / 1920 * self.width, y=380 / 974 * self.height)

        self.username = StringVar()
        username_entry = ctk.CTkEntry(self, width=395 / 1536 * self.width, height=45 / 864 * self.height,
                                      bg_color="#D9D9D9", textvariable=self.username)
        username_entry.place(x=148 / 1920 * self.width, y=418 / 974 * self.height)

        password_label = ctk.CTkLabel(self, text="Password:", font=("Inter", 22), bg_color="#CFEAFA", text_color="black")
        password_label.place(x=152 / 1920 * self.width, y=490 / 974 * self.height)

        self.password = StringVar()
        self.password_entry = ctk.CTkEntry(self, width=395 / 1536 * self.width, height=45 / 864 * self.height,
                                      bg_color="#D9D9D9", textvariable=self.password, show="*")
        self.password_entry.place(x=148 / 1920 * self.width, y=528 / 974 * self.height)
        self.toggle_button = ctk.CTkButton(self, text="👁", width=30, height=30,
                                           font=("Arial", 20),
                                           command=self.toggle_password_visibility,
                                           fg_color="#CFEAFA", text_color="Blue",
                                           bg_color="#CFEAFA", hover_color="#BFEAFE")
        self.toggle_button.place(x=(285 + 360) / 1920 * self.width, y=538 / 974 * self.height)

        forgot_label = ctk.CTkLabel(self, text="Forgot Password?", font=("Inter", 15), bg_color="#CFEAFA", text_color="Blue")
        forgot_label.place(x=451 / 1920 * self.width, y=580 / 974 * self.height)
        forgot_label.bind("<Button-1>", lambda e: self.forget_password())

        login_button = ctk.CTkButton(self, text="Login", bg_color="#D9D9D9", fg_color="Blue", text_color="white",
                                     border_color="#1572D3", width=160, height=44, font=("Inter", 18), command=self.login)
        login_button.place(x=273 / 1920 * self.width, y=645 / 974 * self.height)

        account_label = ctk.CTkLabel(self, text="Don't have an account?",
                                     font=("Inter", 15),
                                     bg_color="#D9D9D9", fg_color="#CFEAFA",
                                     text_color="black")
        account_label.place(x=285 / 1920 * self.width, y=715 / 974 * self.height)

        new_label = ctk.CTkLabel(self, text="Create a New Account", font=("Arial", 17), bg_color="#CFEAFA", text_color="#5885F0")
        new_label.place(x=266 / 1920 * self.width, y=740 / 974 * self.height)
        new_label.bind("<Button-1>", lambda e: self.new_account())
