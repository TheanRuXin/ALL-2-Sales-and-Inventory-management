import customtkinter as ctk
from PIL import Image
from customtkinter import CTkImage
import sqlite3
import os

def initialize_database():
    conn = sqlite3.connect("Trackwise.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        role TEXT,
        email TEXT,
        phone TEXT,
        dob TEXT,
        photo_path TEXT
    )
    """)

    conn.commit()
    conn.close()

class UserPage(ctk.CTkFrame):
    def __init__(self, parent,controller, user_id):
        super().__init__(parent)
        self.controller = controller
        self.user_id = user_id
        self.user_data = self.get_user_data_from_db()
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()
        self.configure(fg_color="#FFFFFF")
        self.create_main_frame()
        self.create_edit_button()
        self.load_profile_image()
        self.create_welcome_label()
        self.create_user_info_labels()
        self.create_back_button()

    def get_user_data_from_db(self):
        try:
            conn = sqlite3.connect("Trackwise.db")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT username, role, email, phone, dob
                FROM users WHERE id = ?
            """, (self.user_id,))
            row = cursor.fetchone()
            conn.close()
            if row:
                return {
                    "username": row[0],
                    "role": row[1],
                    "email": row[2],
                    "phone": row[3],
                    "dob": row[4]
                }
            else:
                return None
        except Exception as e:
            print(f"Database error: {e}")
            return None

    def create_main_frame(self):
        self.main_frame_width = int(self.screen_width * 0.92)
        self.main_frame_height = int(self.screen_height * 0.76)

        # Shift frame just 40 pixels to the left instead of 100
        main_frame_x = (self.screen_width - self.main_frame_width) // 2 - 40
        main_frame_y = (self.screen_height - self.main_frame_height) // 2 - 35

        self.main_frame = ctk.CTkFrame(
            master=self,
            width=self.main_frame_width,
            height=self.main_frame_height,
            corner_radius=10,
            fg_color="#D9D9D9"
        )
        self.main_frame.place(x=main_frame_x, y=main_frame_y)

    def create_edit_button(self):
        edit_button_width = int(self.screen_width * 0.065)
        edit_button_height = int(self.screen_height * 0.06)

        self.edit_button = ctk.CTkButton(
            master=self.main_frame,
            text="Edit",
            command=self.on_edit_click,
            width=edit_button_width,
            height=edit_button_height,
            font = ("Inter", 18)
        )
        self.edit_button.place(x=self.screen_width - 260, y=66)

    def on_edit_click(self):
        self.load_edit_page()

    def load_profile_image(self):
        try:
            conn = sqlite3.connect("Trackwise.db")
            cursor = conn.cursor()
            cursor.execute("SELECT photo_path FROM users WHERE id = ?", (self.user_id,))
            row = cursor.fetchone()
            conn.close()

            image_path = row[0] if row and row[0] and os.path.exists(row[0]) else r"C:\Users\User\Documents\Ruxin file\ALL 2\profile_pic.png"

            profile_img = Image.open(image_path)
            profile_img = profile_img.resize((200, 200))
            profile_photo = CTkImage(dark_image=profile_img, size=(200, 200))

            self.profile_label = ctk.CTkLabel(master=self.main_frame, image=profile_photo, text="")
            self.profile_label.image = profile_photo
            self.profile_label.place(x=int(self.screen_width * 0.12), y=int(self.screen_height * 0.15))
        except Exception as e:
            print(f"Image load error: {e}")

    def create_welcome_label(self):
        username = self.user_data['username'] if self.user_data else "User"
        welcome_y = int(self.screen_height * 0.42)
        self.welcome_label = ctk.CTkLabel(
            master=self.main_frame,
            text=f"Welcome, {username}",
            font=("Inter", 30),
            text_color="#131010"
        )
        self.welcome_label.place(x=int(self.screen_width * 0.095), y=welcome_y)

        # Add role below welcome message
        if self.user_data and self.user_data['role']:
            self.role_label = ctk.CTkLabel(
                master=self.main_frame,
                text=self.user_data["role"],
                font=("Inter", 24),
                text_color="#5E5E5E"
            )
            self.role_label.place(x=int(self.screen_width * 0.15), y=welcome_y + 40)

    def create_user_info_labels(self):
        if not self.user_data:
            return

        # Left side: Username, Phone Number
        left_info = [
            ("Username:", self.user_data["username"]),
            ("Phone Number:", self.user_data["phone"])
        ]

        # Right side: Email, Date of Birth
        right_info = [
            ("Email:", self.user_data["email"]),
            ("Date of Birth:", self.user_data["dob"])
        ]

        left_x = int(self.screen_width * 0.37)
        right_x = int(self.screen_width * 0.68)
        start_y = int(self.screen_height * 0.20)
        gap = int(self.screen_height * 0.20)

        for i, (label_text, value_text) in enumerate(left_info):
            label = ctk.CTkLabel(
                master=self.main_frame,
                text=label_text,
                font=("Inter", 30),
                text_color="#000000"
            )
            label.place(x=left_x, y=start_y + i * gap)

            value = ctk.CTkLabel(
                master=self.main_frame,
                text=value_text,
                font=("Inter", 25),
                text_color="#796E6E"
            )
            value.place(x=left_x, y=start_y + 44 + i * gap)

        for i, (label_text, value_text) in enumerate(right_info):
            label = ctk.CTkLabel(
                master=self.main_frame,
                text=label_text,
                font=("Inter", 30),
                text_color="#000000"
            )
            label.place(x=right_x, y=start_y + i * gap)

            value = ctk.CTkLabel(
                master=self.main_frame,
                text=value_text,
                font=("Inter", 25),
                text_color="#796E6E"
            )
            value.place(x=right_x, y=start_y + 44 + i * gap)

    def on_back_click(self):
        role = self.user_data["role"].lower() if self.user_data and self.user_data["role"] else ""

        if role == "admin":
            self.controller.show_frame("AdminDashboard")
        elif role == "manager":
            self.controller.show_frame("ManagerDashboard")
        elif role == "cashier":
            self.controller.show_frame("POSApp")
        else:
            print("Unknown role. Cannot route to dashboard.")

        self.destroy()

    def create_back_button(self):
        back_button = ctk.CTkButton(
            master=self.main_frame,
            text="← Back",
            command=self.on_back_click,
            width=100,
            height=40,
            font=("Inter", 16)
        )
        back_button.place(x=20, y=20)

    def load_edit_page(self):
        from profile_edit import EditProfileApp
        for widget in self.winfo_children():
            widget.destroy()
        edit_frame = EditProfileApp(self, self.controller, self.user_id)
        edit_frame.pack(fill="both", expand=True)
