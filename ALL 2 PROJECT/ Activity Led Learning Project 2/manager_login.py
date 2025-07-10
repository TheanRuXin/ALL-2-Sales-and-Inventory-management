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

        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()
        self.allowed_roles = ["Manager", "Admin", "Cashier"]

        self.background_image = ctk.CTkImage(Image.open("Group 2 (1).png"),
                                             size=(self.screen_width, self.screen_height))
        background_label = ctk.CTkLabel(self, image=self.background_image, text="")
        background_label.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.initialize_db()
        self.setup_ui()

    def bind_enter_key(self):
        self.controller.bind("<Return>", lambda event: self.login())

    def unbind_enter_key(self):
        self.controller.unbind("<Return>")

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
                default_username, "Manager", "trackwise@example.com",
                "0123456789", "1990-01-01", hashed_password, None))

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
            if isinstance(stored_hashed_password, str):
                stored_hashed_password = stored_hashed_password.encode()

            if bcrypt.checkpw(password.encode(), stored_hashed_password):
                if role not in self.allowed_roles:
                    messagebox.showerror("Access Denied", "You are not authorized to access this system.")
                    return

                messagebox.showinfo("Login Successful", f"Welcome {role.capitalize()}!")
                self.controller.logged_in_user_id = user_id
                self.controller.show_frame(f"{role}Dashboard")

                # ✅ Clear fields
                self.username.set("")
                self.password.set("")
            else:
                messagebox.showerror("Error", "Invalid Username or Password")
        else:
            messagebox.showerror("Error", "Invalid Username or Password")

    def forget_password(self):
        ForgetPasswordPage(parent=self, controller=self.controller)

    def new_account(self):
        messagebox.showinfo("Help", "Please contact your Manager")

    def toggle_password_visibility(self):
        if self.password_entry.cget("show") == "":
            self.password_entry.configure(show="*")
            self.toggle_button.configure(text="👁")
        else:
            self.password_entry.configure(show="")
            self.toggle_button.configure(text="🙈")

    def setup_ui(self):
        w, h = self.screen_width, self.screen_height

        self.username = StringVar()
        self.password = StringVar()

        username_label = ctk.CTkLabel(self, text="Username:", font=("Inter", 22), bg_color="#CFEAFA",
                                      text_color="Black")
        username_label.place(x=150 / 1920 * w, y=380 / 974 * h)

        self.username_entry = ctk.CTkEntry(self, width=395 / 1536 * w, height=45 / 864 * h,
                                           bg_color="#CFEAFA", textvariable=self.username)
        self.username_entry.place(x=148 / 1920 * w, y=418 / 974 * h)

        password_label = ctk.CTkLabel(self, text="Password:", font=("Inter", 22), bg_color="#CFEAFA", text_color="black")
        password_label.place(x=152 / 1920 * w, y=490 / 974 * h)

        self.password_entry = ctk.CTkEntry(self, width=395 / 1536 * w, height=45 / 864 * h,
                                           bg_color="#CFEAFA", textvariable=self.password, show="*")
        self.password_entry.place(x=148 / 1920 * w, y=528 / 974 * h)

        # 👁 Password visibility toggle button
        self.toggle_button = ctk.CTkButton(self, text="👁", width=30, height=30,
                                           font=("Arial", 20),
                                           command=self.toggle_password_visibility,
                                           fg_color="#CFEAFA", text_color="Blue",
                                           bg_color="#CFEAFA", hover_color="#BFEAFE")
        self.toggle_button.place(x=(285 + 360) / 1920 * w, y=538 / 974 * h)

        forgot_label = ctk.CTkLabel(self, text="Forgot Password?", font=("Inter", 15),
                                    bg_color="#CFEAFA", text_color="Blue")
        forgot_label.place(x=451 / 1920 * w, y=580 / 974 * h)
        forgot_label.bind("<Button-1>", lambda e: self.forget_password())

        login_button = ctk.CTkButton(self, text="Login", bg_color="#CFEAFA", fg_color="Blue", text_color="white",
                                     border_color="#1572D3", width=160, height=44, font=("Inter", 18), command=self.login)
        login_button.place(x=273 / 1920 * w, y=645 / 974 * h)

        account_label = ctk.CTkLabel(self, text="Don't have an account?",
                                     font=("Inter", 15),
                                     fg_color="#CFEAFA", text_color="black")
        account_label.place(x=285 / 1920 * w, y=715 / 974 * h)

        new_label = ctk.CTkLabel(self, text="Create a New Account", font=("Arial", 17),
                                 bg_color="#CFEAFA", text_color="#5885F0")
        new_label.place(x=266 / 1920 * w, y=740 / 974 * h)
        new_label.bind("<Button-1>", lambda e: self.new_account())

    def clear_fields(self):
        self.username.set("")
        self.password.set("")
        self.password_entry.configure(show="*")  # Reset password visibility
        self.toggle_button.configure(text="👁")  # Reset toggle button
