import sqlite3
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import re
import hashlib
import os

class Reset_Password:
    def __init__(self,root):
        self.root = root
        self.root.title("Reset Password")
        self.root.geometry("974x500")

        self.width = self.root.winfo_screenwidth()
        self.height = self.root.winfo_screenheight()

        background_image = ctk.CTkImage(Image.open("assets/Register_User.png"), size=(self.width, self.height - 71))
        background_image_label = ctk.CTkLabel(self.root, image=background_image, text="")
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
        self.password_text = ctk.CTkLabel(self.root, text="Password",
                                          font=("Inter", 23),
                                          bg_color="#FFFFFF", fg_color="#FFFFFF",
                                          text_color="black")
        self.password_text.place(x=550 / 1920 * self.width, y=112 / 974 * self.height)

        self.password = ctk.StringVar()
        self.password_entry = ctk.CTkEntry(self.root, font=("Inter", 18), width=320 / 1536 * self.width,
                                           height=45 / 864 * self.height, bg_color="#FFFFFF",
                                           fg_color="#D9D9D9", border_color="#FFFFFF", text_color="black",
                                           textvariable=self.password, show="*")
        self.password_entry.place(x=550 / 1920 * self.width, y=152 / 974 * self.height)

        # Confirm Password
        self.con_text = ctk.CTkLabel(self.root, text="Confirm Password",
                                      font=("Inter", 23),
                                      bg_color="#FFFFFF", fg_color="#FFFFFF",
                                      text_color="black")
        self.con_text.place(x=550 / 1920 * self.width, y=300 / 974 * self.height)

        self.con = ctk.StringVar()
        self.con_entry = ctk.CTkEntry(self.root, font=("Inter", 18), width=320 / 1536 * self.width,
                                       height=45 / 864 * self.height, bg_color="#FFFFFF",
                                       fg_color="#D9D9D9", border_color="#FFFFFF", text_color="black",
                                       textvariable=self.con, show="*")
        self.con_entry.place(x=550 / 1920 * self.width, y=350 / 974 * self.height)

        # Buttons
        # Reset Password
        reset_button = ctk.CTkButton(self.root, text="Reset Password", bg_color="#D9D9D9", fg_color="Blue",
                                     text_color="white",
                                     border_color="#1572D3", width=129, height=35,
                                     font=("Iter", 14), command=self.reset_password)
        reset_button.place(x=625 / 1920 * root.winfo_screenwidth(), y=450 / 974 * root.winfo_screenheight())

    def is_valid_password(self, password):
        pattern = r"^(?=.*[A-Z])(?=.*\d).{8,}$"
        return re.match(pattern, password)

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def reset_password(self):
        password = self.password.get()
        confirm = self.con.get()

        if not password or not confirm:
            messagebox.showerror("Error", "Both fields are required.")
            return

        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match.")
            return

        try:
            conn = sqlite3.connect("Trackwise.db")
            cursor = conn.cursor()

            # Check if new password is different from old Password
            cursor.execute("SELECT password FROM users WHERE username = ?", (self.username,))
            result = cursor.fetchone()

            new_hashed = self.hash_password(password)

            if result and new_hashed == result[0]:
                messagebox.showerror("Error", "New password cannot be the same as the previous password.")
                conn.close()
                return

            #Update New Password
            cursor.execute("UPDATE users SET password = ? WHERE username = ?", (new_hashed, self.username))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Password reset successfully!")

            # Delete the temporary username file
            try:
                os.remove("reset_user.txt")
            except FileNotFoundError:
                pass

            self.root.destroy()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to reset password: {e}")


root = ctk.CTk()
app = Reset_Password(root)
root.mainloop()