import sqlite3
import customtkinter as ctk
from tkinter import ttk
from datetime import datetime

class SalesReportPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.place(relx=0.05, rely=0, relwidth=1, relheight=1)
        self.configure(fg_color="white")

        self.create_widgets()
        self.load_sales_data()

    def create_widgets(self):
        title = ctk.CTkLabel(self, text="📊 Sales Report", font=("Arial", 22, "bold"))
        title.pack(pady=(20, 10))

        table_container = ctk.CTkFrame(self, fg_color="white")
        table_container.pack(padx=20, pady=10, fill="both", expand=True)

        columns = ("invoice_id", "product_id", "item_name", "quantity_sold", "sale_date", "total_price")
        self.tree = ttk.Treeview(
            table_container,
            columns=columns,
            show="headings",
            height=5
        )

        scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

        self.tree.heading("invoice_id", text="Invoice ID")
        self.tree.heading("product_id", text="Product ID")
        self.tree.heading("item_name", text="Item Name")
        self.tree.heading("quantity_sold", text="Quantity Sold")
        self.tree.heading("sale_date", text="Sale Date")
        self.tree.heading("total_price", text="Total Price (RM)")

        self.tree.column("invoice_id", width=150, anchor="center")
        self.tree.column("product_id", width=100, anchor="center")
        self.tree.column("item_name", width=200, anchor="w")
        self.tree.column("quantity_sold", width=120, anchor="center")
        self.tree.column("sale_date", width=150, anchor="center")
        self.tree.column("total_price", width=130, anchor="e")

        refresh_btn = ctk.CTkButton(self, text="🔄 Refresh", command=self.load_sales_data)
        refresh_btn.pack(pady=(5, 15))

    def load_sales_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        try:
            conn = sqlite3.connect("Trackwise.db")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    s.invoice_id, 
                    i.product_id, 
                    s.item_name, 
                    s.quantity_sold, 
                    s.sale_date, 
                    s.total_price
                FROM 
                    sales s
                LEFT JOIN 
                    inventory i ON s.item_name = i.item_name
                ORDER BY 
                    s.sale_date DESC
            """)
            rows = cursor.fetchall()
            conn.close()

            for row in rows:
                invoice_id, product_id, item_name, quantity_sold, sale_date, total_price = row
                try:
                    sale_date = datetime.fromisoformat(sale_date).strftime("%Y-%m-%d %H:%M")
                except:
                    pass
                self.tree.insert("", "end", values=(
                    invoice_id, product_id or "N/A", item_name,
                    quantity_sold, sale_date, f"RM {total_price:.2f}"
                ))
        except sqlite3.Error as e:
            print(f"Database error: {e}")


# Called from Main.py
def load_sales_report_content(parent):
    SalesReportPage(parent)
