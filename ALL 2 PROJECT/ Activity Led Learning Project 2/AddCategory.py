import customtkinter as ctk
import sqlite3
from tkinter import messagebox

class AddCategoryWindow(ctk.CTkToplevel):
    def __init__(self, parent, on_close_callback=None):
        super().__init__(parent)
        self.on_close_callback = on_close_callback
        self.title("Add Category")
        self.geometry("700x400")
        self.configure(fg_color="#FFFFFF")
        self.resizable(False, False)
        self.attributes("-topmost", True)

        self.width, self.height = 700, 400

        self.create_widgets()

    def create_widgets(self):
        # Add Category Section
        self.label_add = ctk.CTkLabel(self, text="Enter New Category:", font=("Arial", 20))
        self.label_add.pack(pady=(20, 5))

        self.category_var = ctk.StringVar()
        self.entry_add = ctk.CTkEntry(
            self,
            textvariable=self.category_var,
            font=("Arial", 16),
            width=300,
            placeholder_text="Type new category here"
        )
        self.entry_add.pack(pady=5)

        self.add_button = ctk.CTkButton(self, text="Add Category", command=self.add_category)
        self.add_button.pack(pady=(5, 15))

        self.entry_add.bind("<Return>", lambda event: self.add_category())

        # Remove Category Section
        self.label_remove = ctk.CTkLabel(self, text="Select Category to Remove:", font=("Arial", 20))
        self.label_remove.pack(pady=(10, 5))

        self.remove_var = ctk.StringVar()
        self.dropdown_remove = ctk.CTkComboBox(
            master=self,
            variable=self.remove_var,
            values=[],  # Will be set later
            width=300,
            font=("Arial", 16),
            text_color="#0882c4",
            fg_color="white",
            border_color="gray",
            border_width=2,
            dropdown_fg_color="#cce7f9",
            dropdown_text_color="#014894",
            dropdown_font=("Inter", 14),
            dropdown_hover_color="#8dc0f7",
            button_color="#0C5481",
            button_hover_color="#2874ed"
        )
        self.dropdown_remove.pack(pady=5)

        self.remove_button = ctk.CTkButton(self, text="Remove Category", fg_color="red", command=self.remove_category)
        self.remove_button.pack(pady=(5, 15))

        self.cancel_button = ctk.CTkButton(self, text="Cancel", fg_color="green", command=self.destroy)
        self.cancel_button.pack(pady=5)

        self.back_button = ctk.CTkButton(self, text="Back", fg_color="#2A50CB", command=self.go_back)
        self.back_button.pack(pady=5)

        self.load_categories()
        self.dropdown_remove.bind("<Return>", lambda event: self.remove_category())

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

        confirm = messagebox.askyesno("Confirm",
                                      f"Are you sure you want to delete category '{category_to_remove}' and all related inventory items?")
        if not confirm:
            return

        conn = sqlite3.connect('Trackwise.db')
        cursor = conn.cursor()

        try:
            # Remove related inventory items first
            cursor.execute("DELETE FROM inventory WHERE category = ?", (category_to_remove,))

            # Then remove from categories table
            cursor.execute("DELETE FROM categories WHERE name = ?", (category_to_remove,))

            conn.commit()
            messagebox.showinfo("Success",
                                f"Category '{category_to_remove}' and all related items were removed successfully!")

            self.remove_var.set("")
            self.dropdown_remove.set("-- Select Category --")
            self.load_categories()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to remove category: {e}")
        finally:
            conn.close()

    def load_categories(self):
        conn = sqlite3.connect('Trackwise.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM categories ORDER BY name")
        categories = [row[0] for row in cursor.fetchall()]
        conn.close()

        self.dropdown_remove.configure(values=categories)
        self.dropdown_remove.set("-- Select Category --")  # Placeholder-like display

    def go_back(self):
        self.destroy()
        if self.on_close_callback:
            self.on_close_callback()