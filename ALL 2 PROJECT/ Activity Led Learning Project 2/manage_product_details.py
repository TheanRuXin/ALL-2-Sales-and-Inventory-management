from tkinter import filedialog
import sqlite3
from six import BytesIO
import qrcode
import json
import customtkinter as ctk
from tkinter import messagebox, ttk, END
from PIL import Image

class Setup_Database:
    def __init__(self, db_file= "Trackwise.db"):
        self.db_file = db_file

    def view_items(self):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inventory")
        rows = cursor.fetchall()
        conn.close()
        return rows

    def delete_item(self, product_id):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM inventory WHERE product_id = ?", (product_id,))
        conn.commit()
        conn.close()

    def update_item(self, *, product_id, item_name, category, quantity, price, status, registration_date, image_blob=None):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        if image_blob:
            cursor.execute(
                '''UPDATE inventory SET
                item_name = ?, 
                category = ?,
                quantity = ?,
                price = ?,
                status = ?,
                register_date = ?,
                product_image = ?
                WHERE product_id = ?''',
                (item_name, category, int(quantity), float(price), status, registration_date, image_blob, product_id)
            )
        else:
            cursor.execute(
                '''UPDATE inventory SET
                item_name = ?, 
                category = ?,
                quantity = ?,
                price = ?,
                status = ?,
                register_date = ?
                WHERE product_id = ?''',
                (item_name, category, int(quantity), float(price), status, registration_date, product_id)
            )
        conn.commit()
        conn.close()

