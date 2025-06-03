import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import os


class UserPage:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.new_pass_entry = None
        self.confirm_pass_entry = None
        self.new_email_entry = None
        self.confirm_email_entry = None
        self.load_user_content()

    def load_user_content(self):
        for widget in self.parent_frame.winfo_children():
            widget.destroy()

        container = ctk.CTkFrame(self.parent_frame, fg_color="white", corner_radius=0)
        container.pack(fill="both", expand=True)

        canvas = ctk.CTkCanvas(container, bg="white", highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ctk.CTkScrollbar(container, orientation="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollable_frame = ctk.CTkFrame(canvas, fg_color="white")
        scroll_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        canvas.bind("<Configure>", lambda e: canvas.itemconfig(scroll_window, width=e.width))
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        self.create_user_info_section(scrollable_frame)
        self.create_password_change_section(scrollable_frame)
        self.create_email_change_section(scrollable_frame)

    def create_user_info_section(self, parent):
        info_frame = ctk.CTkFrame(parent, fg_color="#e6f1fb", corner_radius=10)
        info_frame.pack(pady=20, padx=40, fill="x")

        icon_path = os.path.join("images", "user_icon.png")
        if os.path.exists(icon_path):
            user_img = ctk.CTkImage(light_image=Image.open(icon_path), size=(100, 150))
            user_icon = ctk.CTkLabel(info_frame, text="", image=user_img)
            user_icon.grid(row=0, column=0, rowspan=6, padx=20, pady=10)
        else:
            print(f"❌ Image not found: {icon_path}")

        user_info = {
            "ID": ":20098097",
            "Name": "John Doe",
            "Role": "Cashier",
            "Registration Date": "15TH September 2024",
            "Last Login": "17th April 2025"
        }

        for idx, (label, value) in enumerate(user_info.items()):
            ctk.CTkLabel(info_frame, text=f"{label} :", font=("Arial", 14, "bold"), text_color="#003366") \
                .grid(row=idx, column=1, sticky="e", padx=(150, 2), pady=2)
            ctk.CTkLabel(info_frame, text=value, font=("Arial", 14), text_color="#003366") \
                .grid(row=idx, column=2, sticky="w", padx=(2, 20), pady=2)

    def create_password_change_section(self, parent):
        pass_frame = ctk.CTkFrame(parent, fg_color="white")
        pass_frame.pack(pady=20)

        ctk.CTkLabel(pass_frame, text="Enter New Password:", font=("Arial", 14)) \
            .grid(row=0, column=0, sticky="e", padx=10, pady=10)
        self.new_pass_entry = ctk.CTkEntry(pass_frame, show="*")
        self.new_pass_entry.grid(row=0, column=1, padx=10)

        ctk.CTkLabel(pass_frame, text="Confirm Password:", font=("Arial", 14)) \
            .grid(row=1, column=0, sticky="e", padx=10, pady=10)
        self.confirm_pass_entry = ctk.CTkEntry(pass_frame, show="*")
        self.confirm_pass_entry.grid(row=1, column=1, padx=10)

        ctk.CTkButton(parent, text="Change Password", corner_radius=10,
                      fg_color="#003366", hover_color="#005599",
                      font=("Arial", 14, "bold"), command=self.change_password) \
            .pack(pady=10)

    def change_password(self):
        new = self.new_pass_entry.get()
        confirm = self.confirm_pass_entry.get()

        if not new or not confirm:
            messagebox.showerror("Error", "Please fill in both fields.")
        elif new != confirm:
            messagebox.showerror("Error", "Passwords do not match.")
        else:
            messagebox.showinfo("Success", "Password changed successfully!")

    def create_email_change_section(self, parent):
        email_frame = ctk.CTkFrame(parent, fg_color="white")
        email_frame.pack(pady=10)

        ctk.CTkLabel(email_frame, text="Enter New Email:", font=("Arial", 14)) \
            .grid(row=0, column=0, sticky="e", padx=10, pady=10)
        self.new_email_entry = ctk.CTkEntry(email_frame)
        self.new_email_entry.grid(row=0, column=1, padx=10)

        ctk.CTkLabel(email_frame, text="Confirm New Email:", font=("Arial", 14)) \
            .grid(row=1, column=0, sticky="e", padx=10, pady=10)
        self.confirm_email_entry = ctk.CTkEntry(email_frame)
        self.confirm_email_entry.grid(row=1, column=1, padx=10)

        ctk.CTkButton(parent, text="Change Email", corner_radius=10,
                      fg_color="#003366", hover_color="#005599",
                      font=("Arial", 14, "bold"), command=self.change_email) \
            .pack(pady=10)

    def change_email(self):
        new_email = self.new_email_entry.get()
        confirm_email = self.confirm_email_entry.get()

        if not new_email or not confirm_email:
            messagebox.showerror("Error", "Please fill in both email fields.")
        elif new_email != confirm_email:
            messagebox.showerror("Error", "Email addresses do not match.")
        elif "@" not in new_email or "." not in new_email:
            messagebox.showerror("Error", "Invalid email format.")
        else:
            messagebox.showinfo("Success", f"Email changed to {new_email} successfully!")
