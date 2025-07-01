import sqlite3
from six import BytesIO
import qrcode
import json
import customtkinter as ctk
from tkinter import messagebox, ttk, END
from PIL import Image

class Setup_Database:
    def __init__(self, db_file="Trackwise.db"):
        self.db_file = db_file
        self.initialize_database()

    def initialize_database(self):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS inventory (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            invoice_id TEXT,
                            product_id TEXT,
                            item_name TEXT NOT NULL,
                            category TEXT,
                            quantity INTEGER,
                            price REAL,
                            status TEXT,
                            register_date TEXT
                        )''')
        conn.commit()
        conn.close()

    def view_items(self):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT id, item_name, category, quantity, price, status, register_date FROM inventory")
        rows = cursor.fetchall()
        conn.close()
        return rows

    def delete_item(self, item_id):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM inventory WHERE id = ?", (item_id,))
        conn.commit()
        conn.close()

    def update_item(self, item_id, item_name, category, quantity, price, status, registration_date):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute(
            '''UPDATE inventory SET item_name = ?, 
            category = ?, quantity = ?, price = ?, 
            status = ?, register_date = ? 
            WHERE id = ?''',
            (item_name, category, int(quantity), float(price), status, registration_date, item_id)
        )
        conn.commit()
        conn.close()


class ManageProductPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.width, self.height = 1554, 800

        background_image = ctk.CTkImage(Image.open("Manage_Product.png"), size=(self.width, self.height))
        background_image_label = ctk.CTkLabel(self, image=background_image, text="")
        background_image_label.place(relx=-0.02, rely=0)

        self.create_widgets()
        self.db = Setup_Database()
        self.refresh_table()

    def create_widgets(self):
        # Item Name
        self.name_text = ctk.CTkLabel(self, text="Name:",
                                      font=("Inter", 23),
                                      bg_color="#FFFFFF", fg_color="#FFFFFF",
                                      text_color="black")
        self.name_text.place(x=1370 / 1920 * self.width, y=112 / 974 * self.height)

        self.name = ctk.StringVar()
        self.name_entry = ctk.CTkEntry(self, font=("Inter", 18), width=320 / 1536 * self.width,
                                       height=45 / 864 * self.height, bg_color="#FFFFFF",
                                       fg_color="#D9D9D9", border_color="#FFFFFF", text_color="black",
                                       textvariable=self.name)
        self.name_entry.place(x=1370 / 1920 * self.width, y=152 / 974 * self.height)

        # Category
        self.category_text = ctk.CTkLabel(self, text="Category:",
                                          font=("Inter", 23),
                                          bg_color="#FFFFFF", fg_color="#FFFFFF",
                                          text_color="black")
        self.category_text.place(x=1370 / 1920 * self.width, y=231 / 974 * self.height)

        self.category = ctk.StringVar()
        self.category_entry = ctk.CTkEntry(self, font=("Inter", 18), width=320 / 1536 * self.width,
                                           height=45 / 864 * self.height, bg_color="#FFFFFF",
                                           fg_color="#D9D9D9", border_color="#FFFFFF", text_color="black",
                                           textvariable=self.category)
        self.category_entry.place(x=1370 / 1920 * self.width, y=270 / 974 * self.height)

        # Quantity
        self.quantity_text = ctk.CTkLabel(self, text="Quantity:",
                                          font=("Inter", 23),
                                          bg_color="#FFFFFF", fg_color="#FFFFFF",
                                          text_color="black")
        self.quantity_text.place(x=1370 / 1930 * self.width, y=342 / 974 * self.height)

        self.quantity = ctk.StringVar()
        self.quantity_entry = ctk.CTkEntry(self, font=("Inter", 18), width=320 / 1536 * self.width,
                                           height=45 / 864 * self.height, bg_color="#FFFFFF",
                                           fg_color="#D9D9D9", border_color="#FFFFFF", text_color="black",
                                           textvariable=self.quantity)
        self.quantity_entry.place(x=1370 / 1930 * self.width, y=380 / 974 * self.height)

        # Category
        self.price_text = ctk.CTkLabel(self, text="Price:",
                                       font=("Inter", 23),
                                       bg_color="#FFFFFF", fg_color="#FFFFFF",
                                       text_color="black")
        self.price_text.place(x=1370 / 1930 * self.width, y=450 / 974 * self.height)

        self.price = ctk.StringVar()
        self.price_entry = ctk.CTkEntry(self, font=("Inter", 18), width=320 / 1536 * self.width,
                                        height=45 / 864 * self.height, bg_color="#FFFFFF",
                                        fg_color="#D9D9D9", border_color="#FFFFFF", text_color="black",
                                        textvariable=self.price)
        self.price_entry.place(x=1370 / 1930 * self.width, y=488 / 974 * self.height)

        # Status
        self.status_text = ctk.CTkLabel(self, text="Status:",
                                        font=("Inter", 23),
                                        bg_color="#FFFFFF", fg_color="#FFFFFF",
                                        text_color="black")
        self.status_text.place(x=1370 / 1930 * self.width, y=560 / 974 * self.height)

        self.status = ctk.StringVar()
        self.status_entry = ctk.CTkEntry(self, font=("Inter", 18), width=320 / 1536 * self.width,
                                         height=45 / 864 * self.height, bg_color="#FFFFFF",
                                         fg_color="#D9D9D9", border_color="#FFFFFF", text_color="black",
                                         textvariable=self.status)
        self.status_entry.place(x=1370 / 1930 * self.width, y=600 / 974 * self.height)

        # Registration Date
        self.date_text = ctk.CTkLabel(self, text="Registration Date:",
                                      font=("Inter", 23),
                                      bg_color="#FFFFFF", fg_color="#FFFFFF",
                                      text_color="black")
        self.date_text.place(x=1370 / 1930 * self.width, y=668 / 974 * self.height)

        self.date = ctk.StringVar()
        self.date_entry = ctk.CTkEntry(self, font=("Inter", 18), width=320 / 1536 * self.width,
                                       height=45 / 864 * self.height, bg_color="#FFFFFF",
                                       fg_color="#D9D9D9", border_color="#FFFFFF", text_color="black",
                                       textvariable=self.date)
        self.date_entry.place(x=1370 / 1930 * self.width, y=710 / 974 * self.height)

        # Buttons
        # Back Button
        self.back_button = ctk.CTkButton(self, text="Back", bg_color="#FFFFFF", fg_color="#2A50CB",
                                         text_color="#FFFCFC",
                                         border_color="#1572D3", width=159, height=44,
                                         font=("Inter", 20), command=self.back)
        self.back_button.place(x=113 / 1920 * self.winfo_screenwidth(), y=730 / 974 * self.winfo_screenheight())

        # Update Product Button
        self.update_button = ctk.CTkButton(self, text="Update Product", bg_color="#FFFFFF", fg_color="#2A50CB",
                                           text_color="#FFFCFC",
                                           border_color="#1572D3", width=159, height=44,
                                           font=("Inter", 20), command=self.update_item_handler)
        self.update_button.place(x=632 / 1920 * self.winfo_screenwidth(), y=730 / 974 * self.winfo_screenheight())

        # Delete Product Button
        self.delete_button = ctk.CTkButton(self, text="Delete Product", bg_color="#FFFFFF", fg_color="#2A50CB",
                                           text_color="#FFFCFC",
                                           border_color="#1572D3", width=159, height=44,
                                           font=("Inter", 20), command=self.delete_item_handler)
        self.delete_button.place(x=950 / 1920 * self.winfo_screenwidth(), y=730 / 974 * self.winfo_screenheight())

        # OR CODES
        self.qr_label = ctk.CTkLabel(self, text="QR Code will appear here", bg_color="#FFFFFF", fg_color="#2A50CB",
                                     width=200, height=182)
        self.qr_label.place(x=338 / 1920 * self.width, y=133 / 974 * self.height)

        # Treeview
        self.entries = {
            "Name": self.name_entry,
            "Category": self.category_entry,
            "Quantity": self.quantity_entry,
            "Price": self.price_entry,
            "Status": self.status_entry,
            "Register_Date": self.date_entry
        }

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", font=("Inter", 18), rowheight=80)
        style.configure("Treeview", font=("Inter", 16), rowheight=32)
        frame = ctk.CTkFrame(self)
        frame.place(x=112 / 1920 * self.width, y=345 / 864 * self.height)
        self.product_treeview = ttk.Treeview(frame, columns=("ID", "Name", "Category", "Quantity",
                                                             "Price", "Status", "Register_Date"),
                                             show="headings")
        self.product_treeview.heading("ID", text="ID")
        self.product_treeview.column("ID", width=80, anchor="center")

        self.product_treeview.heading("Name", text="Name")
        self.product_treeview.column("Name", width=180, anchor="center")

        self.product_treeview.heading("Category", text="Category")
        self.product_treeview.column("Category", width=180, anchor="center")

        self.product_treeview.heading("Quantity", text="Quantity")
        self.product_treeview.column("Quantity", width=180, anchor="center")

        self.product_treeview.heading("Price", text="Price")
        self.product_treeview.column("Price", width=170, anchor="center")

        self.product_treeview.heading("Status", text="Status")
        self.product_treeview.column("Status", width=170, anchor="center")

        self.product_treeview.heading("Register_Date", text="Registration Date")
        self.product_treeview.column("Register_Date", width=240, anchor="center")

        self.product_treeview.pack()

        self.product_treeview.bind("<<TreeviewSelect>>", lambda event: self.on_treeview_select())

    def refresh_table(self):
        self.product_treeview.delete(*self.product_treeview.get_children())
        for row in self.db.view_items():
            item_id, item_name, category, quantity, price, status, register_date = row
            if isinstance(quantity, str):
                try:
                    quantity = int(quantity)
                except ValueError:
                    quantity = 0

            status = "Low Stock" if quantity < 5 else "In Stock"
            self.db.update_item(item_id, item_name, category, quantity, price, status, register_date)

            self.product_treeview.insert("", END, values=(item_id, item_name, category, quantity, price, status, register_date))

    def on_treeview_select(self):
        selected = self.product_treeview.selection()
        if selected:
            values = self.product_treeview.item(selected[0], "values")
            for i, key in enumerate(self.entries.keys()):
                self.entries[key].delete(0, END)
                self.entries[key].insert(0, values[i + 1])
            self.generate_qr_code(values)

    def generate_qr_code(self, item_values):
        data = {
            "Item": item_values[1],
            "Category": item_values[2],
            "Quantity": item_values[3],
            "Price": item_values[4],
            "Status": item_values[5],
            "Register Date": item_values[6],
        }
        json_data = json.dumps(data)
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(json_data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="blue", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        qr_img = Image.open(buffer)
        self.qr_img = ctk.CTkImage(light_image=qr_img, dark_image=qr_img, size=(200, 190))
        self.qr_label.configure(image=self.qr_img, text="")

    def update_item_handler(self):
        selected = self.product_treeview.selection()
        if not selected:
            messagebox.showerror("Error", "No item selected!")
            return
        item_id = self.product_treeview.item(selected[0], "values")[0]

        try:
            name = self.entries["Name"].get().strip()
            category = self.entries["Category"].get().strip()
            quantity = int(self.entries["Quantity"].get())
            price = float(self.entries["Price"].get())
            register_date = self.entries["Register_Date"].get().strip()
        except ValueError:
            messagebox.showerror("Error", "Quantity must be integer and price must be numeric!")
            return

        if not name or not category or not register_date:
            messagebox.showerror("Error", "Name, Category, and Registration Date are required.")
            return

        status = "Low Stock" if quantity < 5 else "In Stock"

        self.db.update_item(item_id, name, category, quantity, price, status, register_date)
        self.refresh_table()
        messagebox.showinfo("Success", "Item updated successfully!")

    def delete_item_handler(self):
        selected = self.product_treeview.selection()
        if not selected:
            messagebox.showerror("Error", "No item selected!")
            return
        item_id = self.product_treeview.item(selected[0], "values")[0]
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this?"):
            self.db.delete_item(item_id)
            self.refresh_table()
            messagebox.showinfo("Success", "Item deleted successfully!")

    def search_items(self, query):
        return [row for row in self.db.view_items() if query.lower() in row[1].lower()]

    def back(self):
        self.controller.show_frame("AdminDashboard")
