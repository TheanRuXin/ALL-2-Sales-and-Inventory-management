import sqlite3
import customtkinter as ctk
from tkcalendar import DateEntry
from tkinter import ttk
import tkinter as tk
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import os
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image


class SalesHistoryPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.screen_width = 1920
        self.screen_height = 974

        self.from_date_var = ctk.StringVar()
        self.to_date_var = ctk.StringVar()
        self.category_var = ctk.StringVar()

        self.configure(fg_color="white")  # Ensure background is white
        self.setup_styles()
        self.setup_ui()

    def setup_styles(self):
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 12), rowheight=30)
        style.configure("Treeview.Heading", font=("Arial", 14, "bold"))

    def fetch_categories(self):
        conn = sqlite3.connect("Trackwise.db")
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT category FROM sales")
        categories = [row[0] for row in cursor.fetchall() if row[0] is not None]
        conn.close()
        return ["All"] + categories

    def setup_ui(self):
        try:
            # Load and reference the image properly
            background_image = Image.open(r"C:\Users\User\Documents\Ruxin file\ALL 2\View sales history.png").resize((1920, 974))
            self.ctk_background_image = ctk.CTkImage(light_image=background_image, dark_image=background_image, size=(1920, 974))
            self.bg_label = ctk.CTkLabel(self, image=self.ctk_background_image, text="")
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print(f"Error loading background image: {e}")

        self.frame = ctk.CTkFrame(self, fg_color="white", border_color="white", width=1300, height=550)
        self.frame.place(relx=0.50, rely=0.85, anchor="s")

        self.left_frame = ctk.CTkFrame(self.frame, fg_color="white", width=300, height=550)
        self.right_frame = ctk.CTkFrame(self.frame, fg_color="transparent", width=950, height=550)

        ctk.CTkLabel(self.left_frame, text="From:", font=("Arial", 24)).place(x=10, y=9, anchor="w")
        DateEntry(self.left_frame, textvariable=self.from_date_var, width=15, date_pattern="yyyy-mm-dd",
                  font=("Arial", 12), justify="center").place(x=10, y=40, width=300, height=30)

        ctk.CTkLabel(self.left_frame, text="To:", font=("Arial", 24)).place(x=10, y=90, anchor="w")
        DateEntry(self.left_frame, textvariable=self.to_date_var, width=15, date_pattern="yyyy-mm-dd",
                  font=("Arial", 12), justify="center").place(x=10, y=140, width=300, height=30)

        ctk.CTkLabel(self.left_frame, text="Category:", font=("Arial", 24)).place(x=10, y=160)
        self.category_dropdown = ctk.CTkComboBox(self.left_frame, variable=self.category_var,
                                                 values=self.fetch_categories(), width=238, height=30)
        self.category_dropdown.place(x=10, y=200)
        self.category_dropdown.set("All")

        ctk.CTkButton(self.left_frame, text="Filter", command=self.fetch_sales_data, width=238, height=35,
                      fg_color="#2155CD", font=("Arial", 20)).place(x=10, y=270)
        ctk.CTkButton(self.left_frame, text="Print Report", command=self.generate_pdf_report, width=238, height=35,
                      fg_color="#2155CD", font=("Arial", 20)).place(x=10, y=340)
        ctk.CTkButton(self.left_frame, text="Generate Sales Chart", command=self.generate_sales_chart, width=238,
                      height=35, fg_color="#2155CD", font=("Arial", 20)).place(x=10, y=410)
        ctk.CTkButton(self.left_frame, text="Sales Analysis", command=self.sales_analysis, width=238, height=35,
                      fg_color="#2155CD", font=("Arial", 20)).place(x=10, y=480)

        columns = ("Date", "Item Name", "Category", "Quantity Sold", "Total Price (RM)")
        self.tree = ttk.Treeview(self.right_frame, columns=columns, show="headings", height=20)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=140)
        self.tree.place(relx=0.5, rely=0.8, anchor="s", width=1185, height=540)

        self.total_label = ctk.CTkLabel(self.right_frame, text="Total Sales: RM0.00", font=("Arial", 24, "bold"))
        self.total_label.place(x=10, y=480)

        self.after(100, self.place_frames_at_bottom)

    def place_frames_at_bottom(self):
        self.left_frame.place(x=0, y=self.frame.winfo_height() - self.left_frame.winfo_reqheight())
        self.right_frame.place(x=300, y=self.frame.winfo_height() - self.right_frame.winfo_reqheight())

    def fetch_sales_data(self):
        conn = sqlite3.connect("Trackwise.db")
        cursor = conn.cursor()

        query = """
        SELECT strftime('%Y-%m-%d', sale_date), item_name, category, SUM(quantity_sold), SUM(total_price)
        FROM sales WHERE 1=1
        """
        params = []

        from_date = self.from_date_var.get()
        to_date = self.to_date_var.get()
        if from_date and to_date:
            query += " AND DATE(sale_date) BETWEEN ? AND ?"
            params.extend([from_date, to_date])

        selected_category = self.category_var.get()
        if selected_category and selected_category != "All":
            query += " AND category = ?"
            params.append(selected_category)

        query += " GROUP BY strftime('%Y-%m-%d', sale_date), item_name, category ORDER BY sale_date DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        self.tree.delete(*self.tree.get_children())

        total_sales = 0
        for row in rows:
            formatted_row = list(row)
            formatted_row[4] = f"{formatted_row[4]:.2f}"
            self.tree.insert("", "end", values=formatted_row)
            total_sales += float(row[4])

        self.total_label.configure(text=f"Total Sales : RM {total_sales:.2f}")

    def generate_pdf_report(self):
        store_name = "Trackwise"
        store_address = "13 Lorong 5 Taman Bunga, 15000 Bukit Jambut, Pulau Pinang"
        store_contact = "Phone: 012-345 6789"

        data = [("Date", "Item", "Category", "Quantity", "Total Price(RM)")]
        grand_total = 0.0

        for item in self.tree.get_children():
            row = self.tree.item(item)["values"]
            grand_total += float(row[4])
            data.append(row)

        if len(data) == 1:
            print("No data available to generate report.")
            return

        data.append(("", "", "", "Grand Total", f"{grand_total:.2f}"))

        pdf_file = "Sales_Report.pdf"
        pdf = SimpleDocTemplate(pdf_file, pagesize=A4)
        elements = []

        styles = getSampleStyleSheet()
        elements.append(Paragraph(store_name, styles["Heading1"]))
        elements.append(Paragraph(store_address, styles["Normal"]))
        elements.append(Paragraph(store_contact, styles["Normal"]))
        elements.append(Spacer(1, 12))

        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -2), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ]))
        elements.append(table)
        pdf.build(elements)

        os.system(f"start {pdf_file}" if os.name == "nt" else f"open {pdf_file}")

    def generate_sales_chart(self):
        conn = sqlite3.connect("Trackwise.db")
        cursor = conn.cursor()
        query = """
        SELECT item_name, SUM(quantity_sold) FROM sales WHERE 1=1
        """
        params = []

        from_date = self.from_date_var.get()
        to_date = self.to_date_var.get()
        if from_date and to_date:
            query += " AND DATE(sale_date) BETWEEN ? AND ?"
            params.extend([from_date, to_date])

        selected_category = self.category_var.get()
        if selected_category and selected_category != "All":
            query += " AND category = ?"
            params.append(selected_category)

        query += " GROUP BY item_name"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            print("No data available for chart.")
            return

        items = [r[0] for r in rows]
        quantities = [r[1] for r in rows]
        colors_list = [cm.get_cmap('tab20')(i) for i in range(len(items))]

        popup = tk.Toplevel()
        popup.title("Sales Chart")
        popup.geometry("900x600")

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(items, quantities, color=colors_list)
        ax.set_title("Sales by Item")
        ax.set_xlabel("Item Name")
        ax.set_ylabel("Quantity Sold")
        ax.tick_params(axis='x', rotation=45)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=popup)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def sales_analysis(self):
        if self.controller.current_dashboard:
            self.controller.current_dashboard.load_page("sales_analysis")
        else:
            self.controller.show_frame("SaleAnalysis")
