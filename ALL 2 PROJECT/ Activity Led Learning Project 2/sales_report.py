import sqlite3
import customtkinter as ctk
from tkinter import ttk
from datetime import datetime
from tkinter import filedialog
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from tkcalendar import DateEntry


class SalesReportPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(fg_color="white")
        self.pack(fill="both", expand=True)

        self.sales_data = []
        self.create_widgets()

        # Automatically set today’s date and load today’s records
        self.from_date.set_date(datetime.now())
        self.to_date.set_date(datetime.now())
        self.load_transaction_summary()

    def create_widgets(self):
        # Title
        ctk.CTkLabel(self, text="📊 Transaction Summary", font=("Arial", 24, "bold"), text_color="#0C5481").pack(pady=(20, 10))

        # Date filter row
        filter_frame = ctk.CTkFrame(self, fg_color="white")
        filter_frame.pack(pady=5)

        self.from_date = DateEntry(
            filter_frame,
            width=30,
            font=("Arial", 14),
            background='#eaf9ff',
            foreground='#057687',
            bordercolor='#eaf9ff',
            date_pattern='yyyy-mm-dd',
            disabledbackground='#eaf9ff',
            disabledforeground='#057687',
        )
        self.from_date.pack(side="left", padx=5)

        self.to_date = DateEntry(
            filter_frame,
            width=30,
            font=("Arial", 14),
            background='#eaf9ff',
            foreground='#057687',
            bordercolor='#eaf9ff',
            date_pattern='yyyy-mm-dd',
            disabledbackground='#eaf9ff',
            disabledforeground='#057687',
        )
        self.to_date.pack(side="left", padx=5)

        filter_btn = ctk.CTkButton(filter_frame,fg_color="#0C5481", hover_color="#0882c4", text="🔍 Filter", command=self.load_transaction_summary)
        filter_btn.pack(side="left", padx=5)

        # Table Frame
        self.table_frame = ctk.CTkFrame(self, fg_color="#eaf9ff", corner_radius=10)
        self.table_frame.pack(padx=30, pady=10, fill="both", expand=True)

        # Treeview + Scrollbar Container
        tree_container = ctk.CTkFrame(self.table_frame, fg_color="#eaf9ff")
        tree_container.pack(fill="both", expand=True)

        # Treeview styling
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview.Heading",
                        background="#0C5481", foreground="white",
                        font=("Arial", 15, "bold"))
        style.configure("Treeview",
                        background="#eaf9ff",
                        foreground="#057687",
                        rowheight=30,
                        fieldbackground="#eaf9ff",
                        font=("Arial", 14))

        # 💡 Make selection visible like the heading
        style.map("Treeview",
                  background=[("selected", "#0C5481")],
                  foreground=[("selected", "white")])

        columns = ("invoice_id", "sale_date", "total_items", "total_price")
        self.tree = ttk.Treeview(tree_container, columns=columns, show="headings", height=18)

        for col in columns:
            self.tree.heading(col, text={
                "invoice_id": "Invoice ID",
                "sale_date": "Sale Date",
                "total_items": "Total Items",
                "total_price": "Total Amount (RM)"
            }[col])
            self.tree.column(col, anchor="center", width=180)

        self.tree.grid(row=0, column=0, sticky="nsew")

        # Vertical Scrollbar
        scrollbar = ctk.CTkScrollbar(tree_container,
                                     orientation="vertical",
                                     command=self.tree.yview,
                                     fg_color="#0C5481",
                                     button_color="#cce7f9",
                                     button_hover_color="#0882c4")
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Make sure grid expands properly
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)

        # Buttons
        button_frame = ctk.CTkFrame(self, fg_color="white")
        button_frame.pack(pady=(5, 15))

        ctk.CTkButton(button_frame, text="🔄 Refresh", command=self.refresh_summary,
                      fg_color="#0C5481", hover_color="#0882c4").pack(side="left", padx=10)

        ctk.CTkButton(button_frame, text="🖨️ Print", command=self.print_transaction_summary,
                      fg_color="#0C5481", hover_color="#0882c4").pack(side="left", padx=10)

        ctk.CTkButton(button_frame, text="💾 Save as PDF", command=self.save_transaction_summary_pdf,
                      fg_color="#0C5481", hover_color="#0882c4").pack(side="left", padx=10)

    def load_transaction_summary(self):
        self.tree.delete(*self.tree.get_children())
        self.sales_data.clear()

        from_date = self.from_date.get()
        to_date = self.to_date.get()

        query = """
            SELECT 
                invoice_id, 
                sale_date, 
                COUNT(*) as total_items, 
                SUM(total_price) as total_price 
            FROM sales
        """
        conditions = []
        params = []

        if from_date:
            conditions.append("date(sale_date) >= date(?)")
            params.append(from_date)
        if to_date:
            conditions.append("date(sale_date) <= date(?)")
            params.append(to_date)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " GROUP BY invoice_id, sale_date ORDER BY sale_date DESC"

        try:
            conn = sqlite3.connect("Trackwise.db")
            cursor = conn.cursor()
            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()
            conn.close()

            for row in rows:
                invoice_id, sale_date, total_items, total_price = row
                try:
                    sale_date_fmt = datetime.fromisoformat(sale_date).strftime("%Y-%m-%d %H:%M")
                except:
                    sale_date_fmt = sale_date

                self.sales_data.append((invoice_id, sale_date_fmt, total_items, total_price))
                self.tree.insert("", "end", values=(invoice_id, sale_date_fmt, total_items, f"RM {total_price:.2f}"))

        except sqlite3.Error as e:
            print(f"Database error: {e}")

    def refresh_summary(self):
        self.from_date.set_date(datetime.now())
        self.to_date.set_date(datetime.now())
        self.load_transaction_summary()

    def print_transaction_summary(self):
        print("\n📋 Transaction Summary:")
        for row in self.sales_data:
            invoice_id, sale_date, total_items, total_price = row
            print(f"- {invoice_id} | {sale_date} | Items: {total_items} | Total: RM {total_price:.2f}")

    def save_transaction_summary_pdf(self):
        from_date = self.from_date.get().strip()
        to_date = self.to_date.get().strip()

        if from_date and to_date:
            default_name = f"Transaction_Report_{from_date}_to_{to_date}.pdf"
        elif from_date:
            default_name = f"Transaction_Report_from_{from_date}.pdf"
        elif to_date:
            default_name = f"Transaction_Report_to_{to_date}.pdf"
        else:
            today = datetime.now().strftime("%Y-%m-%d")
            default_name = f"Transaction_Report_Today_{today}.pdf"

        file_path = filedialog.asksaveasfilename(
            initialfile=default_name,
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Save Report As"
        )

        if not file_path:
            return

        try:
            pdf = canvas.Canvas(file_path, pagesize=letter)
            width, height = letter

            pdf.setFont("Helvetica-Bold", 16)
            pdf.drawString(40, height - 50, "Transaction Summary Report")

            y = height - 80
            pdf.setFont("Helvetica-Bold", 12)
            pdf.drawString(40, y, "Invoice ID")
            pdf.drawString(150, y, "Sale Date")
            pdf.drawString(300, y, "Total Items")
            pdf.drawString(400, y, "Total (RM)")

            y -= 20
            pdf.setFont("Helvetica", 11)

            for row in self.sales_data:
                invoice_id, sale_date, total_items, total_price = row
                pdf.drawString(40, y, str(invoice_id))
                pdf.drawString(150, y, str(sale_date))
                pdf.drawString(310, y, str(total_items))
                pdf.drawString(410, y, f"{total_price:.2f}")
                y -= 20
                if y < 50:
                    pdf.showPage()
                    y = height - 50

            pdf.save()
            print(f"✅ PDF saved successfully as: {file_path}")

        except Exception as e:
            print("Error saving PDF:", e)


# Called from main dashboard
def load_sales_report_content(parent):
    SalesReportPage(parent)