class ManageProductPage(ctk.CTkFrame):
    def __init__(self,parent,controller):
        super().__init__(parent)
        self.controller = controller
        self.product_image_path = None

        self.width, self.height = 1574, 800

        background_image = ctk.CTkImage(Image.open(r"Manage_Product.png"), size=(self.width, self.height))
        background_image_label = ctk.CTkLabel(self, image=background_image, text="")
        background_image_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.categories = []
        self.load_categories()
        self.create_widgets()
        self.category_combobox.configure(values=self.categories)
        if self.categories:
            self.category_combobox.set("Select Categories")

        self.db = Setup_Database()
        self.refresh_table()

    def load_categories(self):
        conn = sqlite3.connect('Trackwise.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM categories")
        self.categories = [row[0] for row in cursor.fetchall()]
        conn.close()

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
                                       fg_color="#ebf9ff", border_color="#0C5481", text_color="black",
                                       textvariable=self.name)
        self.name_entry.place(x=1370 / 1920 * self.width, y=152 / 974 * self.height)

        # Category
        self.category_text = ctk.CTkLabel(self, text="Category:",
                                          font=("Inter", 23),
                                          bg_color="#FFFFFF", fg_color="#FFFFFF",
                                          text_color="black")
        self.category_text.place(x=1370 / 1920 * self.width, y=231 / 974 * self.height)

        self.category = ctk.StringVar()
        self.category_combobox = ctk.CTkComboBox(self, width=320 / 1536 * self.width,values=self.categories,
                                           height=45 / 864 * self.height, bg_color="#FFFFFF", button_color="#0C5481", button_hover_color="#52a0bf",
                                           fg_color="#ebf9ff", border_color="#0C5481", text_color="black")
        if self.categories:
            self.category_combobox.set(self.categories[0])
        self.category_combobox.place(x=1370 / 1920 * self.width, y=270 / 974 * self.height)

        # Quantity
        self.quantity_text = ctk.CTkLabel(self, text="Quantity:",
                                          font=("Inter", 23),
                                          bg_color="#FFFFFF", fg_color="#FFFFFF",
                                          text_color="black")
        self.quantity_text.place(x=1386 / 1920 * self.width, y=342 / 974 * self.height)

        self.quantity = ctk.StringVar()
        self.quantity_entry = ctk.CTkEntry(self, font=("Inter", 18), width=320 / 1536 * self.width,
                                           height=45 / 864 * self.height, bg_color="#FFFFFF",
                                           fg_color="#ebf9ff", border_color="#0C5481", text_color="black",
                                           textvariable=self.quantity)
        self.quantity_entry.place(x=1370 / 1920 * self.width, y=380 / 974 * self.height)

        # Price
        self.price_text = ctk.CTkLabel(self, text="Price:",
                                       font=("Inter", 23),
                                       bg_color="#FFFFFF", fg_color="#FFFFFF",
                                       text_color="black")
        self.price_text.place(x=1370 / 1920 * self.width, y=450 / 974 * self.height)

        self.price = ctk.StringVar()
        self.price_entry = ctk.CTkEntry(self, font=("Inter", 18), width=320 / 1536 * self.width,
                                        height=45 / 864 * self.height, bg_color="#FFFFFF",
                                        fg_color="#ebf9ff", border_color="#0C5481", text_color="black",
                                        textvariable=self.price)
        self.price_entry.place(x=1370 / 1920 * self.width, y=488 / 974 * self.height)

        # Status
        self.status_text = ctk.CTkLabel(self, text="Status:",
                                        font=("Inter", 23),
                                        bg_color="#FFFFFF", fg_color="#FFFFFF",
                                        text_color="black")
        self.status_text.place(x=1370 / 1920 * self.width, y=560 / 974 * self.height)

        self.status = ctk.StringVar()
        self.status_entry = ctk.CTkComboBox(self, values=["In Stock", "Out of Stock", "Unavailable"],
                                            font=("Arial", 18), width=320 / 1536 * self.width,
                                            height=45 / 864 * self.height, bg_color="#FFFFFF", button_color="#0C5481", button_hover_color="#52a0bf",
                                            fg_color="#ebf9ff", border_color="#0C5481", text_color="black",
                                            )
        self.status_entry.place(x=1370 / 1920 * self.width, y=600 / 974 * self.height)

        # Registration Date
        self.date_text = ctk.CTkLabel(self, text="Registration Date:",
                                      font=("Inter", 23),
                                      bg_color="#FFFFFF", fg_color="#FFFFFF",
                                      text_color="black")
        self.date_text.place(x=1370 / 1920 * self.width, y=668 / 974 * self.height)

        self.date = ctk.StringVar()
        self.date_entry = ctk.CTkEntry(self, font=("Inter", 18), width=320 / 1536 * self.width,
                                       height=45 / 864 * self.height, bg_color="#FFFFFF",
                                       fg_color="#ebf9ff", border_color="#0C5481", text_color="black",
                                       textvariable=self.date,state="disabled")
        self.date_entry.place(x=1370 / 1920 * self.width, y=710 / 974 * self.height)

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

        # Change Image Button
        self.change_image_button = ctk.CTkButton(self, text="Change Image",
                                                 font=("Inter", 16),
                                                 width=150, height=40,
                                                 bg_color="#FFFFFF", fg_color="#0C5481",
                                                 text_color="#FFFCFC",
                                                 border_color="#1572D3",
                                                 command=self.change_product_image)
        self.change_image_button.place(x=900 / 1920 * self.width, y=170 / 864 * self.height)

        # Search Box
        self.search_label = ctk.CTkLabel(self, text="Search Product:",
                                         font=("Inter", 20),
                                         bg_color="#FFFFFF", fg_color="#FFFFFF",
                                         text_color="black")
        self.search_label.place(x=800 / 1920 * self.width, y=245 / 864 * self.height)

        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(self, textvariable=self.search_var,
                                         width=320 / 1536 * self.width,
                                         height=45 / 864 * self.height,
                                         bg_color="#FFFFFF",
                                         fg_color="#ebf9ff", border_color="#0C5481",
                                         text_color="black",
                                         font=("Inter", 16))
        self.search_entry.place(x=800 / 1920 * self.width, y=280 / 864 * self.height)
        self.search_entry.bind("<KeyRelease>", lambda e: self.search_items(self.search_var.get()))

        # OR CODES
        self.qr_label = ctk.CTkLabel(self, text="QR Code will Appear Here", bg_color="#FFFFFF", fg_color="#eaf9ff",
                                     width=200, height=182)
        self.qr_label.place(x=458 / 1920 * self.width, y=133 / 974 * self.height)

        # Product Image Label
        self.product_image_label = ctk.CTkLabel(self, text="Product Image Will Appear Here", bg_color="#FFFFFF",
                                                fg_color="#eaf9ff", width=200, height=182)
        self.product_image_label.place(x=130 / 1920 * self.width, y=133 / 974 * self.height)

        # Frame for Table and Scrollbar (Manage Product Table)
        table_frame = ctk.CTkFrame(self, fg_color="transparent")
        table_frame.place(x=100 / 1920 * self.width, y=360 / 864 * self.height, relwidth=0.65, relheight=0.5)

        tree_container = ctk.CTkFrame(table_frame, fg_color="transparent")
        tree_container.pack(fill="both", expand=True)

        # Treeview Style
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview.Heading",
                        background="#0C5481", foreground="white",
                        font=("Arial", 14, "bold"))
        style.configure("Treeview",
                        background="#eaf9ff",
                        foreground="#057687",
                        rowheight=26,
                        fieldbackground="#eaf9ff",
                        font=("Arial", 13))
        style.map('Treeview',
                  background=[('selected', '#b0d9e6')])

        # Treeview Columns
        self.product_treeview = ttk.Treeview(tree_container,
                                             columns=("Product ID", "Name", "Category", "Quantity", "Price", "Status",
                                                      "Register_Date"),
                                             show="headings", height=12)

        # Define columns with reduced width
        self.product_treeview.heading("Product ID", text="Product ID")
        self.product_treeview.column("Product ID", width=140, anchor="center")

        self.product_treeview.heading("Name", text="Name")
        self.product_treeview.column("Name", width=140, anchor="center")

        self.product_treeview.heading("Category", text="Category")
        self.product_treeview.column("Category", width=130, anchor="center")

        self.product_treeview.heading("Quantity", text="Quantity")
        self.product_treeview.column("Quantity", width=130, anchor="center")

        self.product_treeview.heading("Price", text="Price")
        self.product_treeview.column("Price", width=130, anchor="center")

        self.product_treeview.heading("Status", text="Status")
        self.product_treeview.column("Status", width=120, anchor="center")

        self.product_treeview.heading("Register_Date", text="Register Date")
        self.product_treeview.column("Register_Date", width=140, anchor="center")

        self.product_treeview.grid(row=0, column=0, sticky="nsew")

        # Scrollbar
        scrollbar = ctk.CTkScrollbar(tree_container, orientation="vertical",
                                     command=self.product_treeview.yview,
                                     fg_color="#0C5481",
                                     button_color="#cce7f9",
                                     button_hover_color="#0882c4")
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.product_treeview.configure(yscrollcommand=scrollbar.set)

        # Stretchable layout
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)

        # Tags for highlighting
        self.product_treeview.tag_configure("Red", background="#FF6666")
        self.product_treeview.tag_configure("Green", background="#D6F5D6")

        # Start blinking rows
        self.blink_red_rows()
    def blink_red_rows(self):
        current_color = getattr(self, "_blink_color", "#FF6666")
        new_color = "#FFFFFF" if current_color == "#FF6666" else "#FF6666"
        self._blink_color = new_color

        # Update red tag color
        self.product_treeview.tag_configure("Red", background=new_color)

        # Repeat every 500 milliseconds
        self.after(500, self.blink_red_rows)

    def refresh_table(self):
        self.product_id_map = {}

        for row in self.product_treeview.get_children():
            self.product_treeview.delete(row)

        for row in self.db.view_items():
            item_id, product_id,item_name, category, quantity, price, status, register_date, image_data = row
            if int(quantity) == 0:
                status = "Out of Stock"
                tags = "Red"
            elif int(quantity) < 5:
                status = "Low Stock"
                tags = "Red"
            else:
                status = "In Stock"
                tags = ""
            self.product_treeview.insert(
                "", END,
                values=(product_id, item_name, category, quantity, price, status, register_date),
                tags=tags
            )

    def on_treeview_select(self):
        selected_item = self.product_treeview.selection()
        if selected_item:
            values = self.product_treeview.item(selected_item, "values")
            for i, key in enumerate(self.entries.keys()):
                widget = self.entries[key]
                value = values[i + 1]

                if key == "Register_Date":
                    # Temporarily enable entry, set value, then disable it again
                    widget.configure(state="normal")
                    widget.delete(0, END)
                    widget.insert(0, value)
                    widget.configure(state="disabled")
                elif hasattr(widget, "delete"):  # CTkEntry
                    widget.delete(0, END)
                    widget.insert(0, value)
                else:  # CTkComboBox
                    widget.set(value)

            self.generate_qr_code(values)
            product_id = values[0]
            conn = sqlite3.connect(self.db.db_file)
            cursor = conn.cursor()
            cursor.execute("SELECT product_image FROM inventory WHERE product_id = ?", (product_id,))
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
                    self.product_image_label.image_ref = self.product_img
                except Exception as e:
                    print(f"Error loading image: {e}")
                    self.product_image_label.configure(image=None, text="Invalid Image", fg_color="#2A50CB")
            else:
                self.product_image_label.configure(image=None, text="No Image", fg_color="#2A50CB")


    def generate_qr_code(self, item_values):
        data = {
            "Product_ID": item_values[0],
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
        self.qr_label.configure(image=self.qr_img, text="")
        self.qr_label.image = self.qr_img

    def update_item_handler(self):
        selected_item = self.product_treeview.selection()
        if not selected_item:
            messagebox.showerror("Error", "No Item Selected!")
            return

        item_values = self.product_treeview.item(selected_item, "values")
        product_id = item_values[0]  # Now using product_id from first column

        new_name = self.entries["Name"].get()
        new_category = self.category_combobox.get()
        new_quantity = self.entries["Quantity"].get()
        new_price = self.entries["Price"].get()
        new_status = self.entries["Status"].get()
        new_date = self.entries["Register_Date"].get()

        try:
            new_quantity_int = int(new_quantity)
            new_price_float = float(new_price)
        except ValueError:
            messagebox.showerror("Error", "Quantity must be an integer and Price must be a number.")
            return
        if not (1 <= new_quantity_int <= 144):
            messagebox.showerror("Error", "Quantity must be between 1 and 144.")
            return

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

        if all(str(original_values[key]).strip().lower() == str(updated_values[key]).strip().lower() for key in original_values):
            return

        if self.is_duplicate_name(new_name, exclude_product_id=product_id):
            messagebox.showerror("Error", f"An item with the name '{new_name}' already exists.")
            return

        image_data = None
        if self.product_image_path:
            try:
                with open(self.product_image_path, 'rb') as f:
                    image_data = f.read()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read product image: {e}", parent=self)
                return
        if new_quantity_int < 5:
            new_status = "Low Stock"
        else:
            new_status = "In Stock"
        self.status_entry.set(new_status)

        # Proceed with update
        self.db.update_item(
            item_name=new_name,
            category=new_category,
            quantity=new_quantity_int,
            price=new_price_float,
            status=new_status,
            registration_date=new_date,
            product_id=product_id,
            image_blob = image_data
        )

        self.refresh_table()
        for row_id in self.product_treeview.get_children():
            values = self.product_treeview.item(row_id, "values")
            if str(values[0]) == str(product_id):
                self.product_treeview.selection_set(row_id)
                self.on_treeview_select()
                break
        messagebox.showinfo("Success", "Item Updated Successfully!")


    def is_duplicate_name(self, name, exclude_product_id=None):
        for item in self.db.view_items():
            existing_product_id = item[0]
            existing_name = item[1]
            if existing_name.lower() == name.lower():
                if exclude_product_id is None or str(existing_product_id) != str(exclude_product_id):
                    return True
        return False

    def clear_fields(self):
        for entry in self.entries.values():
            if hasattr(entry, "delete"):  # For CTkEntry
                entry.delete(0, END)
            else:  # For CTkComboBox
                entry.set("")  # or a default value like entry.set("In Stock")

        self.product_image_label.configure(image=None, text="Product Image Here", fg_color="#2A50CB")
        self.qr_label.configure(image=None, text="QR Code will Appear Here", fg_color="#2A50CB")
        self.product_treeview.selection_remove(self.product_treeview.selection())

    def delete_item_handler(self):
        selected_item = self.product_treeview.selection()
        if not selected_item:
            messagebox.showerror("Error", "No Item Selected!")
            return

        product_id = self.product_treeview.item(selected_item, "values")[0]

        if messagebox.askyesno("Confirm Delete", "Are You Sure You Want To Delete This?"):
            self.db.delete_item(product_id)
            self.refresh_table()
            messagebox.showinfo("Success", "Item Deleted Successfully!")

    def search_items(self, query):
        results = [row for row in self.db.view_items() if query.lower() in row[2].lower()]

        for row in self.product_treeview.get_children():
            self.product_treeview.delete(row)

        self.product_id_map = {}

        for row in results:
            item_id, product_id,item_name, category, quantity, price, status, register_date, image_data = row

            if int(quantity) < 5:
                status = "Low Stock"
            elif int(quantity) == 0:
                status = "Out of Stock"
            else:
                status = "In Stock"

            self.db.update_item(
                product_id=product_id,
                item_name=item_name,
                category=category,
                quantity=quantity,
                price=price,
                status=status,
                registration_date=register_date
            )

            stock_colour = 'Red' if int(quantity) < 5 else 'Green'
            self.product_treeview.insert("", END,
                                         values=(product_id,item_name, category, quantity, price, status, register_date),
                                         tags=(stock_colour,))

    def change_product_image(self):
        selected_item = self.product_treeview.selection()
        if not selected_item:
            messagebox.showerror("Error", "No item selected.")
            return

        product_id = self.product_treeview.item(selected_item, "values")[0]
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
            cursor.execute("UPDATE inventory SET product_image = ? WHERE product_id = ?", (image_blob, product_id))
            conn.commit()
            conn.close()
            self.product_image_path = file_path
            messagebox.showinfo("Success", "Image Updated Successfully.")
            self.on_treeview_select()  # refresh image shown
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update image.\n{e}")
