import customtkinter as ctk
import sqlite3
import subprocess
from tkinter import messagebox

class AddCategoryWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Add New Category")
        self.root.geometry("500x300")
        self.root.resizable(False, False)

        self.create_widgets()

    def create_widgets(self):
        self.label = ctk.CTkLabel(self.root, text="Enter New Category:", font=("Arial", 20))
        self.label.pack(pady=20)

        self.category_var = ctk.StringVar()
        self.entry = ctk.CTkEntry(self.root, textvariable=self.category_var, font=("Arial", 16), width=300)
        self.entry.pack(pady=10)

        self.add_button = ctk.CTkButton(self.root, text="Add Category", command=self.add_category)
        self.add_button.pack(pady=10)

        # Cancel just closes the window
        self.cancel_button = ctk.CTkButton(self.root, text="Cancel", fg_color="gray", command=self.root.destroy)
        self.cancel_button.pack(pady=5)

        # Back reopens the Register_Product window
        self.back_button = ctk.CTkButton(self.root, text="Back", fg_color="#2A50CB", command=self.go_back)
        self.back_button.pack(pady=5)

    def add_category(self):
        new_category = self.category_var.get().strip()
        if not new_category:
            messagebox.showwarning("Warning", "Category name cannot be empty.")
            return

        conn = sqlite3.connect('Trackwise.db')
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO categories (name) VALUES (?)", (new_category,))
            conn.commit()
            messagebox.showinfo("Success", f"Category '{new_category}' added successfully!")
            self.root.destroy()
        except sqlite3.IntegrityError:
            messagebox.showwarning("Warning", f"Category '{new_category}' already exists.")
        finally:
            conn.close()

    def go_back(self):
        try:
            subprocess.Popen(["python", "Register_Product.py"])
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to go back: {e}")

if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    app = AddCategoryWindow(root)
    root.mainloop()
