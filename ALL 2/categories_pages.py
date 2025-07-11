import customtkinter as ctk
import sqlite3
from tkinter import ttk, messagebox

class CategoriesPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.configure(fg_color="white")

        self.style = ttk.Style()
        self.style.theme_use("default")
        self.blinking_started = False

        # Change selected row background and foreground color
        self.style.map("Treeview",
            background=[('selected', '#3399FF')],
            foreground=[('selected', 'white')]
        )

        self.create_widgets()
        self.load_category_data()

    def create_widgets(self):
        # Search Label
        self.search_label = ctk.CTkLabel(self, text="Search:", text_color="black")
        self.search_label.place(x=50, y=20)

        # Search Entry
        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(self, textvariable=self.search_var, width=300)
        self.search_entry.place(x=110, y=20)
        self.search_entry.bind("<Return>", lambda event: self.search_data())

        # Search Button
        self.search_button = ctk.CTkButton(self, text="Search", command=self.search_data)
        self.search_button.place(x=430, y=20)

        self.search_entry.bind("<Return>", lambda event: self.search_data())
        # Reset Button
        self.reset_button = ctk.CTkButton(self, text="Reset", command=self.load_category_data)
        self.reset_button.place(x=580, y=20)

        # Treeview
        columns = ("product_id", "item_name", "category", "quantity", "price", "status", "register_date")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=20)

        # Headings
        self.tree.heading("product_id", text="Product ID")
        self.tree.heading("item_name", text="Item Name")
        self.tree.heading("category", text="Category")
        self.tree.heading("quantity", text="Quantity")
        self.tree.heading("price", text="Price (RM)")
        self.tree.heading("status", text="Status")
        self.tree.heading("register_date", text="Register Date")

        # Column widths
        self.tree.column("product_id", width=160, anchor="w")
        self.tree.column("item_name", width=160, anchor="w")
        self.tree.column("category", width=160, anchor="w")
        self.tree.column("quantity", width=100, anchor="w")
        self.tree.column("price", width=100, anchor="w")
        self.tree.column("status", width=160, anchor="w")
        self.tree.column("register_date", width=160, anchor="w")

        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        self.tree.place(x=50, y=70, width=1500, height=800)
        self.scrollbar.place(x=1550, y=70, height=800)

    def load_category_data(self):
        # Clear tree
        for row in self.tree.get_children():
            self.tree.delete(row)

        conn = sqlite3.connect("Trackwise.db")
        cursor = conn.cursor()
        cursor.execute("SELECT product_id, item_name, category, quantity, price, status, register_date FROM inventory")
        rows = cursor.fetchall()
        conn.close()

        self.low_stock_items = []

        for row in rows:
            product_id, item_name, category, quantity, price, status, register_date = row
            formatted_price = f"RM {price:.2f}"

            tags = ()
            if quantity < 5:
                tags = ("low_stock",)
                self.low_stock_items.append(product_id)

            self.tree.insert("", "end", values=(
                product_id, item_name, category, quantity,
                formatted_price, status, register_date), tags=tags)

        self.all_data = rows  # Store for search

        self.tree.tag_configure("low_stock", background="white")

        if not self.blinking_started:
            self.blink_state = True
            self.blinking_started = True
            self.blink_low_stock_rows()

    def search_data(self):
        query = self.search_var.get().lower()

        # Clear tree
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Filter rows
        for row in self.all_data:
            product_id, item_name, category, quantity, price, status, register_date = row
            formatted_price = f"RM {price:.2f}"

            row_values = [
                str(product_id), item_name, category, str(quantity),
                formatted_price, status, register_date
            ]
            combined = " ".join(row_values).lower()

            if query in combined:
                tags = ("low_stock",) if quantity < 5 else ()
                self.tree.insert("", "end", values=(
                    product_id, item_name, category, quantity,
                    formatted_price, status, register_date), tags=tags)

    def blink_low_stock_rows(self):
        color = "red" if self.blink_state else "white"
        self.tree.tag_configure("low_stock", background=color)
        self.blink_state = not self.blink_state
        self.after(500, self.blink_low_stock_rows)