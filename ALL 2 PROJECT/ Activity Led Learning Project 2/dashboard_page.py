import customtkinter as ctk
from tkinter import messagebox, ttk
from PIL import Image
import os
import sqlite3
from payment_window import PaymentFrame

class Dashboard:
    def __init__(self, parent, cashier_username, cart_items=None, total_price=0.0, on_cart_update=None,
                 selected_category=None, selected_item=None, quantity_text=""):
        self.on_cart_update = on_cart_update
        self.selected_category = selected_category
        self.selected_item = selected_item
        self.saved_quantity_text = quantity_text
        self.cart_items = cart_items if cart_items else []
        self.total_price = total_price
        self.parent = parent
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
        # Create user greeting
        user_icon = self.load_icon("user1.png", size=(40, 40))
        self.user_frame = ctk.CTkFrame(self.main_frame, fg_color="white")
        self.user_frame.grid(row=0, column=0, sticky="nw", padx=30, pady=20)
        ctk.CTkLabel(self.user_frame, image=user_icon, text="").pack(side="left", padx=(0, 10))
        ctk.CTkLabel(self.user_frame, text=f"Welcome, {self.cashier_name}", font=("Arial", 16, "bold"), text_color="#0C5481").pack(side="left")

        # Dropdown panel
        panel = ctk.CTkFrame(self.main_frame, fg_color="white")
        panel.grid(row=0, column=0, sticky="ne", padx=20, pady=(60, 10))

        self.category_var = ctk.StringVar(value="Select Category")
        self.category_dropdown = ctk.CTkComboBox(
            panel,
            values=self.fetch_categories(),
            variable=self.category_var,
            width=250,height=40, command=self.update_items_dropdown, text_color="#0882c4", fg_color="#cce7f9", border_color="#0C5481",border_width=2,
            dropdown_fg_color="#cce7f9", dropdown_text_color="#014894", dropdown_font=("Inter", 14), dropdown_hover_color="#8dc0f7", button_color="#0C5481", button_hover_color="#2874ed")
        self.category_dropdown.grid(row=2, column=0, padx=10, pady=10)

        self.item_var = ctk.StringVar(value="Select Item")
        self.item_dropdown = ctk.CTkComboBox(
            panel,
            values=["Select a Category First"],
            variable=self.item_var,
            width=250, height=40, text_color="#0882c4", fg_color="#cce7f9", border_color="#0C5481", border_width=2, dropdown_fg_color="#cce7f9", dropdown_text_color="#014894",
            dropdown_font=("Inter", 14), dropdown_hover_color="#8dc0f7", button_color="#0C5481", button_hover_color="#2874ed")
        self.item_dropdown.grid(row=2, column=1, padx=10, pady=10)

        self.quantity_entry = ctk.CTkEntry(
            panel,
            text_color="#0C5481", fg_color="#cce7f9", height=40, placeholder_text="Quantity", placeholder_text_color="#0882c4", border_color="#0C5481", width=250)
        self.quantity_entry.grid(row=2, column=2, padx=10, pady=10)
        self.quantity_entry.bind("<Return>", lambda event: self.add_to_cart())

        button_config = {"width": 300, "height": 50, "fg_color": "#0C5481", "hover_color": "#2874ed", "text_color": "white", "font": ("Arial", 14, "bold")}
        button_panel = ctk.CTkFrame(self.main_frame, fg_color="white")
        button_panel.grid(row=1, column=1, sticky="n", padx=(10, 10), pady=(380, 10))

        ctk.CTkButton(button_panel, text="Add to Cart", command=self.add_to_cart, **button_config).pack(pady=(0, 10), fill="x")
        ctk.CTkButton(button_panel, text="Delete Item", command=self.delete_last_item, **button_config).pack(pady=(0, 10), fill="x")
        ctk.CTkButton(button_panel, text="Cancel Order", command=self.cancel_order, width=300, height=50, fg_color="red", hover_color="#b01518", text_color="white", font=("Arial", 14, "bold")).pack(pady=(0, 10), fill="x")
        ctk.CTkButton(button_panel, text="Proceed to Payment", command=self.pay_order, width=300, height=50, fg_color="#5cb85c", hover_color="green", text_color="white", font=("Arial", 14, "bold")).pack(pady=(0, 10), fill="x")

        self.cart_table = ctk.CTkFrame(self.main_frame, fg_color="#eaf9ff", corner_radius=10)
        self.main_frame.columnconfigure(0, weight=4)
        self.cart_table.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview.Heading", background="#0C5481", foreground="white", font=("Arial", 15, "bold"), padding=[10, 10])
        style.configure("Treeview", background="#eaf9ff", foreground="#057687", rowheight=30, fieldbackground="#cce7f9", font=("Arial", 14))

        columns = ("Item Name", "Product ID", "Quantity", "Price", "Status")
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
        self.total_label.configure(text=f"Total: RM {self.total_price:.2f}")

        # ✅ Restore dropdowns and quantity field if values were passed
        if self.selected_category and self.selected_category in self.fetch_categories():
            self.category_var.set(self.selected_category)
            self.update_items_dropdown(None)

            if self.selected_item and self.selected_item in self.fetch_items_by_category(self.selected_category):
                self.item_var.set(self.selected_item)

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

    def add_to_cart(self):
        item = self.item_var.get()
        qty_text = self.quantity_entry.get()

        if item in ("Select Item", "Select a Category First") or not qty_text.isdigit():
            messagebox.showwarning("Input Error", "Select a valid item and enter quantity.")
            return

        requested_qty = int(qty_text)

        with sqlite3.connect('Trackwise.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT product_id, price, status, quantity FROM inventory WHERE item_name = ?", (item,))
            result = cursor.fetchone()

        if result:
            prod_id, price, status, available_stock = result

            # Calculate current quantity in cart for this item
            cart_qty = 0
            for name, _, qty, _, _ in self.cart_items:
                if name == item:
                    cart_qty = qty
                    break

            if cart_qty + requested_qty > available_stock:
                messagebox.showwarning("Stock Limit",
                                       f"Only {available_stock - cart_qty} more units available for '{item}'.")
                return

            # Check if item is already in the cart
            for i, (name, pid, qty, price, status) in enumerate(self.cart_items):
                if name == item:
                    self.cart_items[i] = (name, pid, qty + requested_qty, price, status)
                    self.total_price += requested_qty * price
                    self.refresh_cart_treeview()
                    self.total_label.configure(text=f"Total: RM {self.total_price:.2f}")
                    self.quantity_entry.delete(0, 'end')

                    if self.on_cart_update:
                        self.on_cart_update(self.cart_items, self.total_price)
                    return

            # Add new item
            self.cart_items.append((item, prod_id, requested_qty, price, status))
            self.total_price += requested_qty * price
            self.refresh_cart_treeview()
            self.total_label.configure(text=f"Total: RM {self.total_price:.2f}")
            self.quantity_entry.delete(0, 'end')

            if self.on_cart_update:
                self.on_cart_update(self.cart_items, self.total_price)

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
        self.calc_entry.configure(text="")
        self.quantity_entry.delete(0, 'end')

        if self.on_cart_update:
            self.on_cart_update(self.cart_items, self.total_price)

    def pay_order(self):
        if not self.cart_items:
            messagebox.showwarning("Payment", "Cart is empty.")
            return
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        PaymentFrame(parent=self.main_frame, total_amount=self.total_price, cart_items=self.cart_items.copy(), on_payment_complete=self.clear_cart_and_reload, on_cancel=lambda: self.reload_dashboard_content(keep_cart=True)).pack(fill="both", expand=True)

    def reload_dashboard_content(self, keep_cart=False):
        # Preserve cart and total only if keep_cart is True
        current_cart = self.cart_items if keep_cart else []
        current_total = self.total_price if keep_cart else 0.0

        # Destroy everything in the parent container (root frame)
        for widget in self.parent.winfo_children():
            widget.destroy()

        # Recreate Dashboard with or without cart
        Dashboard(self.parent, self.cashier_username, current_cart, current_total)

    def clear_cart_and_reload(self):
        self.cart_items.clear()
        self.total_price = 0.0
        self.reload_dashboard_content()

    def update_dashboard_cart(self, cart_items, total_price):
        self.dashboard_cart_items = cart_items
        self.dashboard_total_price = total_price

    def create_calculator(self):
        calc_frame = ctk.CTkFrame(self.main_frame, fg_color="#eaf9ff", border_color="#0C5481", border_width=2, corner_radius=10)
        calc_frame.grid(row=1, column=1, sticky="n", padx=10, pady=20)

        # Total Display Frame (adjusted)
        total_frame = ctk.CTkFrame(self.main_frame, fg_color="#eaf9ff", border_color="#0C5481", border_width=2, corner_radius=10)
        total_frame.grid(row=0, column=1, sticky="n", padx=10, pady=(30, 10), ipadx=10, ipady=10)

        # Total Label inside Frame
        self.total_label = ctk.CTkLabel(total_frame, text="Total: RM 0.00", fg_color="#eaf9ff", text_color="#0C5481", font=("Arial", 20, "bold"), corner_radius=8, width=260, height=80, justify="center")
        self.total_label.pack(padx=10, pady=10)

        self.calc_entry = ctk.CTkLabel(calc_frame, text="", width=280, height=50, anchor="e", font=("Arial", 18))
        self.calc_entry.grid(row=0, column=0, columnspan=4, padx=5, pady=5)

        buttons = [
            ('1', 1, 0), ('2', 1, 1), ('3', 1, 2), ('AC', 1, 3),
            ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('⌫', 2, 3),
            ('7', 3, 0), ('8', 3, 1), ('9', 3, 2), ('+', 3, 3),
            ('.', 4, 0), ('0', 4, 1), ('x', 4, 2),
            ('%', 5, 0), ('/', 5, 1), ('-', 5, 2), ('=', 5, 3)
        ]

        for key, row, col in buttons:
            height = 100 if key == '+' else 50
            rowspan = 2 if key == '+' else 1
            btn = ctk.CTkButton(
                calc_frame,
                text=key, width=60, height=height, fg_color="#cce7f9", border_color="#0C5481",border_width=2, text_color="#0C5481",
                font=("Arial", 24, "bold"), corner_radius=8, hover_color="#8dc0f7", command=lambda k=key: self.on_calc_button_press(k))
            if key == '+':
                btn.grid(row=row, column=col, rowspan=rowspan, padx=5, pady=5, sticky="ns")
            else:
                btn.grid(row=row, column=col, sticky="n", padx=5, pady=(0, 5))

    def on_calc_button_press(self, key):
        current = self.calc_entry.cget("text")
        if key == "AC":
            self.calc_entry.configure(text="")
        elif key == "⌫":
            self.calc_entry.configure(text=current[:-1])
        elif key == "=":
            try:
                expression = current.replace("x", "*").replace("%", "/100")
                result = eval(expression)
                rounded = round(result, 2)
                self.calc_entry.configure(text=str(rounded))
                self.total_price += rounded
                self.total_label.configure(text=f"Total: RM {self.total_price:.2f}")
            except:
                self.calc_entry.configure(text="Error")
        else:
            self.calc_entry.configure(text=current + key)

    def load_icon(self, filename, size=(30, 30)):
        path = os.path.join("images", filename)
        return ctk.CTkImage(Image.open(path), size=size) if os.path.exists(path) else None

def load_dashboard_content(parent, cashier_username, cart_items=None, total_price=0.0, on_cart_update=None):
    return Dashboard(parent, cashier_username, cart_items, total_price, on_cart_update)

