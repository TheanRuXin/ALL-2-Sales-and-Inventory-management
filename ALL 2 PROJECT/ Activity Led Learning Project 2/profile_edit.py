import customtkinter as ctk
from PIL import Image
from tkinter import filedialog, messagebox
import sqlite3
import bcrypt
import os, re
from datetime import datetime
from tkcalendar import DateEntry

class EditProfileApp(ctk.CTkFrame):
    def __init__(self, parent, controller, user_id):
        super().__init__(parent)
        self.controller = controller
        self.user_id = user_id
        self.photo_path = None
        self.configure(fg_color="#FFFFFF")

        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()

        self.create_main_frame()
        self.create_layout()
        self.populate_user_data()

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

    def create_layout(self):
        self.add_image()
        self.add_labels()
        self.add_entries()
        self.add_buttons()

    def add_image(self):
        self.image_label = ctk.CTkLabel(self.main_frame, text="")
        self.image_label.place(x=125, y=150)

    def add_labels(self):
        labels = [
            ("Change Password", 900, 40, 35),
            ("(optional)", 1200, 50, 25),
            ("Username:", 480, 100, 28),
            ("Email:", 480, 220, 28),
            ("Phone Number:", 480, 340, 28),
            ("Date of Birth:", 480, 460, 28),
            ("Old Password:", 915, 160, 28),
            ("New Password:", 915, 280, 28),
            ("Confirm New Password:", 915, 400, 28),
        ]
        for text, x, y, size in labels:
            label = ctk.CTkLabel(self.main_frame, text=text, font=("Inter", size), text_color="#000000")
            label.place(x=x, y=y)

    def add_entries(self):
        self.entries = {}
        fields = [
            ("Username", 480, 140),
            ("Email", 480, 260),
            ("Phone Number", 480, 380),
            ("Old Password", 915, 200),
            ("New Password", 915, 320),
            ("Confirm Password", 915, 440)
        ]
        for label, x, y in fields:
            show = "*" if "Password" in label else ""
            entry = ctk.CTkEntry(self.main_frame, width=300, height=40, fg_color="#FFFAFA", text_color="#000000", show=show, font=("Inter", 16))
            entry.place(x=x, y=y)
            self.entries[label] = entry

        self.dob_calendar = DateEntry(self.main_frame, date_pattern='dd/mm/yyyy', width=31, background='lightblue', foreground='black', borderwidth=2, font=('Inter', 14))
        self.dob_calendar.place(x=600, y=630)
        self.entries["Date of Birth"] = self.dob_calendar

    def add_buttons(self):
        buttons = [
            ("Save", 1050, 580, self.save_changes),
            ("Cancel", 1200, 580, self.cancel_edit),
            ("Change Photo", 130, 380, self.change_photo),
        ]
        for text, x, y, cmd in buttons:
            width = 190 if text == "Change Photo" else 120
            btn = ctk.CTkButton(self.main_frame, text=text, command=cmd, width=width, height=50, font=("Inter", 18))
            btn.place(x=x, y=y)

    def populate_user_data(self):
        conn = sqlite3.connect("Trackwise.db")
        cursor = conn.cursor()
        cursor.execute("SELECT username, email, phone, dob, photo_path FROM users WHERE id = ?", (self.user_id,))
        result = cursor.fetchone()
        conn.close()

        if result:
            username, email, phone, dob, photo_path = result
            self.entries["Username"].insert(0, username or "")
            self.entries["Email"].insert(0, email or "")
            self.entries["Phone Number"].insert(0, phone or "")
            if dob:
                try:
                    self.dob_calendar.set_date(datetime.strptime(dob, "%d/%m/%Y"))
                except:
                    pass
            self.photo_path = photo_path
            if photo_path and os.path.exists(photo_path):
                try:
                    img = ctk.CTkImage(Image.open(photo_path), size=(200, 200))
                    self.image_label.configure(image=img)
                    self.image_label.image = img
                except:
                    pass

    def change_photo(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            try:
                img = ctk.CTkImage(Image.open(file_path), size=(200, 200))
                self.image_label.configure(image=img)
                self.image_label.image = img
                self.photo_path = file_path
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {e}")

    def save_changes(self):
        username = self.entries["Username"].get().strip()
        email = self.entries["Email"].get().strip()
        phone = self.entries["Phone Number"].get().strip()
        dob = self.dob_calendar.get().strip()
        old_pw = self.entries["Old Password"].get()
        new_pw = self.entries["New Password"].get()
        confirm_pw = self.entries["Confirm Password"].get()

        conn = sqlite3.connect("Trackwise.db")
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE id = ?", (self.user_id,))
        result = cursor.fetchone()

        if not result:
            messagebox.showerror("Error", "User not found.")
            return

        current_hashed_pw = result[0]
        if old_pw or new_pw or confirm_pw:
            if not bcrypt.checkpw(old_pw.encode(), current_hashed_pw.encode()):
                messagebox.showerror("Error", "Old password incorrect.")
                return
            if new_pw != confirm_pw:
                messagebox.showerror("Error", "Passwords do not match.")
                return
            if len(new_pw) < 8 or not re.search(r'\d', new_pw) or not re.search(r'[A-Z]', new_pw):
                messagebox.showerror("Error", "Password must be 8+ characters, with number and uppercase.")
                return
            new_hashed_pw = bcrypt.hashpw(new_pw.encode(), bcrypt.gensalt())
        else:
            new_hashed_pw = current_hashed_pw

        cursor.execute("""
            UPDATE users SET username = ?, email = ?, phone = ?, dob = ?, password = ?, photo_path = ?
            WHERE id = ?
        """, (username, email, phone, dob, new_hashed_pw, self.photo_path, self.user_id))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Profile updated successfully.")
        self.controller.show_profile(self.user_id)

    def cancel_edit(self):
        self.controller.show_profile(self.user_id)
