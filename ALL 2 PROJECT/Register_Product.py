import os
import sqlite3
import qrcode
import customtkinter as ctk
from PIL import Image, ImageTk
from tkinter import messagebox
from datetime import datetime
import subprocess
import random
import string

QR_FOLDER = "qrcodes"

def generate_unique_product_id():
    letters = ''.join(random.choices(string.ascii_uppercase, k=5))
    numbers = ''.join(random.choices(string.digits, k=8))
    return f"{letters}{numbers}"

class Manager_Login:
    def __init__(self, root):
        self.root = root
        self.root.title("Inventory Management System")
        self.root.geometry("1920x974")

        self.width = self.root.winfo_screenwidth()
        self.height = self.root.winfo_screenheight()

        background_image = ctk.CTkImage(Image.open("Register_Product.png"), size=(self.width, self.height - 71))
        background_image_label = ctk.CTkLabel(self.root, image=background_image, text="")
        background_image_label.place(relx=0, rely=0)

        self.categories = []
        self.initialize_database()
        self.load_categories()
        self.create_widgets()

    def initialize_database(self):
        conn = sqlite3.connect('Trackwise.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id TEXT,
            item_name TEXT NOT NULL,
            category TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            status TEXT NOT NULL,
            register_date TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

    def load_categories(self):
        conn = sqlite3.connect('Trackwise.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM categories")
        self.categories = [row[0] for row in cursor.fetchall()]
        conn.close()

    def create_widgets(self):
        self.item_text = ctk.CTkLabel(self.root, text="Item Name:", font=("Arial",23), bg_color="#FFFFFF", fg_color="#FFFFFF", text_color="black")
        self.item_text.place(x=210 / 1920 * self.width, y=215 / 974 * self.height)

        self.item = ctk.StringVar()
        self.item_entry = ctk.CTkEntry(self.root, font=("Arial",18), width=395 / 1536 * self.width, height=45 / 864 * self.height, bg_color="#FFFFFF", fg_color="#D9D9D9", border_color="#FFFFFF", text_color="black", textvariable=self.item)
        self.item_entry.place(x=205 / 1920 * self.width, y=255 / 974 * self.height)

        self.category_text = ctk.CTkLabel(self.root, text="Category:", font=("Arial",23), bg_color="#FFFFFF", fg_color="#FFFFFF", text_color="black")
        self.category_text.place(x=210 / 1920 * self.width, y=360 / 974 * self.height)

        self.category = ctk.StringVar()
        self.category_combobox = ctk.CTkComboBox(self.root, values=self.categories, variable=self.category, font=("Arial", 18), width=395 / 1536 * self.width, height=45 / 864 * self.height, bg_color="#FFFFFF", fg_color="#D9D9D9")
        self.category_combobox.place(x=205 / 1920 * self.width, y=400 / 974 * self.height)

        # 🔗 Replaced Add Category input with a link
        self.add_category_link = ctk.CTkLabel(
            self.root,
            text="Add a new category",
            font=("Arial", 16, "underline"),
            text_color="blue",
            cursor="hand2"
        )
        self.add_category_link.place(x=205 / 1920 * self.width, y=470 / 974 * self.height)
        self.add_category_link.bind("<Button-1>", self.open_add_category_window)

        self.quantity_text = ctk.CTkLabel(self.root, text="Quantity:", font=("Arial",23), bg_color="#FFFFFF", fg_color="#FFFFFF", text_color="black")
        self.quantity_text.place(x=210 / 1920 * self.width, y=524 / 974 * self.height)

        self.quantity = ctk.StringVar()
        self.quantity_entry = ctk.CTkEntry(self.root, font=("Arial",18), width=395 / 1536 * self.width, height=45 / 864 * self.height, bg_color="#FFFFFF", fg_color="#D9D9D9", border_color="#FFFFFF", text_color="black", textvariable=self.quantity)
        self.quantity_entry.place(x=205 / 1920 * self.width, y=560 / 974 * self.height)

        self.price_text = ctk.CTkLabel(self.root, text="Price:", font=("Arial", 23), bg_color="#FFFFFF", fg_color="#FFFFFF", text_color="black")
        self.price_text.place(x=937 / 1920 * self.width, y=209 / 974 * self.height)

        self.price = ctk.StringVar()
        self.price_entry = ctk.CTkEntry(self.root, font=("Arial", 18), width=395 / 1536 * self.width, height=45 / 864 * self.height, bg_color="#FFFFFF", fg_color="#D9D9D9", border_color="#FFFFFF", text_color="black", textvariable=self.price)
        self.price_entry.place(x=935 / 1920 * self.width, y=255 / 974 * self.height)

        self.status_text = ctk.CTkLabel(self.root, text="Status:", font=("Arial", 23), bg_color="#FFFFFF", fg_color="#FFFFFF", text_color="black")
        self.status_text.place(x=937 / 1920 * self.width, y=360 / 974 * self.height)

        self.status = ctk.StringVar()
        self.status_entry = ctk.CTkEntry(self.root, font=("Arial", 18), width=395 / 1536 * self.width, height=45 / 864 * self.height, bg_color="#FFFFFF", fg_color="#D9D9D9", border_color="#FFFFFF", text_color="black", textvariable=self.status)
        self.status_entry.place(x=935 / 1920 * self.width, y=400 / 974 * self.height)

        self.date_text = ctk.CTkLabel(self.root, text="Registration Date:", font=("Arial", 23), bg_color="#FFFFFF", fg_color="#FFFFFF", text_color="black")
        self.date_text.place(x=937 / 1920 * self.width, y=508 / 974 * self.height)

        self.date = ctk.StringVar(value= datetime.now().strftime("%d-%m-%Y"))
        self.date_entry = ctk.CTkEntry(self.root, font=("Arial", 18), width=395 / 1536 * self.width, height=45 / 864 * self.height, bg_color="#FFFFFF", fg_color="#D9D9D9", border_color="#FFFFFF", text_color="black", textvariable=self.date, state="readonly")
        self.date_entry.place(x=935 / 1920 * self.width, y=550 / 974 * self.height)

        self.back_button = ctk.CTkButton(self.root, text="Back", bg_color="#FFFFFF", fg_color="#2A50CB", text_color="#FFFCFC", border_color="#1572D3", width=159, height=44, font=("Inter", 20), command=self.go_back)
        self.back_button.place(x=113 / 1920 * self.width, y=730 / 974 * self.height)

        self.add_button = ctk.CTkButton(self.root, text="Add Product", bg_color="#FFFFFF", fg_color="#2A50CB", text_color="#FFFCFC", border_color="#1572D3", width=159, height=44, font=("Inter", 20), command=self.add_item)
        self.add_button.place(x=1526 / 1920 * self.width, y=730 / 974 * self.height)

        self.qr_label = ctk.CTkLabel(self.root, text="QR Code will appear here", bg_color="#FFFFFF", fg_color="#2A50CB", width=197, height=197)
        self.qr_label.place(x=1499 / 1920 * self.width, y=280 / 974 * self.height)

    def open_add_category_window(self, event=None):
        try:
            subprocess.Popen(["python", "AddCategory.py"])  # Ensure AddCategory.py exists
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Add Category window: {e}")

    def add_item(self):
        item_name = self.item_entry.get().strip()
        category = self.category.get().strip()
        quantity = self.quantity_entry.get().strip()
        price = self.price_entry.get().strip()
        status = self.status_entry.get().strip()
        register_date = self.date_entry.get()

        if not item_name or not category or not quantity or not price or not status:
            messagebox.showerror("Error", "All Fields are required")
            return

        try:
            quantity = int(quantity)
            price = float(price)
        except ValueError:
            messagebox.showerror("Error", "Quantity must be integer and Price must be a number.")
            return

        conn = sqlite3.connect('Trackwise.db')
        cursor = conn.cursor()

        while True:
            product_id = generate_unique_product_id()
            cursor.execute("SELECT 1 FROM inventory WHERE product_id = ?", (product_id,))
            if not cursor.fetchone():
                break

        cursor.execute("""
            INSERT INTO inventory (product_id, item_name, category, quantity, price, status, register_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (product_id, item_name, category, quantity, price, status, register_date))
        conn.commit()
        conn.close()

        qr_data = (f"Product ID: {product_id}\nName: {item_name}\nCategory: {category}\n"
                   f"Quantity: {quantity}\nPrice: RM{price}\nStatus: {status}\nRegister Date: {register_date}")

        os.makedirs(QR_FOLDER, exist_ok=True)
        qr_img_path = os.path.join(QR_FOLDER, f"{product_id}.png")
        qr_code = qrcode.make(qr_data)
        qr_code.save(qr_img_path)

        qr_display_img = Image.open(qr_img_path).resize((297, 297))
        qr_tk_img = ImageTk.PhotoImage(qr_display_img)
        self.qr_label.configure(image=qr_tk_img, text="")
        self.qr_label.image = qr_tk_img

        messagebox.showinfo("Success", f"Item added successfully!\nQR Code saved at {qr_img_path}")

    def go_back(self):
        try:
            subprocess.Popen(["python", "Admin_Dashboard.py"])
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Admin Dashboard: {e}")

if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    app = Manager_Login(root)
    root.mainloop()
