import customtkinter as ctk
from PIL import Image
from customtkinter import CTkImage
import sqlite3
import os, sys, subprocess

def initialize_database():
    conn = sqlite3.connect("Trackwise.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        role TEXT,
        email TEXT,
        phone TEXT,
        dob TEXT
    )
    """)

    conn.commit()
    conn.close()

class UserProfileApp:
    def __init__(self, root, user_id):
        self.root = root
        self.user_id = user_id
        self.user_data = self.get_user_data_from_db()

        self.setup_window()
        self.create_main_frame()
        self.create_edit_button()
        self.load_profile_image()
        self.create_welcome_label()
        self.create_user_info_labels()

    def get_user_data_from_db(self):
        try:
            conn = sqlite3.connect("Trackwise.db")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT username, role, email, phone, dob
                FROM users WHERE user_id = ?
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

    def setup_window(self):
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        self.root.geometry(f"{self.screen_width}x{self.screen_height}")
        self.root.title("User Profile")
        self.root.configure(bg="#FFFFFF")
        self.root.resizable(True, True)

    def create_main_frame(self):
        self.main_frame_width = int(self.screen_width * 0.92)
        self.main_frame_height = int(self.screen_height * 0.76)
        main_frame_x = (self.screen_width - self.main_frame_width) // 2
        main_frame_y = (self.screen_height - self.main_frame_height) // 2 - 35

        self.main_frame = ctk.CTkFrame(
            master=self.root,
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
        subprocess.Popen([sys.executable, "profile_edit.py"])
        self.root.destroy()

    def load_profile_image(self):
        try:
            conn = sqlite3.connect("Trackwise.db")
            cursor = conn.cursor()
            cursor.execute("SELECT photo_path FROM users WHERE user_id = ?", (self.user_id,))
            row = cursor.fetchone()
            conn.close()

            image_path = row[0] if row and row[0] and os.path.exists(row[0]) else "profile_pic.png"

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
        self.welcome_label = ctk.CTkLabel(
            master=self.main_frame,
            text=f"Welcome, {username}",
            font=("Inter", 30),
            text_color="#131010"
        )
        self.welcome_label.place(x=int(self.screen_width * 0.095), y=int(self.screen_height * 0.42))

    def create_user_info_labels(self):
        if not self.user_data:
            return

        user_info = [
            ("Username:", self.user_data["username"]),
            ("Role:", self.user_data["role"]),
            ("Email:", self.user_data["email"]),
            ("Phone Number:", self.user_data["phone"]),
            ("Date of Birth:", self.user_data["dob"])
        ]

        start_y = int(self.screen_height * 0.10)
        gap = int(self.screen_height * 0.12)

        for i, (label_text, value_text) in enumerate(user_info):
            label = ctk.CTkLabel(
                master=self.main_frame,
                text=label_text,
                font=("Inter", 30),
                text_color="#000000"
            )
            label.place(x=int(self.screen_width * 0.37), y=start_y + i * gap)

            value = ctk.CTkLabel(
                master=self.main_frame,
                text=value_text,
                font=("Inter", 25),
                text_color="#796E6E"
            )
            value.place(x=int(self.screen_width * 0.37), y=start_y + 44 + i * gap)

if __name__ == "__main__":
    initialize_database()

    window = ctk.CTk()
    app = UserProfileApp(window, user_id=1)  # You must ensure this user exists in the DB
    window.mainloop()
