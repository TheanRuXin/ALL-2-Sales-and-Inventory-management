import os
import sqlite3
import qrcode
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk
from datetime import datetime
import random
import string
from AddCategory import AddCategoryWindow

QR_FOLDER ="qrcodes"

def generate_unique_product_id():
    letters = ''.join(random.choices(string.ascii_uppercase, k=5))
    numbers = ''.join(random.choices(string.digits, k=8))
    return f"{letters}{numbers}"

class RegisterProductPage(ctk.CTkFrame):
    def __init__(self,parent,controller):
        super().__init__(parent)
        self.controller = controller

        self.width, self.height = 1554, 800

        background_image = ctk.CTkImage(Image.open(r"Register_Product.png"),  size=(self.width, self.height))
        background_image_label = ctk.CTkLabel(self, image=background_image, text="")
        background_image_label.place(relx=-0.02, rely=0)

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
            product_id TEXT UNIQUE,
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
        #Left Side
        #Item Name
        self.item_text = ctk.CTkLabel(self, text="Item Name:",
                                    font=("Arial",23),
                                    bg_color="#FFFFFF", fg_color="#FFFFFF",
                                    text_color="black")
        self.item_text.place(x=210 / 1920 * self.width, y=215 / 974 * self.height)

        self.item = ctk.StringVar()
        self.item_entry = ctk.CTkEntry(self, font=("Arial",18), width=395 / 1536 * self.width,
                                   height=45 / 864 * self.height, bg_color="#FFFFFF",
                                   fg_color="#D9D9D9", border_color="#FFFFFF", text_color="black",
                                   textvariable=self.item)
        self.item_entry.place(x=205 / 1920 * self.width, y=255 / 974 * self.height)

        #Category
        self.category_text = ctk.CTkLabel(self, text="Category:",
                                    font=("Arial",23),
                                    bg_color="#FFFFFF", fg_color="#FFFFFF",
                                    text_color="black")
        self.category_text.place(x=210 / 1920 * self.width, y=360 / 974 * self.height)

        self.category = ctk.StringVar()
        self.category_combobox = ctk.CTkComboBox(self, values=self.categories, variable=self.category,
                                                 font=("Arial", 18), width=395, height=45)
        self.category_combobox.place(x=205 / 1920 * self.width, y=400 / 974 * self.height)

        self.add_category_link = ctk.CTkLabel(self, text="Add a new category", font=("Arial", 16, "underline"),
                                              text_color="blue", cursor="hand2")
        self.add_category_link.place(x=205 / 1920 * self.width, y=470 / 974 * self.height)
        self.add_category_link.bind("<Button-1>", self.open_add_category_window)

        self.quantity_text = ctk.CTkLabel(self, text="Quantity:",
                                    font=("Arial",23),
                                    bg_color="#FFFFFF", fg_color="#FFFFFF",
                                    text_color="black")
        self.quantity_text.place(x=210 / 1920 * self.width, y=508 / 974 * self.height)

        self.quantity = ctk.StringVar()
        self.quantity_entry = ctk.CTkEntry(self, font=("Arial",18), width=395 / 1536 * self.width,
                                   height=45 / 864 * self.height, bg_color="#FFFFFF",
                                   fg_color="#D9D9D9", border_color="#FFFFFF", text_color="black",
                                   textvariable=self.quantity)
        self.quantity_entry.place(x=205 / 1920 * self.width, y=550 / 974 * self.height)

        #Right Side
        #Price
        self.price_text = ctk.CTkLabel(self, text="Price:",
                                      font=("Arial", 23),
                                      bg_color="#FFFFFF", fg_color="#FFFFFF",
                                      text_color="black")
        self.price_text.place(x=937 / 1920 * self.width, y=209 / 974 * self.height)

        self.price = ctk.StringVar()
        self.price_entry = ctk.CTkEntry(self, font=("Arial", 18), width=395 / 1536 * self.width,
                                       height=45 / 864 * self.height, bg_color="#FFFFFF",
                                       fg_color="#D9D9D9", border_color="#FFFFFF", text_color="black",
                                       textvariable=self.price)
        self.price_entry.place(x=935 / 1920 * self.width, y=255 / 974 * self.height)

        #Status
        self.status_text = ctk.CTkLabel(self, text="Status:",
                                          font=("Arial", 23),
                                          bg_color="#FFFFFF", fg_color="#FFFFFF",
                                          text_color="black")
        self.status_text.place(x=937 / 1920 * self.width, y=360 / 974 * self.height)

        self.status = ctk.StringVar()
        self.status_entry = ctk.CTkEntry(self, font=("Arial", 18), width=395 / 1536 * self.width,
                                           height=45 / 864 * self.height, bg_color="#FFFFFF",
                                           fg_color="#D9D9D9", border_color="#FFFFFF", text_color="black",
                                           textvariable=self.status)
        self.status_entry.place(x=935 / 1920 * self.width, y=400 / 974 * self.height)

        #Registration Date
        self.date_text = ctk.CTkLabel(self, text="Registration Date:",
                                          font=("Arial", 23),
                                          bg_color="#FFFFFF", fg_color="#FFFFFF",
                                          text_color="black")
        self.date_text.place(x=937 / 1920 * self.width, y=508 / 974 * self.height)

        self.date = ctk.StringVar(value= datetime.now().strftime("%d-%m-%Y"))
        self.date_entry = ctk.CTkEntry(self, font=("Arial", 18), width=395 / 1536 * self.width,
                                           height=45 / 864 * self.height, bg_color="#FFFFFF",
                                           fg_color="#D9D9D9", border_color="#FFFFFF", text_color="black",
                                           textvariable=self.date, state="readonly")
        self.date_entry.place(x=935 / 1920 * self.width, y=550 / 974 * self.height)

        #Back Button
        self.back_button = ctk.CTkButton(self, text="Back", bg_color="#FFFFFF", fg_color="#2A50CB",
                                       text_color="#FFFCFC",
                                       border_color="#1572D3", width=159, height=44,
                                       font=("Inter", 20), command=self.go_back)
        self.back_button.place(x=113 / 1920 * self.winfo_screenwidth(), y=730 / 974 * self.winfo_screenheight())

        #Add Product Button
        self.add_button = ctk.CTkButton(self, text="Add Product", bg_color="#FFFFFF", fg_color="#2A50CB",
                                         text_color="#FFFCFC",
                                         border_color="#1572D3", width=159, height=44,
                                         font=("Inter", 20), command=self.add_item)
        self.add_button.place(x=1526 / 1920 * self.winfo_screenwidth(), y=730 / 974 * self.winfo_screenheight())

        #OR CODES
        self.qr_label = ctk.CTkLabel(self, text="QR Code will appear here", bg_color="#FFFFFF", fg_color="#2A50CB",
                                     width=197, height=197)
        self.qr_label.place(x=1499 / 1920 * self.width, y=280 / 974 * self.height)

    def open_add_category_window(self, event=None):
        def refresh_and_reload():
            self.load_categories()
            self.category_combobox.configure(values=self.categories)
            if self.categories:
                self.category_combobox.set(self.categories[0])

        AddCategoryWindow(self, on_close_callback=refresh_and_reload)

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
            messagebox.showerror("Error", "Quantitiy must be integer and Price must be a number.")
            return

        conn = sqlite3.connect('Trackwise.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inventory WHERE item_name = ?", (item_name,))
        if cursor.fetchone():
            messagebox.showerror("Error", f"Item '{item_name}' already exists in inventory.")
            conn.close()
            return

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
        item_id = cursor.lastrowid
        conn.close()

        qr_data = (f"Item ID: {item_id}\n Name: {item_name}\n Category: {category}\n "
                   f"Quantity: {quantity}\n Price: RM{price}\n Status:{status}\n Register Date: {register_date}")

        os.makedirs(QR_FOLDER, exist_ok=True)
        qr_img_path = os.path.join(QR_FOLDER, f"item_{item_id}.png")
        qr_code = qrcode.make(qr_data)
        qr_code.save(qr_img_path)

        qr_display_img = Image.open(qr_img_path).resize((297, 297))
        qr_tk_img = ImageTk.PhotoImage(qr_display_img)
        self.qr_label.configure(image=qr_tk_img, text="")
        self.qr_label.image = qr_tk_img

        messagebox.showinfo("Success", f"Item added successfully!\n"
                                       f"QR Code saved at {qr_img_path}")

    def go_back(self):
        self.controller.show_frame("AdminDashboard")