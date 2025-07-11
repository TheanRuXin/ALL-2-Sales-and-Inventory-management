import os
import sqlite3
import qrcode
import customtkinter as ctk
from tkinter import messagebox, filedialog
from PIL import Image
from datetime import datetime
import random
import string
from AddCategory import AddCategoryWindow
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
import platform
import subprocess

QR_FOLDER ="qrcodes"

def generate_unique_product_id():
    letters = ''.join(random.choices(string.ascii_uppercase, k=5))
    numbers = ''.join(random.choices(string.digits, k=8))
    return f"{letters}{numbers}"

class RegisterProductPage(ctk.CTkFrame):
    def __init__(self,parent,controller):
        super().__init__(parent)
        self.controller = controller
        self.product_image_path = None

        self.width, self.height = 1574, 800

        background_image = ctk.CTkImage(Image.open(r"C:\Users\User\Documents\Ruxin file\ALL 2\Register_Product.png"),  size=(self.width, self.height))
        background_image_label = ctk.CTkLabel(self, image=background_image, text="")
        background_image_label.place(x=0, y=0, relwidth=1, relheight=1)

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
            register_date TEXT NOT NULL,
            product_image BLOB
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
        self.item_text = ctk.CTkLabel(self, text="Item Name:",
                                      font=("Arial", 23),
                                      bg_color="#FFFFFF", fg_color="#FFFFFF",
                                      text_color="black")
        self.item_text.place(x=(210 / 1920 * self.width) - 50, y=215 / 974 * self.height)

        self.item = ctk.StringVar()
        self.item_entry = ctk.CTkEntry(self, font=("Arial", 18), width=395 / 1536 * self.width,
                                       height=45 / 864 * self.height, bg_color="#FFFFFF",
                                       fg_color="#ebf9ff", border_color="#0C5481", text_color="black",
                                       textvariable=self.item)
        self.item_entry.place(x=(205 / 1920 * self.width) - 50, y=255 / 974 * self.height)

        # Category
        self.category_text = ctk.CTkLabel(self, text="Category:",
                                          font=("Arial", 23),
                                          bg_color="#FFFFFF", fg_color="#FFFFFF",
                                          text_color="black")
        self.category_text.place(x=(210 / 1920 * self.width) - 50, y=360 / 974 * self.height)

        self.category = ctk.StringVar()
        self.category_combobox = ctk.CTkComboBox(self, values=self.categories, variable=self.category,
                                                 fg_color="#ebf9ff", border_color="#0C5481",
                                                 button_color="#0C5481", button_hover_color="#52a0bf",
                                                 font=("Arial", 18), width=395, height=45)
        self.category_combobox.place(x=(205 / 1920 * self.width) - 50, y=400 / 974 * self.height)

        self.add_category_link = ctk.CTkLabel(self, bg_color="#FFFFFF", fg_color="#FFFFFF", text="Add a new category",
                                              font=("Arial", 16, "underline"),
                                              text_color="blue", cursor="hand2")
        self.add_category_link.place(x=(205 / 1920 * self.width) - 50, y=470 / 974 * self.height)
        self.add_category_link.bind("<Button-1>", self.open_add_category_window)

        self.quantity_text = ctk.CTkLabel(self, text="Quantity:",
                                          font=("Arial", 23),
                                          bg_color="#FFFFFF", fg_color="#FFFFFF",
                                          text_color="black")
        self.quantity_text.place(x=(210 / 1920 * self.width) - 50, y=508 / 974 * self.height)

        self.quantity = ctk.StringVar()
        self.quantity_entry = ctk.CTkEntry(self, font=("Arial", 18), width=395 / 1536 * self.width,
                                           height=45 / 864 * self.height, bg_color="#FFFFFF",
                                           fg_color="#ebf9ff", border_color="#0C5481", text_color="black",
                                           textvariable=self.quantity)
        self.quantity_entry.place(x=(205 / 1920 * self.width) - 50, y=550 / 974 * self.height)

        # Right Side
        # Price
        self.price_text = ctk.CTkLabel(self, text="Price:",
                                       font=("Arial", 23),
                                       bg_color="#FFFFFF", fg_color="#FFFFFF",
                                       text_color="black")
        self.price_text.place(x=(937 / 1920 * self.width) - 50, y=209 / 974 * self.height)

        self.price = ctk.StringVar()
        self.price_entry = ctk.CTkEntry(self, font=("Arial", 18), width=395 / 1536 * self.width,
                                        height=45 / 864 * self.height, bg_color="#FFFFFF",
                                        fg_color="#ebf9ff", border_color="#0C5481", text_color="black",
                                        textvariable=self.price)
        self.price_entry.place(x=(935 / 1920 * self.width) - 50, y=255 / 974 * self.height)

        # Status
        self.status_text = ctk.CTkLabel(self, text="Status:",
                                        font=("Arial", 23),
                                        bg_color="#FFFFFF", fg_color="#FFFFFF",
                                        text_color="black")
        self.status_text.place(x=(937 / 1920 * self.width) - 50, y=360 / 974 * self.height)

        self.status = ctk.StringVar(value="In Stock")  # Define StringVar

        self.status_label = ctk.CTkEntry(
            self,
            font=("Arial", 18),
            text_color="black",
            width=395 / 1536 * self.width,
            height=45 / 864 * self.height,
            fg_color="#ebf9ff",
            bg_color="#FFFFFF",
            corner_radius=8,
            border_color="#0C5481",
            textvariable=self.status,  # ✅ Use textvariable instead of `text`
            state="disabled"
        )

        self.status_label.place(x=(935 / 1920 * self.width) - 50, y=400 / 974 * self.height)

        self.date_text = ctk.CTkLabel(self, text="Registration Date:",
                                      font=("Arial", 23),
                                      bg_color="#FFFFFF", fg_color="#FFFFFF",
                                      text_color="black")
        self.date_text.place(x=(937 / 1920 * self.width) - 50, y=508 / 974 * self.height)

        self.date = ctk.StringVar(value=datetime.now().strftime("%d-%m-%Y"))
        self.date_entry = ctk.CTkEntry(self, font=("Arial", 18), width=395 / 1536 * self.width,
                                       height=45 / 864 * self.height, bg_color="#FFFFFF",
                                       fg_color="#ebf9ff", border_color="#0C5481", text_color="black",
                                       textvariable=self.date, state="readonly")
        self.date_entry.place(x=(935 / 1920 * self.width) - 50, y=550 / 974 * self.height)

        # Add Product Button
        self.add_button = ctk.CTkButton(self, text="Add Product", bg_color="#FFFFFF", fg_color="#0C5481",
                                        text_color="#FFFCFC",
                                        border_color="#1572D3", width=159, height=44,
                                        font=("Inter", 20), command=self.add_item)
        self.add_button.place(x=(1475 / 1920 * self.winfo_screenwidth()) - 40, y=750 / 974 * self.winfo_screenheight())

        # OR CODES
        self.qr_label = ctk.CTkLabel(self, text="QR Code will appear here", bg_color="#FFFFFF", fg_color="#ebf9ff",
                                     width=197, height=197)
        self.qr_label.place(x=(1499 / 1920 * self.width) - 40, y=500 / 974 * self.height)

        self.product_image_preview = ctk.CTkLabel(self, text="Product Image", bg_color="#FFFFFF",
                                                  fg_color="#ebf9ff",
                                                  width=197, height=197)
        self.product_image_preview.place(x=(1499 / 1920 * self.width) - 40, y=230 / 974 * self.height)

        # Upload Image
        self.product_image_path = None

        self.upload_btn = ctk.CTkButton(self, text="Upload Product Image",
                                        command=self.upload_product_image, bg_color="#FFFFFF",
                                        fg_color="#0C5481", text_color="white", width=200)
        self.upload_btn.place(x=(1499 / 1920 * self.width) - 40, y=150 / 974 * self.height)

        self.form_widgets = [
            self.item_text, self.item_entry,
            self.category_text, self.category_combobox, self.add_category_link,
            self.quantity_text, self.quantity_entry,
            self.price_text, self.price_entry,
            self.date_text, self.date_entry,
            self.status_text, self.status_label
        ]

    def open_add_category_window(self, event=None):
        # Hide only form widgets
        for widget in self.form_widgets:
            widget.place_forget()

        if hasattr(self, 'add_category_frame') and self.add_category_frame:
            self.add_category_frame.destroy()

        self.add_category_frame = AddCategoryWindow(self, on_close_callback=self.restore_product_form)
        self.add_category_frame.place(x=600 / 1920 * self.width,y=250 / 974 * self.height)

    def place_form_widgets(self):
        self.item_text.place(x=(210 / 1920 * self.width) - 50, y=215 / 974 * self.height)
        self.item_entry.place(x=(205 / 1920 * self.width) - 50, y=255 / 974 * self.height)

        self.category_text.place(x=(210 / 1920 * self.width) - 50, y=360 / 974 * self.height)
        self.category_combobox.place(x=(205 / 1920 * self.width) - 50, y=400 / 974 * self.height)
        self.add_category_link.place(x=(205 / 1920 * self.width) - 50, y=470 / 974 * self.height)

        self.quantity_text.place(x=(210 / 1920 * self.width) - 50, y=508 / 974 * self.height)
        self.quantity_entry.place(x=(205 / 1920 * self.width) - 50, y=550 / 974 * self.height)

        self.price_text.place(x=(937 / 1920 * self.width) - 50, y=209 / 974 * self.height)
        self.price_entry.place(x=(935 / 1920 * self.width) - 50, y=255 / 974 * self.height)

        self.status_text.place(x=(937 / 1920 * self.width) - 50, y=360 / 974 * self.height)
        self.status_label.place(x=(935 / 1920 * self.width) - 50, y=400 / 974 * self.height)

        self.date_text.place(x=(937 / 1920 * self.width) - 50, y=508 / 974 * self.height)
        self.date_entry.place(x=(935 / 1920 * self.width) - 50, y=550 / 974 * self.height)

    def restore_product_form(self):
        if hasattr(self, 'add_category_frame') and self.add_category_frame:
            self.add_category_frame.destroy()
            self.add_category_frame = None
        self.place_form_widgets()
        self.refresh_categories()

    def refresh_categories(self):
        conn = sqlite3.connect('Trackwise.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM categories")
        categories = [row[0] for row in cursor.fetchall()]
        conn.close()
        self.category_combobox.configure(values=categories)

    def show_form_fields(self):
        for widget in getattr(self, "widgets", []):
            widget.place(widget.place_info())
        self.refresh_categories()

    def add_item(self):
        item_name = self.item_entry.get().strip()
        item_name = item_name.lower().title()

        # Reject if item name has no letters
        if not any(char.isalpha() for char in item_name):
            messagebox.showerror("Invalid Name", "Item Name Should Not Only Contain Numbers.")
            return
        category = self.category.get().strip()
        quantity = self.quantity_entry.get().strip()
        price = self.price_entry.get().strip()
        status = "In Stock"
        register_date = self.date_entry.get()

        image_data = None
        if self.product_image_path:
            with open(self.product_image_path, 'rb') as f:
                image_data = f.read()

        if not item_name or not category or not quantity or not price or not status:
            messagebox.showerror("Error", "All Fields are required")
            return

        if not self.product_image_path:
            messagebox.showerror("Error", "Please upload a product image before adding the item.")
            return

        try:
            quantity = int(quantity)
            if not (1 <= quantity <= 144):
                messagebox.showerror("Invalid Quantity", "Quantity must be between 1 and 144.\n"
                                                         "Example: 5 or 120")
                return
            status = "Low Stock" if quantity < 5 else "In Stock"
        except ValueError:
            messagebox.showerror("Invalid Quantity", "Quantity must be a whole number.\n"
                                                     "Example: 5 or 120")
            return

        try:
            price = float(price)
        except ValueError:
            messagebox.showerror("Invalid Price", "Price must be a valid number.\n"
                                                  "Example: 0.09 or 250.00")
            return

        conn = sqlite3.connect('Trackwise.db')
        cursor = conn.cursor()

        cursor.execute("SELECT item_name FROM inventory WHERE LOWER(item_name) = LOWER(?)", (item_name,))
        existing_item = cursor.fetchone()
        if existing_item:
            conn.close()
            messagebox.showerror("Duplicate Product", f"'{item_name}' Already Exists.")
            return

        product_id = generate_unique_product_id()

        conn = sqlite3.connect('Trackwise.db')
        cursor = conn.cursor()
        cursor.execute("""
                    INSERT INTO inventory (product_id,item_name, category, quantity, price, status, register_date, product_image)
                    VALUES (?,?, ?, ?, ?, ?, ?, ?)
                    """, (product_id,item_name, category, quantity, price, status, register_date, image_data))
        conn.commit()
        item_id = cursor.lastrowid
        conn.close()

        qr_data = (f"Product ID: {product_id}\n "
                   f"Item ID: {item_id}\n "
                   f"Name: {item_name}\n "
                   f"Category: {category}\n "
                   f"Quantity: {quantity}\n "
                   f"Price: RM{price}\n "
                   f"Status:{status}\n "
                   f"Register Date: {register_date}")

        os.makedirs(QR_FOLDER, exist_ok=True)
        qr_img_path = os.path.join(QR_FOLDER, f"item_{item_id}.png")
        qr_code = qrcode.make(qr_data)
        qr_code.save(qr_img_path)

        qr_display_img = Image.open(qr_img_path)
        qr_tk_img = ctk.CTkImage(light_image=qr_display_img, size=(197, 197))
        self.qr_label.configure(image=qr_tk_img, text="")
        self.qr_label.image = qr_tk_img

        messagebox.showinfo("Success", f"Item added successfully!\n"
                                       f"QR Code saved at {qr_img_path}")
        self.item.set("")
        self.category.set("")
        self.quantity.set("")
        self.price.set("")
        self.status_label.configure(text="")
        self.product_image_path = None
        self.product_image_preview.configure(image=None, text="Product Image")
        self.product_image_preview.image = None
        self.qr_label.configure(image=None, text="QR Code")
        self.qr_label.image = None

    def upload_product_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            self.product_image_path = file_path
            img = Image.open(file_path)
            ctk_img = ctk.CTkImage(light_image=img, size=(197, 197))  # scale small
            self.product_image_preview.configure(image=ctk_img, text="")
            self.product_image_preview.image = ctk_img

    def save_qr_as_pdf(self, qr_img_path, item_id, product_name):
        width, height = 60 * mm, 60 * mm
        pdf_path = os.path.join(QR_FOLDER, f"item_{item_id}.pdf")

        c = canvas.Canvas(pdf_path, pagesize=(width, height))

        # Draw product name as heading
        c.setFont("Helvetica-Bold", 12)
        text_width = c.stringWidth(product_name, "Helvetica-Bold", 12)
        c.drawString((width - text_width) / 2, height - 20, product_name)

        # Draw QR code centered below heading
        qr_size = 40 * mm
        qr_x = (width - qr_size) / 2
        qr_y = (height - 20 - qr_size - 10)
        c.drawImage(qr_img_path, qr_x, qr_y, width=qr_size, height=qr_size)

        c.save()

        messagebox.showinfo("PDF Saved", f"QR Code PDF saved to:\n{pdf_path}")

        # Automatically open the PDF
        try:
            if platform.system() == "Windows":
                os.startfile(pdf_path)
            elif platform.system() == "Users":
                subprocess.call(['open', pdf_path])
            else:
                subprocess.call(['xdg-open', pdf_path])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open PDF:\n{e}")

    def reset_fields(self):
        self.item.set("")
        self.category.set("")
        self.quantity.set("")
        self.price.set("")
        self.status_label.configure(text="In Stock")
        self.date.set(datetime.now().strftime("%d-%m-%Y"))
        self.product_image_path = None
        self.product_image_preview.configure(image=None, text="Product Image")
        self.product_image_preview.image = None

        self.qr_label.configure(image=None, text="QR Code")
        self.qr_label.image = None