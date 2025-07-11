import customtkinter as ctk
import sqlite3
from tkinter import messagebox

class AddCategoryWindow(ctk.CTkFrame):
    def __init__(self, parent, on_close_callback=None):
        super().__init__(parent)
        self.on_close_callback = on_close_callback

        screen_width = parent.winfo_screenwidth()
        screen_height = parent.winfo_screenheight()

        # Adjust position to be near the QR image (which is at x ≈ 1499 / 1920 * width)
        x = int(1499 / 1920 * screen_width)  # You can tweak this 1280 value to shift left/right
        y = int(510 / 974 * screen_height)

        self.configure(width=400, height=500, fg_color="#FFFFFF")
        self.configure(corner_radius=0)

        self.place(x=x, y=y)

        self.category_var = ctk.StringVar()
        self.remove_var = ctk.StringVar()

        self.create_widgets()
        self.load_categories()

    def create_widgets(self):
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(expand=True)  # Center within the main frame

        self.label_add = ctk.CTkLabel(content_frame, text="Enter New Category:", font=("Arial", 20))
        self.label_add.pack(pady=(40, 10))

        self.entry_add = ctk.CTkEntry(content_frame, textvariable=self.category_var, font=("Arial", 16),
                                      width=300, placeholder_text="Type new category here")
        self.entry_add.pack(pady=5)

        self.add_button = ctk.CTkButton(content_frame, text="Add Category", command=self.add_category)
        self.add_button.pack(pady=(5, 20))

        self.label_remove = ctk.CTkLabel(content_frame, text="Remove Existing Category:", font=("Arial", 20))
        self.label_remove.pack(pady=(10, 10))

        self.dropdown_remove = ctk.CTkComboBox(content_frame, variable=self.remove_var, values=[], width=300)
        self.dropdown_remove.pack(pady=5)

        self.remove_button = ctk.CTkButton(content_frame, text="Remove Category", fg_color="red",
                                           command=self.remove_category)
        self.remove_button.pack(pady=(5, 20))

        self.back_button = ctk.CTkButton(content_frame, text="Back", fg_color="green", command=self.go_back)
        self.back_button.pack(pady=10)

    def load_categories(self):
        conn = sqlite3.connect('Trackwise.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM categories ORDER BY name")
        categories = [row[0] for row in cursor.fetchall()]
        conn.close()

        self.dropdown_remove.configure(values=categories)
        self.dropdown_remove.set("-- Select Category --")

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
            self.category_var.set("")
            self.load_categories()
        except sqlite3.IntegrityError:
            messagebox.showwarning("Warning", f"Category '{new_category}' already exists.")
        finally:
            conn.close()

    def remove_category(self):
        category_to_remove = self.remove_var.get()
        if not category_to_remove or category_to_remove not in self.dropdown_remove.cget("values"):
            messagebox.showwarning("Warning", "Please select a valid category to remove.")
            return

        conn = sqlite3.connect('Trackwise.db')
        cursor = conn.cursor()
        cursor.execute("SELECT product_id, item_name, quantity FROM inventory WHERE category = ?", (category_to_remove,))
        items = cursor.fetchall()

        for product_id, name, quantity in items:
            if quantity > 0:
                messagebox.showwarning("Warning", f"Cannot delete category. Product '{name}' has remaining stock.")
                conn.close()
                return

        confirm = messagebox.askyesno("Confirm",
                                      f"Are you sure you want to delete category '{category_to_remove}' and all related items?")
        if not confirm:
            conn.close()
            return

        conn = sqlite3.connect('Trackwise.db')
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM inventory WHERE category = ?", (category_to_remove,))
            cursor.execute("DELETE FROM categories WHERE name = ?", (category_to_remove,))
            conn.commit()
            messagebox.showinfo("Success", f"Category '{category_to_remove}' removed.")
            self.remove_var.set("")
            self.load_categories()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            conn.close()

    def go_back(self):
        self.destroy()
        if self.on_close_callback:
            self.on_close_callback()