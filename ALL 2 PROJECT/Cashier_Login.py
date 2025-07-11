import hashlib
import sqlite3
import customtkinter as ctk
from tkinter import messagebox, StringVar
from PIL import Image
import subprocess
import tempfile
import pickle
import os

class Cashier_Login:
    def __init__(self, root):
        self.root = root
        self.root.title("Inventory Management System")
        self.root.geometry("1920x974")

        self.width = self.root.winfo_screenwidth()
        self.height = self.root.winfo_screenheight()

        background_image = ctk.CTkImage(Image.open("assets/Manager_Login.png"), size=(self.width, self.height - 71))
        background_image_label = ctk.CTkLabel(self.root, image=background_image, text="")
        background_image_label.place(relx=0, rely=0)

        self.initialize_db()
        self.setup_ui()

    def initialize_db(self):
        conn = sqlite3.connect("Trackwise.db")
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                             id INTEGER PRIMARY KEY AUTOINCREMENT,
                             username TEXT NOT NULL,
                             role TEXT NOT NULL,
                             email TEXT NOT NULL,
                             phone TEXT NOT NULL,
                             dob TEXT NOT NULL,
                             password TEXT NOT NULL,
                             photo_path TEXT NOT NULL
                          )
                       ''')
        conn.commit()
        conn.close()

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def login(self):
        username = self.username.get()
        password = self.password.get()
        hashed_pw = self.hash_password(password)

        conn = sqlite3.connect("Trackwise.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_pw))
        user = cursor.fetchone()
        conn.close()

        if user:
            messagebox.showinfo("Login Successful", f"Welcome {user[3].capitalize()}!")
            self.root.destroy()

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pkl") as f:
                pickle.dump(user, f)
                data_path = f.name

            # Run Main.py with logging for debug
            with open("main_log.txt", "w") as log:
                subprocess.Popen(["python", "Main.py", data_path], stdout=log, stderr=log)
        else:
            messagebox.showerror("Error", "Invalid Username or Password")

    def forget_password(self):
        subprocess.Popen(["python", "Forget_Password.py"])

    def setup_ui(self):
        # Username
        username_label = ctk.CTkLabel(self.root, text="Username:", font=("Inter", 22),
                                      bg_color="#D9D9D9", text_color="Black")
        username_label.place(x=150 / 1920 * self.width, y=390 / 974 * self.height)

        self.username = StringVar()
        username_entry = ctk.CTkEntry(self.root, width=395 / 1536 * self.width,
                                      height=45 / 864 * self.height, bg_color="#D9D9D9",
                                      fg_color="white", border_color="#D9D9D9", text_color="black",
                                      textvariable=self.username)
        username_entry.place(x=148 / 1920 * self.width, y=438 / 974 * self.height)

        # Password
        password_label = ctk.CTkLabel(self.root, text="Password:", font=("Inter", 22),
                                      bg_color="#D9D9D9", fg_color="#D9D9D9", text_color="black")
        password_label.place(x=152 / 1920 * self.width, y=510 / 974 * self.height)

        self.password = StringVar()
        password_entry = ctk.CTkEntry(self.root, width=395 / 1536 * self.width,
                                      height=45 / 864 * self.height, bg_color="#D9D9D9",
                                      fg_color="white", border_color="#D9D9D9", text_color="black",
                                      textvariable=self.password, show="*")
        password_entry.place(x=148 / 1920 * self.width, y=558 / 974 * self.height)

        # Forgot Password
        forgot_label = ctk.CTkLabel(self.root, text="Forgot Password?", font=("Inter", 15),
                                    bg_color="#D9D9D9", text_color="Blue")
        forgot_label.place(x=451 / 1920 * self.width, y=610 / 974 * self.height)
        forgot_label.bind("<Button-1>", lambda e: self.forget_password())

        # Login Button
        login_button = ctk.CTkButton(self.root, text="Login", bg_color="#D9D9D9", fg_color="Blue",
                                     text_color="white", border_color="#1572D3", width=160, height=44,
                                     font=("Inter", 18), command=self.login)
        login_button.place(x=273 / 1920 * self.width, y=675 / 974 * self.height)

        # Help Button
        cashier_button = ctk.CTkButton(self.root, text="Help!", bg_color="#D9D9D9", fg_color="Blue",
                                       text_color="white", border_color="#1572D3", width=129, height=35,
                                       font=("Inter", 14))
        cashier_button.place(x=866 / 1920 * self.width, y=759 / 974 * self.height)

        # Trackwise Button
        admin_button = ctk.CTkButton(self.root, text="Trackwise", bg_color="#D9D9D9", fg_color="Blue",
                                     text_color="white", border_color="#1572D3", width=129, height=35,
                                     font=("Inter", 14))
        admin_button.place(x=1623 / 1920 * self.width, y=759 / 974 * self.height)


if __name__ == "__main__":
    root = ctk.CTk()
    app = Cashier_Login(root)
    root.mainloop()
