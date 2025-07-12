import customtkinter as ctk
from tkinter import messagebox
import sqlite3
from datetime import datetime
import tempfile
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class PaymentFrame(ctk.CTkFrame):
    def __init__(self, parent, total_amount, cart_items, on_payment_complete, on_cancel, discount_amount=0.0, tax_amount=0.0):
        super().__init__(parent, fg_color="white")

        self.cart_items = cart_items
        self.on_payment_complete = on_payment_complete
        self.on_cancel = on_cancel
        self.last_invoice = None
        self.last_payment_method = None
        self.last_receipt_text = ""
        self.discount_amount = discount_amount
        self.tax_amount = tax_amount
        self.original_total = total_amount
        self.net_total = round(total_amount, 2)
        self.total_amount = round(self.net_total  - self.discount_amount, 2)

        self.ensure_sales_table_exists()

        self.grid_columnconfigure((0, 1, 2), weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

        # --- Receipt Section (Left Panel) ---
        self.receipt_frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
            border_width=2,
            border_color="#0C5481",
            width=400,
            height=600
        )
        self.receipt_frame.grid(row=0, column=0, sticky="nsew", padx=30, pady=10)
        self.receipt_frame.grid_propagate(False)

        # --- Inner Container for padding and layout ---
        receipt_inner = ctk.CTkFrame(self.receipt_frame, fg_color="#f8f9fa")
        receipt_inner.pack(fill="both", expand=True, padx=5, pady=5)

        # --- Frame for Receipt Textbox and Scrollbar ---
        receipt_text_frame = ctk.CTkFrame(receipt_inner, fg_color="#f8f9fa")
        receipt_text_frame.pack(fill="both", expand=True, padx=10, pady=(20, 5))

        # --- Textbox ---
        self.receipt_box = ctk.CTkTextbox(
            receipt_text_frame,
            font=("Courier", 13),
            fg_color="white",
            text_color="black",
            border_width=1,
            border_color="#ccc"
        )
        self.receipt_box.pack(side="left", fill="both", expand=True)

        # --- Scrollbar ---
        self.receipt_scroll_y = ctk.CTkScrollbar(
            receipt_text_frame,
            orientation="vertical",
            command=self.receipt_box.yview,
            fg_color="#e9ecef",
            button_color= "#0C5481",
            button_hover_color="#0394fc"
        )
        self.receipt_scroll_y.pack(side="right", fill="y")
        self.receipt_box.configure(yscrollcommand=self.receipt_scroll_y.set)

        # --- Receipt Button Frame (Print & Done) ---
        self.receipt_button_frame = ctk.CTkFrame(receipt_inner, fg_color="#0C5481")
        self.receipt_button_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.print_btn = ctk.CTkButton(
            self.receipt_button_frame,
            text="\U0001F5A8 Print Receipt",
            command=self.print_receipt,
            fg_color="#5cb85c",
            hover_color="#4cae4c",
            text_color="white",
            font=("Arial", 13, "bold"),
            width=120
        )
        self.print_btn.pack(side="left", padx=20, pady=5)

        self.done_btn = ctk.CTkButton(
            self.receipt_button_frame,
            text="✓ Done",
            command=self.on_payment_complete,
            fg_color="#0275d8",
            hover_color="#025aa5",
            text_color="white",
            font=("Arial", 13, "bold"),
            width=120
        )
        self.done_btn.pack(side="right", padx=20, pady=5)

        # Insert default receipt message
        self.receipt_box.insert("1.0", "\n\n\n\n\n\n\n\n\n\n     Receipt will appear here after payment.")
        self.receipt_box.configure(state="disabled")

        # Payment Options (Middle)
        self.options_frame = ctk.CTkFrame(self, fg_color="white")
        self.options_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        ctk.CTkLabel(self.options_frame, text="Payment Options", font=("Arial", 24, "bold"), text_color="#0C5481").pack(
            pady=(30, 10))

        # 1. BUTTONS FIRST
        self.button_frame = ctk.CTkFrame(self.options_frame, fg_color="white")
        self.button_frame.pack(pady=10)

        buttons = [
            ("\U0001F4B5  Cash", self.pay_cash),
            ("\U0001F3E7  Debit Card", self.open_debit_card_window),
            ("\U0001F4F7  DuitNow QR", self.open_duitnow_qr_window),

        ]

        self.payment_buttons = []  # Store all references here

        for name, command in buttons:
            btn = ctk.CTkButton(
                self.button_frame,
                text=name,
                command=command,
                width=450,
                height=80,
                fg_color="#0C5481",
                hover_color="#2874ed",
                text_color="white",
                font=("Arial", 14, "bold")
            )
            btn.pack(pady=15)

            self.payment_buttons.append(btn)  # Store button

        # Cash Input Frame (Enlarged & Refined)
        self.cash_input_frame = ctk.CTkFrame(
            self.options_frame,
            fg_color="#f1f1f1",
            border_width=2,
            border_color="#0C5481",
            width=450,
            height=320  # Increased height
        )
        self.cash_input_frame.pack(pady=10)
        self.cash_input_frame.pack_propagate(False)

        # Cash Title
        ctk.CTkLabel(
            self.cash_input_frame,
            text="💵 Cash Payment",
            font=("Arial", 20, "bold"),
            text_color="#0C5481"
        ).pack(pady=(10, 5))

        # Cash Entry
        self.cash_entry = ctk.CTkEntry(
            self.cash_input_frame,
            placeholder_text="Enter cash amount",
            font=("Arial", 16),
            width=290,
            height=60,
            justify="center"
        )
        self.cash_entry.pack(pady=5)

        # Quick Cash Buttons (Organized with better spacing)
        self.cash_button_frame = ctk.CTkFrame(self.cash_input_frame, fg_color="#f1f1f1")
        self.cash_button_frame.pack(pady=10)

        cash_values = [10, 20, 30, 40, 50, 100]
        for index, val in enumerate(cash_values):
            row = 0 if index < 3 else 1
            col = index % 3
            btn = ctk.CTkButton(
                self.cash_button_frame,
                text=f"RM {val}",
                width=120,
                height=80,
                fg_color="#0C5481",
                hover_color="#2874ed",
                text_color="white",
                font=("Arial", 14, "bold"),
                command=lambda v=val: self.add_cash_value(v)
            )
            btn.grid(row=row, column=col, padx=6, pady=6)

        # Right Side Panel (Calculator + Cash Input)
        self.right_panel = ctk.CTkFrame(self, fg_color="white")
        self.right_panel.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)

        # Back Button at the top
        self.back_btn = ctk.CTkButton(
            self.right_panel, text="← Back to Dashboard", command=self.on_cancel,
            fg_color="#d9534f", hover_color="#c9302c", text_color="white",
            font=("Arial", 14, "bold"), width=220, height=40
        )
        self.back_btn.pack(pady=(0, 20))

        self.calc_frame = ctk.CTkFrame(
            self.right_panel,
            fg_color="#f8f9fa",
            border_width=2,
            border_color="#0C5481",
            width=360,
            height=330
        )
        self.calc_frame.pack(padx=10, pady=(0, 0))  # Removed top padding
        self.calc_frame.pack_propagate(False)

        # Calculator Buttons Grid
        buttons = [
            ('1', 2, 0), ('2', 2, 1), ('3', 2, 2), ('AC', 2, 3),
            ('4', 3, 0), ('5', 3, 1), ('6', 3, 2), ('⌫', 3, 3),
            ('7', 4, 0), ('8', 4, 1), ('9', 4, 2), ('+', 4, 3),
            ('.', 5, 0), ('0', 5, 1), ('x', 5, 2),
            ('%', 6, 0), ('/', 6, 1), ('-', 6, 2), ('=', 6, 3)
        ]

        for key, row, col in buttons:
            height = 100 if key == '+' else 50
            rowspan = 2 if key == '+' else 1

            btn = ctk.CTkButton(
                self.calc_frame,
                text=key,
                width=90,
                height=70,
                fg_color="#cce7f9",
                border_color="#0C5481",
                border_width=2,
                text_color="#0C5481",
                font=("Arial", 24, "bold"),
                corner_radius=8,
                hover_color="#8dc0f7",
                command=lambda k=key: self.on_calc_button_press(k)
            )

            if key == '+':
                btn.grid(row=row, column=col, rowspan=rowspan, padx=5, pady=5, sticky="ns")
            else:
                btn.grid(row=row, column=col, padx=5, pady=5, sticky="n")

        self.total_summary_frame = ctk.CTkFrame(
            self.right_panel,
            fg_color="#f8f9fa",
            border_color="#0C5481",
            border_width=2,
            width=400,
            height=280  # ✅ Set desired height
        )
        self.total_summary_frame.pack(side="bottom", padx=10, pady=(10, 15))
        self.total_summary_frame.pack_propagate(False)  # ✅ Important to lock height

        # Helper function to create rows
        def add_row(label, value, bold=False, color=None):
            font_style = ("Arial", 24, "bold") if bold else ("Arial", 24)
            text_color = color if color else "#0C5481"

            row_frame = ctk.CTkFrame(self.total_summary_frame, fg_color="#f8f9fa")
            row_frame.pack(fill="x", pady=10, padx=5)

            ctk.CTkLabel(row_frame, text=label, font=font_style, text_color=text_color).pack(side="left", padx=(10, 0))
            ctk.CTkLabel(row_frame, text=value, font=font_style, text_color=text_color).pack(side="right", padx=(0, 10))

        # Data rows
        add_row("Total Net before Tax:", f"RM {self.original_total- self.tax_amount:.2f}")
        add_row("Discount:", f"-RM {self.discount_amount:.2f}", color="red")
        add_row("Service Tax (6%):", f"+RM {self.tax_amount:.2f}")
        add_row("Total Cost after Tax:", f"RM {self.total_amount:.2f}", bold=True)
        total_quantity = sum(q for _, _, q, _, _ in self.cart_items)
        add_row("Total Quantity:", str(total_quantity))

    def on_calc_button_press(self, key):
        current = self.cash_entry.get()
        if key == "AC":
            self.cash_entry.delete(0, "end")
        elif key == "⌫":
            self.cash_entry.delete(0, "end")
            self.cash_entry.insert(0, current[:-1])
        elif key == "=":
            try:
                expression = current.replace("x", "*").replace("%", "/100")
                result = eval(expression)
                self.cash_entry.delete(0, "end")
                self.cash_entry.insert(0, str(round(result, 2)))
            except:
                self.cash_entry.delete(0, "end")
                self.cash_entry.insert(0, "Error")
        else:
            self.cash_entry.insert("end", key)

    def ensure_sales_table_exists(self):
        try:
            conn = sqlite3.connect("Trackwise.db")
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sales (
                    invoice_id TEXT,
                    product_id TEXT,
                    category TEXT,
                    item_name TEXT,
                    quantity_sold INTEGER,
                    unit_price REAL,
                    sale_date TEXT,
                    total_price REAL
                )
            """)
            conn.commit()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to ensure 'sales' table exists:\n{e}")
        finally:
            conn.close()

    def add_cash_value(self, value):
        """Adds the selected cash button value to the cash entry."""
        current = self.cash_entry.get()
        try:
            current_val = float(current) if current else 0.0
        except ValueError:
            current_val = 0.0
        updated_val = current_val + value
        self.cash_entry.delete(0, "end")
        self.cash_entry.insert(0, f"{updated_val:.2f}")


    def confirm_payment(self, method):
        if messagebox.askyesno("Confirm Payment", f"Confirm {method} payment of RM {self.total_amount:.2f}?"):
            invoice_id = self.record_sales(method)
            self.last_invoice = invoice_id
            self.last_payment_method = method
            self.show_receipt(invoice_id, method)

    def pay_cash(self):
        input_value = self.cash_entry.get()
        try:
            amount_given = float(input_value)
            if amount_given < self.total_amount:
                messagebox.showerror("Insufficient", f"Received RM {amount_given:.2f}, which is less than total.")
                return
            balance = amount_given - self.total_amount
            invoice_id = self.record_sales("Cash")
            self.last_invoice = invoice_id
            self.last_payment_method = "Cash"
            self.show_receipt(invoice_id, "Cash", balance)
        except (ValueError, TypeError):
            messagebox.showerror("Invalid Input", "Please enter a valid number in the cash input.")

    def record_sales(self, method):
        now = datetime.now()
        invoice_id = now.strftime("%d%m%Y%H%M%S")
        sale_date = now.isoformat(timespec='seconds')

        try:
            conn = sqlite3.connect("Trackwise.db")
            cursor = conn.cursor()

            for item_name, product_id, quantity, price, status in self.cart_items:
                total_price = float(price) * int(quantity)

                cursor.execute("SELECT category FROM inventory WHERE product_id = ?", (product_id,))
                result = cursor.fetchone()
                category = result[0] if result else "Unknown"

                cursor.execute("""
                    INSERT INTO sales (
                        invoice_id, product_id, category, item_name, quantity_sold,
                        unit_price, sale_date, total_price
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (invoice_id, product_id, category, item_name, quantity, price, sale_date, total_price))

                cursor.execute("UPDATE inventory SET quantity = quantity - ? WHERE product_id = ?",
                               (quantity, product_id))

                cursor.execute("SELECT quantity FROM inventory WHERE product_id = ?", (product_id,))
                result = cursor.fetchone()
                if result:
                    current_qty = result[0]
                    new_status = "Low Stock" if 0 < current_qty < 5 else "Out of Stock" if current_qty == 0 else "In Stock"
                    cursor.execute("UPDATE inventory SET status = ? WHERE product_id = ?", (new_status, product_id))

                    if current_qty < 5:
                        warning_msg = f"'{item_name}' stock is low ({current_qty})." if current_qty > 0 else f"'{item_name}' is out of stock."
                        messagebox.showwarning("Stock Alert", warning_msg)
                        self.notify_admins_low_stock(item_name, current_qty)

            conn.commit()
            conn.close()
            messagebox.showinfo("Payment Successful", f"Transaction recorded successfully.\nInvoice ID: {invoice_id}")
            return invoice_id

        except Exception as e:
            messagebox.showerror("Sales Error", f"Failed to record sales:\n{e}")
            return None

    def open_debit_card_window(self):
        from debit_card_window import DebitCardWindow
        DebitCardWindow(self, self.total_amount, self.handle_debit_payment)

    def handle_debit_payment(self, card_info):
        """Callback function after debit card details are entered"""
        # Optional: validate card_info here or log them
        self.confirm_payment("Debit Card")

    def open_duitnow_qr_window(self):
        if hasattr(self, "duitnow_window") and self.duitnow_window.winfo_exists():
            self.duitnow_window.lift()
            self.duitnow_window.focus_force()
            return

        from duitnow_qr_window import DuitNowQRWindow
        self.duitnow_window = DuitNowQRWindow(self, self.total_amount, self.handle_duitnow_payment)

    def open_duitnow_qr_window(self):
        if hasattr(self, "duitnow_window") and self.duitnow_window.winfo_exists():
            self.duitnow_window.lift()
            self.duitnow_window.focus_force()
            return

        from duitnow_qr_window import DuitNowQRWindow
        self.duitnow_window = DuitNowQRWindow(self, self.total_amount, self.handle_duitnow_payment)

    def handle_duitnow_payment(self, _):
        self.confirm_payment("DuitNow QR")

    def notify_admins_low_stock(self, item_name, current_qty):
        try:
            conn = sqlite3.connect("Trackwise.db")
            cursor = conn.cursor()

            # Get all admin emails
            cursor.execute("SELECT email FROM users WHERE role = 'Admin'")
            admin_emails = [row[0] for row in cursor.fetchall()]
            conn.close()

            if not admin_emails:
                print("No admin emails found.")
                return

            sender_email = "ruxinthean@gmail.com"
            sender_password = "vznn pcdo pnol oiqf"

            # Email content
            subject = f"⚠️ Low Stock Alert: {item_name}"
            if current_qty == 0:
                status_text = f"The item '{item_name}' is now OUT OF STOCK."
            else:
                status_text = f"The stock for item '{item_name}' is LOW. Only {current_qty} units left."

            body = (
                f"Dear Admin,\n\n"
                f"{status_text}\n\n"
                f"Please take necessary action to restock.\n\n"
                f"Regards,\nTrackwise POS System"
            )

            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart

            for admin_email in admin_emails:
                msg = MIMEMultipart()
                msg["From"] = sender_email
                msg["To"] = admin_email
                msg["Subject"] = subject
                msg.attach(MIMEText(body, "plain"))

                with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                    server.login(sender_email, sender_password)
                    server.send_message(msg)

            messagebox.showinfo("Email Sent", f"Stock alert email has been sent to all admins.")

        except Exception as e:
            messagebox.showerror("Email Error", f"Failed to send low stock email:\n{e}")

    def show_receipt(self, invoice_id, method, balance=None):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        total_quantity = sum(q for _, _, q, _, _ in self.cart_items)

        receipt_lines = [
            "=" * 42,
            "        Trackwise Product Store",
            "    No. 5, Main Street, KL, Malaysia",
            "         Tel: 012-3456789",
            f"\nInvoice ID:        {invoice_id}",
            f"Date:              {now}",
            f"Payment Method:    {method}",
            f"Total Quantity:    {total_quantity}",
            "-" * 42,
            "Item Name            Qty   Unit  Subtotal",
            "                                   (RM)",
            "-" * 42,
        ]

        for item_name, _, quantity, price, _ in self.cart_items:
            subtotal = float(price) * int(quantity)
            receipt_lines.append(f"{item_name:<22}{quantity:<4}{price:<6}{subtotal:>8.2f}")

        receipt_lines.append("-" * 42)

        # ✅ Use net before tax here
        net_before_tax = self.original_total - self.tax_amount
        receipt_lines.append(f"Net:                        RM {net_before_tax:>8.2f}")

        if self.discount_amount > 0:
            receipt_lines.append(f"Discount:                  -RM {self.discount_amount:>8.2f}")
        if self.tax_amount > 0:
            receipt_lines.append(f"Tax (6%):                  +RM {self.tax_amount:>8.2f}")

        receipt_lines.append(f"Total Amount:               RM {self.total_amount:>8.2f}")

        # ✅ Add Amount Paid and Change if cash payment
        if method == "Cash":
            amount_given = float(self.cash_entry.get())
            receipt_lines.append(f"Amount Paid:                RM {amount_given:>8.2f}")
            receipt_lines.append(f"Change to Return:           RM {balance:>8.2f}")

        receipt_lines.append("-" * 42)
        receipt_lines.append("\n      Thank you for shopping with us!")
        receipt_lines.append("  Track your order with Invoice ID above.")
        receipt_lines.append("  ***NOT VALID FOR REFUND OR EXCHANGE***")
        receipt_lines.append("           Flawless POS System")
        receipt_lines.append("=" * 42)

        receipt_str = "\n".join(receipt_lines)
        self.last_receipt_text = receipt_str

        self.receipt_box.configure(state="normal")
        self.receipt_box.delete("1.0", "end")
        self.receipt_box.insert("1.0", receipt_str)
        self.receipt_box.configure(state="disabled")

    def print_receipt(self):
        if not self.last_receipt_text:
            messagebox.showinfo("No Receipt", "Please complete a payment first.")
            return

        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8") as f:
            f.write(self.last_receipt_text)
            temp_filename = f.name

        os.startfile(temp_filename, "print")