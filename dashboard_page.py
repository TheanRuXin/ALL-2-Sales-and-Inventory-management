import customtkinter as ctk
from tkinter import messagebox, ttk
from PIL import Image
import os
import io
import sqlite3
from payment_window import PaymentFrame
import threading
import pythoncom
import platform
if platform.system() == "Windows":
    import wmi  # For Windows USB detection
elif platform.system() == "Linux":
    import pyudev

class Dashboard:
    def __init__(self, parent, cashier_username, cart_items=None, total_price=0.0, on_cart_update=None,
                 selected_category=None, selected_item=None, quantity_text=""):
        self.on_cart_update = on_cart_update
        self.current_image = None
        self.product_img = None
        self.selected_category = selected_category
        self.selected_item = selected_item
        self.saved_quantity_text = quantity_text
        self.cart_items = cart_items if cart_items else []
        self.total_price = total_price
        self.parent = parent
        self.discount_amount = 0.0
        self.tax_amount = 0.0
        self.cashier_username = cashier_username
        self.cashier_name = self.get_cashier_name()
        self.parent.rowconfigure(0, weight=1)
        self.parent.columnconfigure(0, weight=1)
        self.parent.configure(fg_color="white")
        self.main_frame = ctk.CTkFrame(self.parent, fg_color="white")
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.main_frame.rowconfigure(1, weight=1)
        self.main_frame.columnconfigure(0, weight=2)
        self.main_frame.columnconfigure(1, weight=1)
        self.load_dashboard_content()
        self.check_for_usb_device()  # <-- Add this at the end of __init__
        # QR Entry - Hidden input field for QR scanner input
        self.qr_entry = ctk.CTkEntry(self.main_frame, width=1, height=1)
        self.qr_entry.place(x=-100, y=-100)  # Hidden offscreen
        self.qr_entry.bind("<Return>", self.handle_qr_scan)
        self.qr_entry.focus_set()  # Autofocus so scanner input goes here

    def get_cashier_name(self):
        try:
            conn = sqlite3.connect("Trackwise.db")
            cursor = conn.cursor()
            cursor.execute("SELECT username FROM users WHERE username = ?", (self.cashier_username,))
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else self.cashier_username
        except Exception as e:
            print(f"Database error: {e}")
            return self.cashier_username

    def load_dashboard_content(self, restore=False):
        user_icon = self.load_icon("user1.png", size=(40, 40))
        self.user_frame = ctk.CTkFrame(self.main_frame, fg_color="white")
        self.user_frame.grid(row=0, column=0, sticky="nw", padx=30, pady=20)
        ctk.CTkLabel(self.user_frame, image=user_icon, text="").pack(side="left", padx=(0, 10))
        ctk.CTkLabel(self.user_frame, text=f"Welcome, {self.cashier_name}", font=("Arial", 16, "bold"), text_color="#0C5481").pack(side="left")
        self.product_img = None
        self.product_image_label = ctk.CTkLabel(
            self.main_frame,
            text="Product Image Will Appear Here",
            fg_color="#cce7f9",
            text_color="white",
            width=200,
            height=180
        )
        self.product_image_label.place(x=250, y=15)
        self.product_image_label.configure(image=self.current_image, text="")
        self.product_image_label.image_ref = self.current_image

        button_config = {"width": 300, "height": 50, "fg_color": "#0C5481", "hover_color": "#2874ed", "text_color": "white", "font": ("Arial", 14, "bold")}
        button_panel = ctk.CTkFrame(self.main_frame, fg_color="white")
        button_panel.grid(row=1, column=1, sticky="n", padx=(10, 5), pady=(30, 5))

        # 🔽 Category Dropdown
        self.category_var = ctk.StringVar(value="Select Category")
        self.category_dropdown = ctk.CTkComboBox(
            button_panel,
            values=self.fetch_categories(),
            variable=self.category_var,
            width=300, height=50,
            command=self.update_items_dropdown,
            text_color="#0882c4", fg_color="#cce7f9", border_color="#0C5481", border_width=2,
            dropdown_fg_color="#cce7f9", dropdown_text_color="#014894",
            dropdown_font=("Inter", 14), dropdown_hover_color="#8dc0f7",
            button_color="#0C5481", button_hover_color="#2874ed"
        )
        self.category_dropdown.pack(padx=10, pady=(5, 20))

        # 🔽 Item Dropdown
        self.item_var = ctk.StringVar(value="Select Item")
        self.item_dropdown = ctk.CTkComboBox(
            button_panel,
            values=["Select a Category First"],
            variable=self.item_var,
            width=300, height=50,
            text_color="#0882c4", fg_color="#cce7f9", border_color="#0C5481", border_width=2,
            dropdown_fg_color="#cce7f9", dropdown_text_color="#014894",
            dropdown_font=("Inter", 14), dropdown_hover_color="#8dc0f7",
            button_color="#0C5481", button_hover_color="#2874ed"
        )
        self.item_dropdown.pack(padx=10, pady=(20, 20))

        # 🔽 Quantity Entry
        self.quantity_entry = ctk.CTkEntry(
            button_panel,
            text_color="#0C5481", fg_color="#cce7f9", height=50,
            placeholder_text="Quantity", placeholder_text_color="#0882c4",
            border_color="#0C5481", width=300
        )
        self.quantity_entry.pack(padx=10, pady=(20, 20))
        self.quantity_entry.bind("<Return>", lambda event: self.add_to_cart())

        ctk.CTkButton(button_panel, text="Add to Cart", command=self.add_to_cart, **button_config).pack(pady=(10, 20), fill="x")
        ctk.CTkButton(button_panel, text="Delete Item", command=self.delete_last_item, **button_config).pack(pady=(0, 20), fill="x")
        ctk.CTkButton(button_panel, text="Cancel Order", command=self.cancel_order, width=300, height=50, fg_color="red", hover_color="#b01518", text_color="white", font=("Arial", 14, "bold")).pack(pady=(0, 20), fill="x")
        ctk.CTkButton(button_panel, text="Proceed to Payment", command=self.pay_order, width=300, height=50, fg_color="#5cb85c", hover_color="green", text_color="white", font=("Arial", 14, "bold")).pack(pady=(0, 20), fill="x")

        self.cart_table = ctk.CTkFrame(self.main_frame, fg_color="#eaf9ff", corner_radius=10)
        self.main_frame.columnconfigure(0, weight=4)
        self.cart_table.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview.Heading", background="#0C5481", foreground="white", font=("Arial", 15, "bold"), padding=[10, 10])
        style.configure("Treeview", background="#eaf9ff", foreground="#057687", rowheight=30, fieldbackground="#cce7f9", font=("Arial", 14))

        columns = ("Item Name", "Product ID", "Quantity", "Price")
        self.tree = ttk.Treeview(self.cart_table, columns=columns, show="headings", height=45)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=150)
        self.tree.pack(side="left", fill="x", expand=True)

        scrollbar = ctk.CTkScrollbar(self.cart_table, orientation="vertical", button_hover_color="#0882c4", button_color="#cce7f9", fg_color="#0C5481", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.create_calculator()
        self.refresh_cart_treeview()
        self.update_total_label()

        if self.selected_category and self.selected_category in self.fetch_categories():
            self.category_var.set(self.selected_category)
            self.update_items_dropdown(None)

            if self.selected_item and self.selected_item in self.fetch_items_by_category(self.selected_category):
                self.item_var.set(self.selected_item)
                self.display_selected_item_info()

        if self.saved_quantity_text:
            self.quantity_entry.insert(0, self.saved_quantity_text)

    def fetch_categories(self):
        try:
            with sqlite3.connect('Trackwise.db') as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT DISTINCT category FROM inventory")
                return [row[0] for row in cursor.fetchall()] or ["No Categories"]
        except:
            return ["No Categories"]

    def fetch_items_by_category(self, category):
        try:
            with sqlite3.connect('Trackwise.db') as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT item_name FROM inventory WHERE category = ?", (category,))
                return [row[0] for row in cursor.fetchall()] or ["No Items"]
        except:
            return ["No Items"]

    def update_items_dropdown(self, _):
        items = self.fetch_items_by_category(self.category_var.get())
        self.item_dropdown.configure(values=items)

        self.product_image_label.configure(image=None, text="")
        self.item_dropdown.bind("<<ComboboxSelected>>", self.display_selected_item_info)

    def display_selected_item_info(self, event=None):
        selected_item = self.item_var.get()
        if selected_item in ("Select Item", "Select a Category First"):
            return

        try:
            with sqlite3.connect("Trackwise.db") as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT product_image FROM inventory WHERE item_name = ?", (selected_item,))
                result = cursor.fetchone()

            # Reset image and label
            self.product_image_label.configure(image=None, text="Product Image Here", fg_color="#2A50CB")

            if result and result[0]:
                try:
                    image_data = result[0]  # BLOB
                    image = Image.open(io.BytesIO(image_data)).convert("RGBA")

                    display_size = (200, 180)
                    image = image.resize(display_size)
                    self.product_img = ctk.CTkImage(light_image=image, dark_image=image, size=display_size)
                    self.product_image_label.configure(image=self.product_img, text="")
                    self.product_image_label.image_ref = self.product_img
                    self.product_image_label.place_configure(width=display_size[0], height=display_size[1])

                except Exception as e:
                    print(f"Error loading image: {e}")
                    self.product_image_label.configure(image=None, text="Invalid Image", fg_color="#2A50CB")
            else:
                self.product_image_label.configure(image=None, text="No Image", fg_color="#2A50CB")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load item image:\n{e}", parent=self.main_frame)

    def check_for_usb_device(self):
        def usb_check():
            pythoncom.CoInitialize()
            if platform.system() == "Windows":
                c = wmi.WMI()
                for usb in c.Win32_USBControllerDevice():
                    if "iPhone" in str(usb.Dependent):
                        self.prompt_qr_device()
                        break
            elif platform.system() == "Linux":
                context = pyudev.Context()
                monitor = pyudev.Monitor.from_netlink(context)
                for device in iter(monitor.poll, None):
                    if device.get("ID_MODEL") and "iPhone" in device.get("ID_MODEL"):
                        self.prompt_qr_device()
                        break
            pythoncom.CoUninitialize()

        threading.Thread(target=usb_check, daemon=True).start()

    def prompt_qr_device(self):
        result = messagebox.askyesno("QR Device Detected", "iPhone connected. Use this device for QR scanning?")
        if result:
            self.qr_entry.focus_set()

    def add_to_cart(self):
        item = self.item_var.get()
        qty_text = self.quantity_entry.get()

        if item in ("Select Item", "Select a Category First") or not qty_text.isdigit():
            messagebox.showwarning("Input Error", "Select a valid item and enter quantity.")
            return

        requested_qty = int(qty_text)

        try:
            with sqlite3.connect('Trackwise.db') as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT product_id, price, status, quantity, product_image
                    FROM inventory 
                    WHERE LOWER(TRIM(item_name)) = ?
                """, (item.strip().lower(),))
                result = cursor.fetchone()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to fetch item details.\n{e}")
            return

        if not result:
            messagebox.showerror("Item Error", f"No matching item found for '{item}'.")
            return

        prod_id, price, status, available_stock, image_blob = result

        try:
            price = float(price)
        except:
            messagebox.showerror("Data Error", f"Invalid price for item '{item}'.")
            return

        cart_qty = sum(qty for name, _, qty, _, _ in self.cart_items if name == item)

        if cart_qty + requested_qty > available_stock:
            messagebox.showwarning("Stock Limit",
                                   f"Only {available_stock - cart_qty} more units available for '{item}'.")
            return

        for i, (name, pid, qty, price_in_cart, item_status) in enumerate(self.cart_items):
            if name == item:
                self.cart_items[i] = (name, pid, qty + requested_qty, price, item_status)
                break
        else:
            self.cart_items.append((item, prod_id, requested_qty, price, status))

        self.total_price += requested_qty * price
        self.refresh_cart_treeview()
        self.total_label.configure(text=f"Total: RM {self.total_price:.2f}")
        self.quantity_entry.delete(0, 'end')
        self.update_total_label()

        if image_blob:
            try:
                image = Image.open(io.BytesIO(image_blob)).convert("RGBA")

                display_size = (200, 180)

                self.current_image = ctk.CTkImage(light_image=image, dark_image=image, size=display_size)
                self.product_image_label.configure(image=self.current_image, text="")
                self.product_image_label.image_ref = self.current_image
                self.product_image_label.configure(width=display_size[0], height=display_size[1])
            except Exception as e:
                self.product_image_label.configure(image=None, text="Invalid image")
                print(f"[Image Load Error] {e}")

        if self.on_cart_update:
            self.on_cart_update(self.cart_items, self.total_price)

    def handle_qr_scan(self, event):
        scanned_product_id = self.qr_entry.get().strip()
        self.qr_entry.delete(0, 'end')

        if not scanned_product_id:
            messagebox.showwarning("QR Scan", "Scanned data is empty.")
            return

        try:
            with sqlite3.connect('Trackwise.db') as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT item_name, product_id, quantity, price, status 
                    FROM inventory 
                    WHERE product_id = ?
                """, (scanned_product_id,))
                result = cursor.fetchone()

                if not result:
                    messagebox.showerror("QR Scan", f"No product found with ID {scanned_product_id}.")
                    return

                name, pid, stock_qty, price, status = result
                quantity_to_add = 1
                cart_qty = sum(qty for n, _, qty, _, _ in self.cart_items if n == name)

                if cart_qty + quantity_to_add > stock_qty:
                    messagebox.showwarning("Stock Limit", f"Only {stock_qty - cart_qty} units available.")
                    return

                for i, (n, pid_, qty, price_, st) in enumerate(self.cart_items):
                    if n == name:
                        self.cart_items[i] = (n, pid_, qty + quantity_to_add, price, st)
                        break
                else:
                    self.cart_items.append((name, pid, quantity_to_add, price, status))

                self.total_price += quantity_to_add * price
                self.refresh_cart_treeview()
                self.update_total_label()


        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to fetch product details.\n{e}")

    def refresh_cart_treeview(self):
        self.tree.delete(*self.tree.get_children())
        for item in self.cart_items:
            name, pid, qty, price, status = item
            self.tree.insert("", "end", values=(name, pid, qty, f"{price:.2f}", status))

    def delete_last_item(self):
        if not self.cart_items:
            messagebox.showinfo("Empty Cart", "There are no items to delete.")
            return

        last_item = self.cart_items.pop()
        self.total_price -= last_item[3] * last_item[2]  # price * qty

        children = self.tree.get_children()
        if children:
            self.tree.delete(children[-1])

        self.total_label.configure(text=f"Total: RM {self.total_price:.2f}")

        #  Refresh Net, Tax, Discount, Total
        self.update_total_label()

        if self.on_cart_update:
            self.on_cart_update(self.cart_items, self.total_price)

    def cancel_order(self):
        if messagebox.askyesno("Cancel Order", "Are you sure?"):
            self.clear_cart()

    def clear_cart(self):
        self.cart_items.clear()
        self.total_price = 0.0
        self.tree.delete(*self.tree.get_children())
        self.total_label.configure(text="Total: RM 0.00")
        self.discount_entry.delete(0, 'end')
        self.quantity_entry.delete(0, 'end')

        self.update_total_label()  # <-- 🆕 Refresh net, tax, total

        if self.on_cart_update:
            self.on_cart_update(self.cart_items, self.total_price)

    def pay_order(self):
        if not self.cart_items:
            messagebox.showwarning("Payment", "Cart is empty.")
            return

        # Recalculate the total before passing
        self.update_total_label()

        # Extract values
        final_total = self.get_final_total()
        tax = self.tax_amount
        discount = self.discount_amount

        # Destroy current frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        PaymentFrame(
            parent=self.main_frame,
            total_amount=self.total_price,  # ✅ Net subtotal before tax and discount
            cart_items=self.cart_items.copy(),
            tax_amount=self.tax_amount,  # ✅ Properly calculated tax
            discount_amount=self.discount_amount,  # ✅ Properly calculated discount
            on_payment_complete=self.clear_cart_and_reload,
            on_cancel=lambda: self.reload_dashboard_content(keep_cart=True)
        ).pack(fill="both", expand=True)

    def reload_dashboard_content(self, keep_cart=False):
        current_cart = self.cart_items if keep_cart else []
        current_total = self.total_price if keep_cart else 0.0

        for widget in self.parent.winfo_children():
            widget.destroy()

        Dashboard(self.parent, self.cashier_username, current_cart, current_total)

    def clear_cart_and_reload(self):
        self.cart_items.clear()
        self.total_price = 0.0
        self.reload_dashboard_content()

    def update_dashboard_cart(self, cart_items, total_price):
        self.dashboard_cart_items = cart_items
        self.dashboard_total_price = total_price

    def create_calculator(self):
        # Total Display Frame
        custom_width = 350

        total_frame = ctk.CTkFrame(self.main_frame, fg_color="#eaf9ff", width=custom_width,
                                   border_color="#0C5481", border_width=2, corner_radius=10)
        total_frame.grid(row=0, column=1, sticky="n", padx=10, pady=(10, 10), ipadx=10, ipady=5)

        # Net Label (Subtotal)
        self.net_label = ctk.CTkLabel(total_frame, text="Net: RM 0.00", font=("Arial", 14), text_color="#0C5481",
                                      anchor="w")
        self.net_label.pack(pady=(5, 0), padx=10, fill="x")

        # Tax Label (6% Auto)
        self.tax_label = ctk.CTkLabel(total_frame, text="Tax: RM 0.00", font=("Arial", 14), text_color="#0C5481",
                                      anchor="w")
        self.tax_label.pack(pady=(5, 0), padx=10, fill="x")

        # Discount Entry
        discount_frame = ctk.CTkFrame(total_frame, fg_color="#eaf9ff")
        discount_frame.pack(pady=(5, 0), padx=10, fill="x")
        ctk.CTkLabel(discount_frame, text="Discount:", font=("Arial", 14), text_color="#0C5481", width=140,
                     anchor="w").pack(side="left")
        self.discount_entry = ctk.CTkEntry(discount_frame, placeholder_text="Enter Discount %", width=110)
        self.discount_entry.pack(side="left", padx=5)

        # Total Label (Net + Tax - Discount)
        self.total_label = ctk.CTkLabel(total_frame, text="Total: RM 0.00", font=("Arial", 14, "bold"),
                                        text_color="#0C5481", anchor="w")
        self.total_label.pack(pady=(5, 10), padx=10, fill="x")

        # Discount Apply Button
        action_frame = ctk.CTkFrame(total_frame, fg_color="#eaf9ff")
        action_frame.pack(pady=(0, 10), padx=10, fill="x")
        ctk.CTkButton(action_frame, text="Apply Discount", command=self.apply_discount, width=140,
                      fg_color="#0C5481", hover_color="#2874ed", text_color="white").pack(side="left", padx=5)


    def apply_discount(self):
        try:
            self.discount_amount = float(self.discount_entry.get()) if self.discount_entry.get() else 0.0
        except:
            self.discount_amount = 0.0

        self.update_total_label()  # Recalculate total using current discount

    def apply_tax(self):
        self.tax_amount = self.total_price * 0.06
        self.update_total_label()

    def update_total_label(self):
        try:
            discount_percent = float(self.discount_entry.get()) if self.discount_entry.get() else 0.0
        except:
            discount_percent = 0.0

        net_total = self.total_price
        self.tax_amount = round(net_total * 6 / 106, 2)  # ✅ Extract 6% from tax-inclusive prices
        self.discount_amount = round((discount_percent / 100) * net_total, 2)

        self.final_total = round(net_total - self.discount_amount, 2)  # ✅ No extra tax added

        self.net_label.configure(text=f"Net: RM {net_total - self.tax_amount:.2f}")
        self.tax_label.configure(text=f"Tax (included): RM {self.tax_amount:.2f}")
        self.total_label.configure(text=f"Total: RM {self.final_total:.2f}")

    def get_final_total(self):
        return self.final_total

    def load_icon(self, filename, size=(30, 30)):
        path = os.path.join("images", filename)
        return ctk.CTkImage(Image.open(path), size=size) if os.path.exists(path) else None



def load_dashboard_content(parent, cashier_username, cart_items=None, total_price=0.0, on_cart_update=None):
    return Dashboard(parent, cashier_username, cart_items, total_price, on_cart_update)

