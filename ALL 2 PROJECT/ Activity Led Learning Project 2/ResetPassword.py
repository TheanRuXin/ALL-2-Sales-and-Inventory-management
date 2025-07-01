import sqlite3
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import re
import bcrypt
import os

class Reset_Password(ctk.CTkToplevel):
    def __init__(self, parent,controller=None,on_close_callback=None):
        super().__init__(parent)
        self.controller = controller
        self.on_close_callback = on_close_callback
        self.title("Reset Password")
        self.geometry("974x500")
        self.attributes("-topmost", True)
        self.resizable(False, False)

        self.width = self.winfo_screenwidth()
        self.height = self.winfo_screenheight()

        background_image = ctk.CTkImage(Image.open(r"forget password.png"), size=(974,500))
        background_image_label = ctk.CTkLabel(self, image=background_image, text="")
        background_image_label.place(relx=0, rely=0)

        self.display_ui()

        with open("reset_user.txt", "r") as f:
            self.username = f.read().strip()

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

    def display_ui(self):
        # Password
        self.password_text = ctk.CTkLabel(self, text="Password",
                                          font=("Inter", 23),
                                          bg_color="#FFFFFF", fg_color="#FFFFFF",
                                          text_color="black")
        self.password_text.place(x=400 / 1920 * self.width, y=112 / 974 * self.height)

        self.password = ctk.StringVar()
        self.password_entry = ctk.CTkEntry(self, font=("Inter", 18), width=320 / 1536 * self.width,
                                           height=45 / 864 * self.height, bg_color="#FFFFFF",
                                           fg_color="#D9D9D9", border_color="#FFFFFF", text_color="black",
                                           textvariable=self.password, show="*")
        self.password_entry.place(x=400 / 1920 * self.width, y=152 / 974 * self.height)

        # Confirm Password
        self.con_text = ctk.CTkLabel(self, text="Confirm Password",
                                      font=("Inter", 23),
                                      bg_color="#FFFFFF", fg_color="#FFFFFF",
                                      text_color="black")
        self.con_text.place(x=400 / 1920 * self.width, y=300 / 974 * self.height)

        self.con = ctk.StringVar()
        self.con_entry = ctk.CTkEntry(self, font=("Inter", 18), width=320 / 1536 * self.width,
                                       height=45 / 864 * self.height, bg_color="#FFFFFF",
                                       fg_color="#D9D9D9", border_color="#FFFFFF", text_color="black",
                                       textvariable=self.con, show="*")
        self.con_entry.place(x=400 / 1920 * self.width, y=350 / 974 * self.height)

        # Buttons
        # Reset Password
        reset_button = ctk.CTkButton(self, text="Reset Password", bg_color="#D9D9D9", fg_color="Blue",
                                     text_color="white",
                                     border_color="#1572D3", width=129, height=35,
                                     font=("Iter", 14), command=self.reset_password)
        reset_button.place(x=400 / 1920 * self.winfo_screenwidth(), y=450 / 974 * self.winfo_screenheight())

    def is_valid_password(self, password):
        pattern = r"^(?=.*[A-Z])(?=.*\d).{8,}$"
        return re.match(pattern, password)

    def hash_password(self, password):
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def reset_password(self):
        password = self.password.get()
        confirm = self.con.get()

        if not password or not confirm:
            messagebox.showerror("Error", "Both fields are required.", parent=self)
            self.password_entry.focus_set()
            return

        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match.", parent=self)
            self.password_entry.focus_set()
            return

        if not self.is_valid_password(password):
            messagebox.showerror("Error",
                                 "Password must have at least 8 characters, including 1 uppercase and 1 number.",
                                 parent=self)
            return

        try:
            conn = sqlite3.connect("Trackwise.db")
            cursor = conn.cursor()

            cursor.execute("SELECT password FROM users WHERE username = ?", (self.username,))
            result = cursor.fetchone()

            hashed_pw = self.hash_password(password)

            if result and bcrypt.checkpw(password.encode(), result[0].encode()):
                messagebox.showerror("Error", "New password cannot be the same as the previous password.", parent=self)
                conn.close()
                return

            # Update New Password
            cursor.execute("UPDATE users SET password = ? WHERE username = ?", (hashed_pw, self.username))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Password reset successfully!", parent=self)

            # Delete the temporary "username" file
            try:
                os.remove("reset_user.txt")
            except FileNotFoundError:
                pass

            self.destroy()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to reset password: {e}", parent=self)
