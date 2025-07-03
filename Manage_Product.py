import sqlite3
from six import BytesIO
import qrcode
import json
import customtkinter as ctk
from tkinter import messagebox, ttk, END
from PIL import Image
from tkinter import filedialog

class Setup_Database:
    def __init__(self, db_file= "Trackwise.db"):
        self.db_file = db_file
        self.initialize_database()

    def initialize_database(self):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS inventory (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            item_name TEXT NOT NULL,
                            category TEXT,
                            quantity INTEGER,
                            price REAL,
                            status TEXT,
                            register_date TEXT,
                            product_image BLOB
                            )
                        ''')
        conn.commit()
        conn.close()

    def view_items(self):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inventory")
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
            category = ?,
            quantity = ?,
            price = ?,
            status = ?,
            register_date = ?
            WHERE id = ?''',
            (item_name, category, int(quantity),
             float(price), status, registration_date, item_id)
        )
        conn.commit()
        conn.close()

class Manage_Product:
    def __init__(self,root):
        self.root = root
        self.root.title("View Product Details (Admin)")
        self.root.geometry("1920x974")

        self.width = self.root.winfo_screenwidth()
        self.height = self.root.winfo_screenheight()

        background_image = ctk.CTkImage(Image.open("assets/Manage_Product.png"), size=(self.width, self.height - 71))
        background_image_label = ctk.CTkLabel(self.root, image=background_image, text="")
        background_image_label.place(relx=0, rely=0)

        self.create_widgets()
        self.db = Setup_Database()
        self.refresh_table()

    def create_widgets(self):
        # Item Name
        self.name_text = ctk.CTkLabel(self.root, text="Name:",
                                      font=("Inter", 23),
                                      bg_color="#FFFFFF", fg_color="#FFFFFF",
                                      text_color="black")
        self.name_text.place(x=1386 / 1920 * self.width, y=112 / 974 * self.height)

        self.name = ctk.StringVar()
        self.name_entry = ctk.CTkEntry(self.root, font=("Inter", 18), width=320 / 1536 * self.width,
                                       height=45 / 864 * self.height, bg_color="#FFFFFF",
                                       fg_color="#D9D9D9", border_color="#FFFFFF", text_color="black",
                                       textvariable=self.name)
        self.name_entry.place(x=1386 / 1920 * self.width, y=152 / 974 * self.height)

        #Category
        self.category_text = ctk.CTkLabel(self.root, text="Category:",
                                       font=("Inter", 23),
                                       bg_color="#FFFFFF", fg_color="#FFFFFF",
                                       text_color="black")
        self.category_text.place(x=1386 / 1920 * self.width, y=231 / 974 * self.height)

        self.category = ctk.StringVar()
        self.category_entry = ctk.CTkEntry(self.root, font=("Inter", 18), width=320 / 1536 * self.width,
                                        height=45 / 864 * self.height, bg_color="#FFFFFF",
                                        fg_color="#D9D9D9", border_color="#FFFFFF", text_color="black",
                                        textvariable=self.category)
        self.category_entry.place(x=1386 / 1920 * self.width, y=270 / 974 * self.height)

        # Quantity
        self.quantity_text = ctk.CTkLabel(self.root, text="Quantity:",
                                          font=("Inter", 23),
                                          bg_color="#FFFFFF", fg_color="#FFFFFF",
                                          text_color="black")
        self.quantity_text.place(x=1386 / 1920 * self.width, y=342 / 974 * self.height)

        self.quantity = ctk.StringVar()
        self.quantity_entry = ctk.CTkEntry(self.root, font=("Inter", 18), width=320 / 1536 * self.width,
                                           height=45 / 864 * self.height, bg_color="#FFFFFF",
                                           fg_color="#D9D9D9", border_color="#FFFFFF", text_color="black",
                                           textvariable=self.quantity)
        self.quantity_entry.place(x=1386 / 1920 * self.width, y=380 / 974 * self.height)

        # Price
        self.price_text = ctk.CTkLabel(self.root, text="Price:",
                                        font=("Inter", 23),
                                        bg_color="#FFFFFF", fg_color="#FFFFFF",
                                        text_color="black")
        self.price_text.place(x=1386 / 1920 * self.width, y=450 / 974 * self.height)

        self.price = ctk.StringVar()
        self.price_entry = ctk.CTkEntry(self.root, font=("Inter", 18), width=320 / 1536 * self.width,
                                         height=45 / 864 * self.height, bg_color="#FFFFFF",
                                         fg_color="#D9D9D9", border_color="#FFFFFF", text_color="black",
                                         textvariable=self.price)
        self.price_entry.place(x=1386 / 1920 * self.width, y=488 / 974 * self.height)

        #Status
        self.status_text = ctk.CTkLabel(self.root, text="Status:",
                                          font=("Inter", 23),
                                          bg_color="#FFFFFF", fg_color="#FFFFFF",
                                          text_color="black")
        self.status_text.place(x=1386 / 1920 * self.width, y=560 / 974 * self.height)

        self.status = ctk.StringVar()
        self.status_entry = ctk.CTkEntry(self.root, font=("Inter", 18), width=320 / 1536 * self.width,
                                           height=45 / 864 * self.height, bg_color="#FFFFFF",
                                           fg_color="#D9D9D9", border_color="#FFFFFF", text_color="black",
                                           textvariable=self.status)
        self.status_entry.place(x=1386 / 1920 * self.width, y=600 / 974 * self.height)

        # Registration Date
        self.date_text = ctk.CTkLabel(self.root, text="Registration Date:",
                                      font=("Inter", 23),
                                      bg_color="#FFFFFF", fg_color="#FFFFFF",
                                      text_color="black")
        self.date_text.place(x=1386 / 1920 * self.width, y=668 / 974 * self.height)

        self.date = ctk.StringVar()
        self.date_entry = ctk.CTkEntry(self.root, font=("Inter", 18), width=320 / 1536 * self.width,
                                       height=45 / 864 * self.height, bg_color="#FFFFFF",
                                       fg_color="#D9D9D9", border_color="#FFFFFF", text_color="black",
                                       textvariable=self.date)
        self.date_entry.place(x=1386 / 1920 * self.width, y=710 / 974 * self.height)

        #Buttons
        # Back Button
        self.back_button = ctk.CTkButton(root, text="Back", bg_color="#FFFFFF", fg_color="#2A50CB",
                                         text_color="#FFFCFC",
                                         border_color="#1572D3", width=159, height=44,
                                         font=("Inter", 20))
        self.back_button.place(x=113 / 1920 * root.winfo_screenwidth(), y=730 / 974 * root.winfo_screenheight())

        # Update Product Button
        self.update_button = ctk.CTkButton(root, text="Update Product", bg_color="#FFFFFF", fg_color="#2A50CB",
                                        text_color="#FFFCFC",
                                        border_color="#1572D3", width=159, height=44,
                                        font=("Inter", 20), command=self.update_item_handler)
        self.update_button.place(x=632 / 1920 * root.winfo_screenwidth(), y=730 / 974 * root.winfo_screenheight())

        # Delete Product Button
        self.delete_button = ctk.CTkButton(root, text="Delete Product", bg_color="#FFFFFF", fg_color="#2A50CB",
                                         text_color="#FFFCFC",
                                         border_color="#1572D3", width=159, height=44,
                                         font=("Inter", 20), command=self.delete_item_handler)
        self.delete_button.place(x=950 / 1920 * root.winfo_screenwidth(), y=730 / 974 * root.winfo_screenheight())

        # Change Image Button
        self.change_image_button = ctk.CTkButton(self.root, text="Change Image",
                                                 font=("Inter", 16),
                                                 width=150, height=40,
                                                 bg_color="#FFFFFF", fg_color="#2A50CB",
                                                 text_color="#FFFCFC",
                                                 border_color="#1572D3",
                                                 command=self.change_product_image)
        self.change_image_button.place(x=900 / 1920 * self.width, y=170 / 864 * self.height)

        # Search Box
        self.search_label = ctk.CTkLabel(self.root, text="Search Product:",
                                         font=("Inter", 20),
                                         bg_color="#FFFFFF", fg_color="#FFFFFF",
                                         text_color="black")
        self.search_label.place(x=800 / 1920 * self.width, y=245 / 864 * self.height)

        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(self.root, textvariable=self.search_var,
                                         width=320 / 1536 * self.width,
                                         height=45 / 864 * self.height,
                                         bg_color = "#FFFFFF",
                                         fg_color = "#D9D9D9", border_color = "#FFFFFF",
                                         text_color = "black",
                                         font=("Inter", 16))
        self.search_entry.place(x=800 / 1920 * self.width, y=280 / 864 * self.height)

        self.search_entry.bind("<KeyRelease>", lambda e: self.search_items(self.search_var.get()))

        # OR CODES
        self.qr_label = ctk.CTkLabel(self.root, text="QR Code will Appear Here", bg_color="#FFFFFF", fg_color="#2A50CB",
                                     width=200, height=182)
        self.qr_label.place(x=458 / 1920 * self.width, y=133 / 974 * self.height)

        # Product Image Label
        self.product_image_label = ctk.CTkLabel(self.root, text="Product Image Will Appear Here", bg_color="#FFFFFF",
                                                fg_color="#2A50CB", width=200, height=182)
        self.product_image_label.place(x=130 / 1920 * self.width, y=133 / 974 * self.height)

        #Treeview
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
        style.configure("Treeview.Heading", font= ("Inter", 18), rowheight=80)
        style.configure("Treeview", font=("Inter",16), rowheight=32)
        frame = ctk.CTkFrame(self.root)
        frame.place(x=112 / 1920 * self.width, y=345/ 864 * self.height)
        self.product_treeview = ttk.Treeview(frame, columns=("ID", "Name", "Category", "Quantity",
                                                             "Price", "Status", "Register_Date"),
                                             show = "headings")
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
        for row in self.product_treeview.get_children():
            self.product_treeview.delete(row)

        for row in self.db.view_items():
            item_id, item_name, category, quantity, price, status, register_date, image_data = row

            #Update Status based on the quantity
            if quantity < 5:
                status = "Low Stock"
            else:
                status = "In Stock"

            # Save updated status in the database
            self.db.update_item(item_id, item_name, category, quantity, price, status, register_date)

            stock_colour = 'Red' if quantity < 5 else 'Green'
            self.product_treeview.insert("", END, values=(item_id, item_name,
                                                          category, quantity, price,
                                                          status, register_date), tags=(stock_colour,))

    def on_treeview_select(self):
        selected_item = self.product_treeview.selection()
        if selected_item:
            values = self.product_treeview.item(selected_item, "values")
            for i, key in enumerate(self.entries.keys()):
                self.entries[key].delete(0, END)
                self.entries[key].insert(0, values[i + 1])

            self.generate_qr_code(values)

            # Get image from DB using ID
            item_id = values[0]
            conn = sqlite3.connect(self.db.db_file)
            cursor = conn.cursor()
            cursor.execute("SELECT product_image FROM inventory WHERE id = ?", (item_id,))
            result = cursor.fetchone()
            conn.close()

            # Reset image reference first
            self.product_image_label.configure(image=None, text="Product Image Here", fg_color="#2A50CB")

            if result and result[0]:
                try:
                    image_data = result[0]
                    image = Image.open(BytesIO(image_data)).convert("RGBA")
                    image = image.resize((200, 190))

                    # PERSIST image reference
                    self.product_img = ctk.CTkImage(light_image=image, dark_image=image, size=(200, 180))
                    self.product_image_label.configure(image=self.product_img, text="")
                    self.product_image_label.image_ref = self.product_img  # <- VERY IMPORTANT
                except Exception as e:
                    print(f"Error loading image: {e}")
                    self.product_image_label.configure(image=None, text="Invalid Image", fg_color="#2A50CB")
            else:
                self.product_image_label.configure(image=None, text="No Image", fg_color="#2A50CB")

    def generate_qr_code(self, item_values):
        # Format the item details as JSON
        data = {
            "Item": item_values[1],
            "Category": item_values[2],
            "Quantity": item_values[3],
            "Price": item_values[4],
            "Status": item_values[5],
            "Sale Date": item_values[6],
        }

        json_data = json.dumps(data)

        qr = qrcode.QRCode(
            version = 1,
            box_size = 10,
            border = 4
        )
        qr.add_data(json_data)
        qr.make(fit=True)
        img = qr.make_image(fill_colour="Blue", back_colour="White")

        buffer = BytesIO()
        img.save(buffer, format = "PNG")
        buffer.seek(0)

        qr_img = Image.open(buffer)
        self.qr_img = ctk.CTkImage(
            light_image=qr_img,
            dark_image=qr_img,
            size=(200, 190)
        )

        # Set the image on the label (and clear text if needed)
        self.qr_label.configure(image=self.qr_img, text="")

    def update_item_handler(self):
        selected_item = self.product_treeview.selection()
        if not selected_item:
            messagebox.showerror("Error", "No Item Selected!")
            return

        item_values = self.product_treeview.item(selected_item, "values")
        item_id = item_values[0]

        # Current values from entry fields
        new_name = self.entries["Name"].get()
        new_category = self.entries["Category"].get()
        new_quantity = self.entries["Quantity"].get()
        new_price = self.entries["Price"].get()
        new_date = self.entries["Register_Date"].get()

        try:
            new_quantity_int = int(new_quantity)
            new_price_float = float(new_price)
        except ValueError:
            messagebox.showerror("Error", "Quantity must be an integer and Price must be a number.")
            return

        new_status = "Low Stock" if new_quantity_int < 5 else "In Stock"

        # Original values from treeview (as strings)
        original_values = {
            "Name": item_values[1],
            "Category": item_values[2],
            "Quantity": item_values[3],
            "Price": item_values[4],
            "Status": item_values[5],
            "Register_Date": item_values[6],
        }

        updated_values = {
            "Name": new_name,
            "Category": new_category,
            "Quantity": new_quantity,
            "Price": new_price,
            "Status": new_status,
            "Register_Date": new_date,
        }

        # Check if anything has changed
        if all(str(original_values[key]) == str(updated_values[key]) for key in original_values):
            messagebox.showinfo("No Changes", "No changes were made to the item.")
            return

        if self.is_duplicate_name(new_name, exclude_id=item_id):
            messagebox.showerror("Error", f"An item with the name '{new_name}' already exists.")
            return

        # Proceed with update
        self.db.update_item(
            item_name=new_name,
            category=new_category,
            quantity=new_quantity_int,
            price=new_price_float,
            status=new_status,
            registration_date=new_date,
            item_id=item_id
        )

        self.refresh_table()
        messagebox.showinfo("Success", "Item Updated Successfully!")
        self.clear_fields()

    def is_duplicate_name(self, name, exclude_id=None):
        for item in self.db.view_items():
            existing_id = item[0]
            existing_name = item[1]
            if existing_name.lower() == name.lower():
                if exclude_id is None or str(existing_id) != str(exclude_id):
                    return True
        return False

    def clear_fields(self):
        for entry in self.entries.values():
            entry.delete(0, END)

        self.product_image_label.image_ref = None
        self.product_treeview.selection_remove(self.product_treeview.selection())

    def delete_item_handler(self):
        selected_item = self.product_treeview.selection()
        if not selected_item:
            messagebox.showerror("Error", "No Item Selected!")
            return

        item_id = self.product_treeview.item(selected_item, "values")[0]

        if messagebox.askyesno("Confirm Delete", "Are You Sure You Want To Delete This?"):
            self.db.delete_item(item_id)
            self.refresh_table()
            messagebox.showinfo("Success", "Item Deleted Successfully!")

    def search_items(self, query):
        results = [row for row in self.db.view_items() if query.lower() in row[1].lower()]

        for row in self.product_treeview.get_children():
            self.product_treeview.delete(row)

        for row in results:
            item_id, item_name, category, quantity, price, status, register_date, image_data = row

            if int(quantity) < 5:
                status = "Low Stock"
            else:
                status = "In Stock"

            self.db.update_item(item_id, item_name, category, quantity, price, status, register_date)

            stock_colour = 'Red' if int(quantity) < 5 else 'Green'
            self.product_treeview.insert("", END,
                                         values=(item_id, item_name, category, quantity, price, status, register_date),
                                         tags=(stock_colour,))

    from tkinter import filedialog

    def change_product_image(self):
        selected_item = self.product_treeview.selection()
        if not selected_item:
            messagebox.showerror("Error", "No item selected.")
            return

        item_id = self.product_treeview.item(selected_item, "values")[0]
        file_path = filedialog.askopenfilename(title="Select Image", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])

        if not file_path:
            return  # user cancelled

        try:
            # Open and resize image before saving to DB
            with Image.open(file_path) as img:
                resized_img = img.resize((200, 180)).convert("RGBA")
                buffer = BytesIO()
                resized_img.save(buffer, format="PNG")
                image_blob = buffer.getvalue()

            # Save resized image to database
            conn = sqlite3.connect(self.db.db_file)
            cursor = conn.cursor()
            cursor.execute("UPDATE inventory SET product_image = ? WHERE id = ?", (image_blob, item_id))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Image Updated Successfully.")
            self.on_treeview_select()  # refresh image shown
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update image.\n{e}")


root = ctk.CTk()
app = Manage_Product(root)
root.mainloop()