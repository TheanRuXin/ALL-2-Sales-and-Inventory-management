import customtkinter as ctk
from PIL import Image
from tkinter import filedialog, messagebox, font
import sqlite3
import bcrypt
import os, subprocess, sys, re
from datetime import datetime
from tkcalendar import DateEntry

class EditProfileApp:
    def __init__(self, root, user_id):
        self.root = root
        self.user_id = user_id
        self.photo_path = None  # default, update later
        self.setup_window()
        self.create_main_frame()
        self.create_layout()
        self.populate_user_data()

    def setup_window(self):
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        self.root.geometry(f"{self.screen_width}x{self.screen_height}")
        self.root.title("Profile Edit")
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

    def create_layout(self):
        self.add_image()
        self.add_labels()
        self.add_entries()
        self.add_buttons()

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
        entry_fields = [
            ("Username", 480, 140),
            ("Email", 480, 260),
            ("Phone Number", 480, 380),
            ("Old Password", 915, 200),
            ("New Password", 915, 320),
            ("Confirm Password", 915, 440)
        ]
        entry_font = ("Inter", 16)

        for label_text, x, y in entry_fields:
            show_char = "*" if "Password" in label_text else ""
            entry = ctk.CTkEntry(self.main_frame, width=300, height=40, fg_color="#FFFAFA", text_color="#000000",show=show_char,font=entry_font)
            entry.place(x=x, y=y)
            self.entries[label_text] = entry

        # Adding Date of Birth field as a calendar
        self.dob_calendar = DateEntry(self.main_frame, date_pattern='dd/mm/yyyy', width=31, background='lightblue',
                                      foreground='black', borderwidth=2,  font=('Inter', 14))
        self.dob_calendar.place(x=600, y=630)
        self.entries["Date of Birth"] = self.dob_calendar  # Store reference to the calendar widget

    def add_buttons(self):
        button_data = [
            ("Save", 1050, 580, self.save_changes),
            ("Cancel", 1200, 580, self.cancel_edit),
            ("Change Photo", 130, 380, self.change_photo),
        ]

        for text, x, y, cmd in button_data:
            width = 190 if text == "Change Photo" else 120
            button = ctk.CTkButton(self.main_frame, text=text, command=cmd, width=width, height=50, font=("Inter",18))
            button.place(x=x, y=y)

    def add_image(self):
        try:
            # Use the user's photo if set and the file exists
            if hasattr(self, "photo_path") and self.photo_path and os.path.exists(self.photo_path):
                image_path = self.photo_path
            else:
                # Fall back to default image
                image_path = "profile_pic.png"

            img = ctk.CTkImage(Image.open(image_path), size=(200, 200))
            self.image_label = ctk.CTkLabel(self.main_frame, image=img, text="")
            self.image_label.image = img
            self.image_label.place(x=125, y=150)

        except Exception as e:
            print(f"Error loading image: {e}")

    def populate_user_data(self):
        conn = sqlite3.connect("Trackwise.db")
        cursor = conn.cursor()

        cursor.execute("SELECT username, email, phone, dob, photo_path FROM users WHERE user_id = ?", (self.user_id,))
        result = cursor.fetchone()
        conn.close()

        if result:
            username, email, phone, dob, photo_path = result
            self.entries["Username"].insert(0, username)
            self.entries["Email"].insert(0, email)
            self.entries["Phone Number"].insert(0, phone)
            self.dob_calendar.set_date(datetime.strptime(dob, "%d/%m/%Y"))  # Set the date on the calendar
            self.photo_path = photo_path

            if photo_path and os.path.exists(photo_path):
                try:
                    img = ctk.CTkImage(Image.open(photo_path), size=(200, 200))
                    self.image_label.configure(image=img)
                    self.image_label.image = img
                except Exception as e:
                    print(f"Could not load user photo: {e}")

    def change_photo(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            try:
                img = ctk.CTkImage(Image.open(file_path), size=(200, 200))
                self.image_label.configure(image=img)
                self.image_label.image = img
                self.photo_path = file_path  # store path to update DB later
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {e}")

    def validate_email(self, email):
        # Regular expression for validating email
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            messagebox.showerror("Error", "Invalid email format.")
            return False

        # Check if email is already taken by another user
        conn = sqlite3.connect("Trackwise.db")
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users WHERE email = ?", (email,))
        result = cursor.fetchone()
        conn.close()

        if result and result[0] != self.user_id:
            messagebox.showerror("Error", "Email is already registered by another user.")
            return False
        return True

    def validate_phone(self, phone):
        if not phone.startswith("+60"):
            messagebox.showerror("Error", "Phone number must start with +60.")
            return False
        if not phone[1:].isdigit():  # skip the '+' sign
            messagebox.showerror("Error", "Phone number must be digits.")
            return False
        return True

    def validate_dob(self, dob):
        try:
            datetime.strptime(dob, "%d/%m/%Y")
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Use DD/MM/YYYY.")
            return False
        return True

    def validate_password(self, password):
        if len(password) < 8:
            messagebox.showerror("Error", "Password must be at least 8 characters.")
            return False
        return True

    def save_changes(self):
        username = self.entries["Username"].get()
        email = self.entries["Email"].get()
        phone = self.entries["Phone Number"].get()
        dob = self.dob_calendar.get_date().strftime("%d/%m/%Y")  # Get date from calendar

        old_pw = self.entries["Old Password"].get()
        new_pw = self.entries["New Password"].get()
        confirm_pw = self.entries["Confirm Password"].get()

        if not self.validate_email(email):
            return
        if not self.validate_phone(phone):
            return
        if not self.validate_dob(dob):
            return

        conn = sqlite3.connect("Trackwise.db")
        cursor = conn.cursor()

        # Get current hashed password
        cursor.execute("SELECT password FROM users WHERE user_id = ?", (self.user_id,))
        result = cursor.fetchone()

        if result is None:
            messagebox.showerror("Error", "User not found.")
            conn.close()
            return

        # Convert stored password string to bytes
        current_hashed_pw = result[0]

        # If changing password
        if old_pw or new_pw or confirm_pw:
            if not (old_pw and new_pw and confirm_pw):
                messagebox.showerror("Error", "Please fill all password fields.")
                conn.close()
                return

            if not bcrypt.checkpw(old_pw.encode(), current_hashed_pw):
                messagebox.showerror("Error", "Old password is incorrect.")
                conn.close()
                return

            if new_pw != confirm_pw:
                messagebox.showerror("Error", "New password and confirmation do not match.")
                conn.close()
                return

            if not self.validate_password(new_pw):
                return

            new_hashed_pw = bcrypt.hashpw(new_pw.encode(), bcrypt.gensalt())
        else:
            new_hashed_pw = current_hashed_pw  # no change

        # Optional photo update
        photo_path = getattr(self, "photo_path", None)

        cursor.execute("""
            UPDATE users
            SET username = ?, email = ?, phone = ?, dob = ?, password = ?, photo_path = ?
            WHERE user_id = ?
        """, (username, email, phone, dob, new_hashed_pw, photo_path, self.user_id))

        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Profile updated successfully.")

        for entry in self.entries.values():
            entry.delete(0, 'end')  # Clear each entry

            # Redirect to profile page or close the window
        self.root.destroy()  # Close the current window
        subprocess.Popen([sys.executable, "profile.py"])

    def cancel_edit(self):
        subprocess.Popen([sys.executable, "profile.py"])
        self.root.destroy()

if __name__ == "__main__":
    user_id = 1  # Replace with the actual logged-in user's ID
    window = ctk.CTk()
    app = EditProfileApp(window, user_id)
    window.mainloop()
