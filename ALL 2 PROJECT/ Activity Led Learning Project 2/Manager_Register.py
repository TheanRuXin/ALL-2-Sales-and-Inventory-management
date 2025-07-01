import customtkinter as ctk
from PIL import Image
from tkinter import messagebox
import sqlite3
import re
import bcrypt

class Manager_Register(ctk.CTkFrame):
    def __init__(self,parent,controller):
        super().__init__(parent)
        self.controller = controller
        self.width, self.height = 1574, 800

        background_image = ctk.CTkImage(Image.open(r"manager register.png"), size=(self.width, self.height))
        background_label = ctk.CTkLabel(self, image=background_image, text="")
        background_label.place(x=0, y=0)
        self.create_widgets()

    def create_widgets(self):
        main_frame = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=15, width=1000, height=600)
        main_frame.place(relx=0.5, rely=0.65, anchor="center")

        left_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        left_frame.grid(row=0, column=0, padx=50, pady=20, sticky="n")

        right_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        right_frame.grid(row=0, column=1, padx=50, pady=20, sticky="n")

        # Username
        ctk.CTkLabel(left_frame, text="Username:", font=("Arial", 24)).pack(pady=(10, 5), anchor="w")
        self.username_entry = ctk.CTkEntry(left_frame, placeholder_text="Username", width=350, height=35, justify="center", font=("Arial", 24))
        self.username_entry.pack(pady=(0, 30))

        # Email
        ctk.CTkLabel(left_frame, text="Email:", font=("Arial", 24)).pack(pady=(10, 5), anchor="w")
        self.email_entry = ctk.CTkEntry(left_frame, placeholder_text="Email", width=350, height=35, justify="center", font=("Arial", 24))
        self.email_entry.pack(pady=(0, 30))

        # Role (fixed to Manager)
        ctk.CTkLabel(left_frame, text="User Role:", font=("Arial", 24)).pack(pady=(10,5), anchor="w")
        self.role_entry = ctk.CTkEntry(left_frame, placeholder_text="Manager", width=350, height=35, justify="center", font=("Arial", 24))
        self.role_entry.insert(0, "Manager")
        self.role_entry.configure(state="disabled")
        self.role_entry.pack()

        # Phone
        ctk.CTkLabel(right_frame, text="Phone Number:", font=("Arial", 24)).pack(pady=(10, 5), anchor="w")
        self.phone_entry = ctk.CTkEntry(right_frame, placeholder_text="ex:012-1234567", width=350, height=35, justify="center", font=("Arial", 24))
        self.phone_entry.pack(pady=(0, 30))

        # Password
        ctk.CTkLabel(right_frame, text="Password:", font=("Arial", 24)).pack(pady=(10, 5), anchor="w")
        self.password_entry = ctk.CTkEntry(right_frame, placeholder_text="Password", show="*", width=350, height=35, justify="center", font=("Arial", 24))
        self.password_entry.pack(pady=(0, 30))

        # Confirm Password
        ctk.CTkLabel(right_frame, text="Confirm Password:", font=("Arial", 24)).pack(pady=(10, 5), anchor="w")
        self.confirm_password_entry = ctk.CTkEntry(right_frame, placeholder_text="Confirm Password", show="*", width=350, height=35, justify="center", font=("Arial", 24))
        self.confirm_password_entry.pack(pady=(0, 30))

        register_button = ctk.CTkButton(main_frame, text="Register", width=300, height=30, fg_color="#2A50CB",
                                        hover_color="#1a39a3", command=self.register_manager)
        register_button.grid(row=1, column=0, columnspan=2, pady=(30, 20))

        # Back Button
        ctk.CTkButton(self, text="<- Back", width=100, height=30, fg_color="#2A50CB", hover_color="#1a39a3", command=self.back_to_login).place(x=30, rely=0.97, anchor="sw")

    def hash_password(self, password):
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def back_to_login(self):
        self.controller.show_frame("MainPage")

    def register_manager(self):
        username = self.username_entry.get().strip()
        email = self.email_entry.get().strip()
        phone = self.phone_entry.get().strip()
        password = self.password_entry.get().strip()
        confirm_password = self.confirm_password_entry.get().strip()

        if not username or not email or not phone or not password or not confirm_password:
            messagebox.showerror("Error", "All fields are required!")
            return

        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match!")
            return

        if len(password) < 8 or not re.search(r'\d', password) or not re.search(r'[A-Z]', password):
            messagebox.showerror("Error", "Password must have at least 8 characters, including 1 uppercase and 1 number.")
            return

        conn = sqlite3.connect('Trackwise.db')
        cursor = conn.cursor()

        # Check username existence only
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        if cursor.fetchone():
            messagebox.showerror("Error", "Username already exists!")
            conn.close()
            return

        hashed_pw = self.hash_password(password)

        # Insert full record
        cursor.execute("""INSERT INTO users (username, role, email, phone, dob, password, photo_path) VALUES (?,?,?,?,?,?,?)""",
                       (username, "Manager", email, phone, "", hashed_pw, ""))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "User registered successfully!")
        self.back_to_login()