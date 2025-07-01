import customtkinter as ctk
from tkinter import messagebox
import sqlite3
from datetime import datetime
import tempfile
from PIL import Image, ImageTk
import io
import os

class PaymentFrame(ctk.CTkFrame):
    def __init__(self, parent, total_amount, cart_items, on_payment_complete, on_cancel):
        super().__init__(parent, fg_color="white")
        self.total_amount = total_amount
        self.cart_items = cart_items
        self.on_payment_complete = on_payment_complete
        self.on_cancel = on_cancel
        self.last_invoice = None
        self.last_payment_method = None
        self.last_receipt_text = ""

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=2)

        # Left side: receipt display
        self.receipt_frame = ctk.CTkFrame(self, fg_color="#f8f9fa", border_width=2, border_color="#0C5481", width=410)
        self.receipt_frame.grid(row=0, column=0, sticky="ns", padx=10, pady=10)

        self.receipt_box = ctk.CTkTextbox(self.receipt_frame, font=("Courier", 11), wrap="none", width=380)
        self.receipt_box.pack(padx=10, pady=(10, 0), fill="both", expand=True)
        self.receipt_box.insert("1.0", "\n\n\n\n\n\n\n\n\n\n     Receipt will appear here after payment.")
        self.receipt_box.configure(state="disabled")

        # Scrollbars
        self.receipt_scroll_y = ctk.CTkScrollbar(self.receipt_frame, orientation="vertical", command=self.receipt_box.yview, fg_color="#0C5481")
        self.receipt_scroll_y.place(relx=1.0, rely=0, relheight=0.92, anchor="ne")


        self.receipt_box.configure(yscrollcommand=self.receipt_scroll_y.set)

        self.receipt_button_frame = ctk.CTkFrame(self.receipt_frame,  fg_color="#0C5481")
        self.receipt_button_frame.pack(fill="x", pady=5)

        self.print_btn = ctk.CTkButton(self.receipt_button_frame, text="🖨️ Print Receipt", command=self.print_receipt,
                                       fg_color="#5cb85c", hover_color="#4cae4c",
                                       text_color="white", font=("Arial", 13, "bold"), width=120)
        self.print_btn.pack(side="left", padx=20, pady=5)

        self.done_btn = ctk.CTkButton(self.receipt_button_frame, text="✓ Done", command=self.on_payment_complete,
                                      fg_color="#0275d8", hover_color="#025aa5",
                                      text_color="white", font=("Arial", 13, "bold"), width=120)
        self.done_btn.pack(side="right", padx=20, pady=5)

        # Right side: payment options
        self.options_frame = ctk.CTkFrame(self, fg_color="white")
        self.options_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        ctk.CTkLabel(self.options_frame, text="Payment Options", font=("Arial", 24, "bold"), text_color="#0C5481").pack(pady=(30, 10))
        ctk.CTkLabel(self.options_frame, text=f"Total Amount: RM {self.total_amount:.2f}", font=("Arial", 18, "bold")).pack(pady=(0, 5))
        total_quantity = sum(q for _, _, q, _, _ in self.cart_items)
        ctk.CTkLabel(self.options_frame, text=f"Total Quantity: {total_quantity}", font=("Arial", 16)).pack(pady=(0, 10))

        self.button_frame = ctk.CTkFrame(self.options_frame, fg_color="white")
        self.button_frame.pack(pady=10)

        buttons = [
            ("💵  Cash", self.pay_cash),
            ("🏧  Debit Card", lambda: self.confirm_payment("Debit Card")),
            ("💳  Credit Card", lambda: self.confirm_payment("Credit Card")),
            ("🪪  MyKasih", lambda: self.confirm_payment("MyKasih")),
            ("📱  TNG eWallet", lambda: self.confirm_payment("TNG eWallet")),
            ("📷  DuitNow QR", lambda: self.confirm_payment("DuitNow QR")),
        ]

        for name, command in buttons:
            ctk.CTkButton(self.button_frame, text=name, command=command, width=240, height=40,
                          fg_color="#0C5481", hover_color="#2874ed", text_color="white",
                          font=("Arial", 14, "bold")).pack(pady=5)

        ctk.CTkButton(self.options_frame, text="← Back to Dashboard", command=self.on_cancel,
                      fg_color="#d9534f", hover_color="#c9302c", text_color="white",
                      font=("Arial", 14, "bold")).pack(pady=20)

    def confirm_payment(self, method):
        if messagebox.askyesno("Confirm Payment", f"Confirm {method} payment of RM {self.total_amount:.2f}?"):
            invoice_id = self.record_sales(method)
            self.last_invoice = invoice_id
            self.last_payment_method = method
            self.show_receipt(invoice_id, method)


    def pay_cash(self):
        input_popup = ctk.CTkInputDialog(title="Cash Payment", text=f"Total: RM {self.total_amount:.2f}\n\nEnter amount received:")
        input_value = input_popup.get_input()
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
            messagebox.showerror("Invalid Input", "Please enter a valid number.")

    def record_sales(self, method):
        now = datetime.now()
        invoice_id = now.strftime("%d%m%Y%H%M%S")
        sale_date = now.isoformat(timespec='seconds')

        try:
            conn = sqlite3.connect("Trackwise.db")
            cursor = conn.cursor()

            for item_name, product_id, quantity, price, status in self.cart_items:
                total_price = float(price) * int(quantity)

                cursor.execute("""
                    INSERT INTO sales (invoice_id, product_id, item_name, quantity_sold, unit_price, sale_date, total_price)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (invoice_id, product_id, item_name, quantity, price, sale_date, total_price))

                cursor.execute("UPDATE inventory SET quantity = quantity - ? WHERE product_id = ?",
                               (quantity, product_id))

                cursor.execute("SELECT quantity FROM inventory WHERE product_id = ?", (product_id,))
                result = cursor.fetchone()
                if result:
                    current_qty = result[0]
                    new_status = "Low Stock" if current_qty < 5 else "In Stock"
                    cursor.execute("UPDATE inventory SET status = ? WHERE product_id = ?", (new_status, product_id))
                    if current_qty < 5:
                        messagebox.showwarning("Low Stock", f"'{item_name}' stock is low ({current_qty}).")

            conn.commit()
            conn.close()
            return invoice_id

        except Exception as e:
            messagebox.showerror("Sales Error", f"Failed to record sales:\n{e}")
            return None

    def show_receipt(self, invoice_id, method, balance=None):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        total_quantity = sum(q for _, _, q, _, _ in self.cart_items)

        receipt_lines = [
            "================= RECEIPT =================",
            "         Trackwise Product Store",
            "        No. 5, Main Street, KL, Malaysia",
            "         Tel: 012-3456789",
            f"\nInvoice ID:         {invoice_id}",
            f"Date:               {now}",
            f"Payment Method:     {method}",
            f"Total Quantity:     {total_quantity}",
            "\n------------------------------------------",
            "Item Name          Qty   Unit   Subtotal",
            "                                 (RM)",
            "------------------------------------------",
        ]

        for item_name, _, quantity, price, _ in self.cart_items:
            subtotal = float(price) * int(quantity)
            receipt_lines.append(f"{item_name:<17}  {quantity:<4}  {price:<6}  {subtotal:.2f}")

        receipt_lines.append("------------------------------------------")
        receipt_lines.append(f"Total Amount:                 RM {self.total_amount:.2f}")
        if balance is not None:
            receipt_lines.append(f"Change to Return:             RM {balance:.2f}")
        receipt_lines.append("------------------------------------------")
        receipt_lines.append("\nThank you for shopping with us!")
        receipt_lines.append("Track your order with Invoice ID above.")
        receipt_lines.append("***NOT VALID FOR REFUND OR EXCHANGE***")
        receipt_lines.append("==========================================")

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
