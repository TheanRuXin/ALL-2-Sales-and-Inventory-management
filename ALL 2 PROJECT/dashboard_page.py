# dashboard_page.py
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import os
import datetime
import sqlite3


class Dashboard:
    def __init__(self, parent, cashier_name="Cashier"):
        self.parent = parent
        self.cashier_name = cashier_name
        self.cart_items = []
        self.total_price = 0.0

        # Configure root
        self.parent.rowconfigure(0, weight=1)
        self.parent.columnconfigure(0, weight=1)
        self.parent.configure(fg_color="white")

        # Master frame to hold everything
        self.main_frame = ctk.CTkFrame(self.parent, fg_color="white")
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.main_frame.rowconfigure(1, weight=1)  # For cart table expansion
        self.main_frame.columnconfigure(1, weight=3)  # Center panel wider
        self.load_dashboard_content()

    def load_dashboard_content(self):
        from tkinter import ttk

        # User icon and cashier name display
        user_icon = self.load_icon("user1.png", size=(40, 40))  # Ensure this image exists

        self.user_frame = ctk.CTkFrame(self.main_frame, fg_color="white")
        self.user_frame.grid(row=0, column=0, sticky="nw", padx=30, pady=20)
        self.user_icon_label = ctk.CTkLabel(self.user_frame, image=user_icon, text="")
        self.user_icon_label.image = user_icon
        self.user_icon_label.pack(side="left", padx=(0, 10))
        self.user_name_label = ctk.CTkLabel(self.user_frame, text=f"Welcome, {self.cashier_name}", font=("Arial", 16, "bold"), text_color="#0C5481")
        self.user_name_label.pack(side="left")

        # Panel to hold dropdowns and buttons
        panel = ctk.CTkFrame(self.main_frame, fg_color="white")
        panel.grid(row=1, column=0, padx=30, pady=10, sticky="nw")

        # Dropdown: Category
        self.category_var = ctk.StringVar(value="Select Category")
        self.category_dropdown = ctk.CTkComboBox(
            panel,
            values=self.fetch_categories(),
            variable=self.category_var,
            width=210,
            height=35,
            command=self.update_items_dropdown,
            text_color="#0882c4",
            fg_color="#cce7f9",
            border_color="#0C5481",
            border_width=2,
            dropdown_fg_color="#cce7f9",
            dropdown_text_color="#014894",
            dropdown_font=("Inter", 14),
            dropdown_hover_color="#8dc0f7",
            button_color="#0C5481",
            button_hover_color="#2874ed"
        )
        self.category_dropdown.grid(row=0, column=0, padx=10, pady=10)

        # Dropdown: Items
        self.item_var = ctk.StringVar(value="Select Item")
        self.item_dropdown = ctk.CTkComboBox(
            panel,
            values=["Select a Category First"],
            variable=self.item_var,
            width=210,
            height=35,
            text_color="#0882c4",
            fg_color="#cce7f9",
            border_color="#0C5481",
            border_width=2,
            dropdown_fg_color="#cce7f9",
            dropdown_text_color="#014894",
            dropdown_font=("Inter", 14),
            dropdown_hover_color="#8dc0f7",
            button_color="#0C5481",
            button_hover_color="#2874ed"
        )
        self.item_dropdown.grid(row=0, column=1, padx=10, pady=10)

        # Quantity
        self.quantity_entry = ctk.CTkEntry(panel, text_color="#0C5481", fg_color="#cce7f9", height=35, placeholder_text="Quantity", placeholder_text_color="#0882c4", border_color="#0C5481", width=210)
        self.quantity_entry.grid(row=0, column=2, padx=10, pady=10)

        # Button styling config
        button_config = {
            "width": 140,
            "height": 35,
            "fg_color": "#0C5481",
            "hover_color": "#2874ed",
            "text_color": "white",
            "font": ("Arial", 14, "bold"),
            "corner_radius": 8
        }

        # New button panel below Treeview
        button_panel = ctk.CTkFrame(self.parent, fg_color="white")
        button_panel.place(x=10, y=580)  # Adjust `y` based on your layout

        ctk.CTkButton(button_panel, text="Add to Cart", command=self.add_to_cart, **button_config).grid(row=0, column=0, padx=10, pady=10)
        ctk.CTkButton(button_panel, text="Pay (Cash)", command=self.pay_cash, **button_config).grid(row=0, column=1, padx=10, pady=10)
        ctk.CTkButton(button_panel, text="Pay (Debit)", command=self.pay_order, **button_config).grid(row=0, column=2, padx=10, pady=10)
        ctk.CTkButton(button_panel, text="Print Receipt", command=self.print_receipt, **button_config).grid(row=0, column=3, padx=10, pady=10)

        # Treeview Cart Table
        self.cart_table = ctk.CTkFrame(self.parent, bg_color="#eaf9ff", fg_color="#eaf9ff", width=700, height=100, corner_radius=10)
        self.cart_table.place(x=10, y=200)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview.Heading", background="#0C5481", foreground="white", font=("Arial", 14, "bold"))
        style.configure("Treeview", background="#eaf9ff", foreground="#057687", fg_color="#057687", rowheight=30, fieldbackground="#cce7f9")


        columns = ("Name", "Product ID", "Quantity", "Price", "Status")
        self.tree = ttk.Treeview(self.cart_table, columns=columns, show="headings", height=14)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", stretch=True)
            self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ctk.CTkScrollbar(self.cart_table, button_color="#84d4e0", button_hover_color="#cce7f9", fg_color="#0C5481", orientation="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Calculator
        self.create_calculator()

        # Bottom Buttons (Horizontally aligned)
        btn_y = 590
        ctk.CTkButton(self.main_frame, text="Delete Item", command=self.delete_last_item, width=140, height=35,fg_color="#0C5481", hover_color="#2874ed", text_color="white", font=("Arial", 13, "bold")).place( x=660, y=btn_y)
        ctk.CTkButton(self.main_frame, text="Cancel Order", command=self.cancel_order, width=140, height=35, fg_color="#d9534f", hover_color="#c9302c", text_color="white", font=("Arial", 13, "bold")).place(x=810, y=btn_y)
        ctk.CTkButton(self.main_frame, text="Pay Now", command=self.pay_order, width=140, height=35, fg_color="#5cb85c", hover_color="#4cae4c", text_color="white", font=("Arial", 13, "bold")).place(x=960, y=btn_y)

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
                return [row[0] for row in cursor.fetchall()] or ["No Items Available"]
        except:
            return ["No Items Available"]

    def update_items_dropdown(self, _):
        items = self.fetch_items_by_category(self.category_var.get())
        self.item_dropdown.configure(values=items)

    def create_image_button(self, parent, image_file, command, size=(120, 40)):
        path = os.path.join("images", image_file)
        if not os.path.exists(path):
            return ctk.CTkLabel(parent, text="Missing Image")
        img = ctk.CTkImage(Image.open(path), size=size)
        btn = ctk.CTkLabel(parent, image=img, text="")
        btn.image = img
        btn.bind("<Button-1>", lambda e: command())
        return btn

    def add_to_cart(self):
        item = self.item_var.get()
        quantity_text = self.quantity_entry.get()
        if item in ("Select Item", "Select a Category First") or not quantity_text.isdigit():
            messagebox.showwarning("Input Error", "Please select a valid item and enter quantity.")
            return
        quantity = int(quantity_text)
        with sqlite3.connect('Trackwise.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT price, status FROM inventory WHERE item_name = ?", (item,))
            result = cursor.fetchone()
        if result:
            price, status = result
            subtotal = quantity * price
            self.total_price += subtotal
            self.cart_items.append((item, quantity, price, status))
            self.total_label = ctk.CTkLabel(
                self.main_frame,
                text="Total: RM 0.00",
                font=("Arial", 20, "bold"),
                text_color="white",
                width=300,
                height=60,
                corner_radius=15
            )
            self.total_label.place(x=50, y=400)
            self.tree.insert("", "end", values=(item, quantity, f"{price:.2f}", status))

    def clear_cart(self):
        self.cart_items.clear()
        self.total_price = 0.0
        self.tree.delete(*self.tree.get_children())
        self.total_label.configure(text="Total: RM 0.00")
        self.calc_entry.delete(0, 'end')
        self.quantity_entry.delete(0, 'end')

    def cancel_order(self):
        if messagebox.askyesno("Cancel", "Are you sure you want to cancel the order?"):
            self.clear_cart()

    def delete_last_item(self):
        if not self.cart_items:
            messagebox.showinfo("Empty Cart", "There are no items to delete.")
            return

        # Remove last item from internal cart
        last_item = self.cart_items.pop()
        self.total_price -= last_item[2] * last_item[1]

        # Remove last row from Treeview
        children = self.tree.get_children()
        if children:
            self.tree.delete(children[-1])

        # Update total label
        self.total_label.configure(text=f"Total: RM {self.total_price:.2f}")

    def pay_cash(self):
        if not self.cart_items:
            messagebox.showwarning("Payment", "Cart is empty.")
            return
        if messagebox.askyesno("Cash Payment", f"Confirm cash payment of RM {self.total_price:.2f}?"):
            messagebox.showinfo("Payment Successful", "Cash payment received. Thank you!")
            self.clear_cart()

    def pay_order(self):
        if not self.cart_items:
            messagebox.showwarning("Payment", "Cart is empty.")
            return
        messagebox.showinfo("Payment", f"Debit payment of RM {self.total_price:.2f} accepted.")
        self.clear_cart()

    def print_receipt(self):
        if not self.cart_items:
            messagebox.showerror("Error", "Cart is empty.")
            return
        now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"receipt_{now}.txt"
        with open(filename, "w") as f:
            f.write("----- RECEIPT -----\n")
            for item, qty, price, _ in self.cart_items:
                f.write(f"{item} x{qty} - RM {qty * price:.2f}\n")
            f.write(f"\nTotal: RM {self.total_price:.2f}\n")
            f.write(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("Thank you for your purchase!\n")
        os.system(f"notepad {filename}")

    def create_calculator(self):
        calc_frame = ctk.CTkFrame(self.main_frame, fg_color="#eaf9ff", width=300, height=300, border_color="#0C5481", border_width=2, corner_radius=10)
        calc_frame.place(x=840, y=200)

        self.total_label = ctk.CTkLabel(
            self.parent,
            text="Total",
            fg_color="#eaf9ff",  # light background
            text_color="black",  # dark text for contrast
            font=("Helvetica", 16, "bold"),
            corner_radius=8,
            width=300,
            height=50,
            justify="center",
        )
        self.total_label.place(x=830, y=90)

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
                text=key,
                width=60,
                height=height,
                fg_color="#cce7f9",  # Background color
                border_color="#0C5481",  # Border color
                border_width=2,  # Border thickness (if supported)
                text_color="#0C5481",
                font=("Arial", 24, "bold"),
                corner_radius=8,
                hover_color="#8dc0f7",
                command=lambda k=key: self.on_calc_button_press(k)
            )
            if key == '+':
                btn.grid(row=row, column=col, rowspan=rowspan, padx=5, pady=5, sticky="ns")
            else:
                btn.grid(row=row, column=col, padx=5, pady=5)

    def load_icon(self, filename, size=(30, 30)):
        path = os.path.join("images", filename)
        if os.path.exists(path):
            return ctk.CTkImage(Image.open(path), size=size)
        return None

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
                rounded_result = round(result, 2)
                self.calc_entry.configure(text=str(rounded_result))
                self.total_price += rounded_result
                self.total_label.configure(text=f"Total: RM {self.total_price:.2f}")
            except:
                self.calc_entry.configure(text="Error")
        else:
            self.calc_entry.configure(text=current + key)


# Entry function to be imported in new.py
def load_dashboard_content(parent):
    Dashboard(parent)


"""

        self.total_frame = ctk.CTkFrame(
            self.main_frame,

            fg_color="#eaf9ff",  # light background
            border_width=4,
            border_color="green",
            corner_radius=8,
            width=300,
            height=100,

        )
        self.total_frame.place(x=830, y=90)

"""