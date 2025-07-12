import customtkinter as ctk
from customtkinter import CTkImage
from PIL import Image
from tkinter import ttk, messagebox, filedialog
import sqlite3
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import ParagraphStyle

class InventoryReport(ctk.CTkFrame):
    def __init__(self,parent,controller):
        super().__init__(parent)
        self.controller = controller
        self.width, self.height = 1574, 800

        # Load background image
        self.original_bg_image = Image.open(r"C:\Users\User\Documents\Ruxin file\ALL 2\View sales history.png")
        self.bg_photo = CTkImage(light_image=self.original_bg_image, size=(self.width, self.height))

        self.bg_label = ctk.CTkLabel(self, text="", image=self.bg_photo)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.frame = ctk.CTkFrame(self, fg_color="white", width=1300, height=550)
        self.frame.place(relx=0.45, rely=0.78, anchor="s")

        self.create_widgets()
        self.blink_state = False
        self.start_blinking()

    def create_widgets(self):
        self.category_var = ctk.StringVar(value="All")
        self.var_low_stock = ctk.BooleanVar(value=False)

        # Header Frame
        top_controls = ctk.CTkFrame(self.frame, fg_color="white")
        top_controls.pack(fill="x", pady=(20, 0), padx=20)

        ctk.CTkLabel(top_controls, text="Category:", font=("Inter", 22), text_color="black").grid(row=0, column=0,
                                                                                                  padx=(0, 10))

        categories = self.fetch_categories()
        categories.insert(0, "All")
        self.dropdown = ctk.CTkOptionMenu(top_controls, variable=self.category_var, values=categories, width=200,
                                          font=("Inter", 16))
        self.dropdown.grid(row=0, column=1, padx=10)

        self.checkbox = ctk.CTkCheckBox(top_controls, text="Low Stock / Out of Stock", font=("Inter", 18),
                                        text_color="black", variable=self.var_low_stock)
        self.checkbox.grid(row=0, column=2, padx=20)

        ctk.CTkButton(top_controls, text="Search", command=self.on_search, width=140, font=("Inter", 16)).grid(row=0,
                                                                                                               column=3,
                                                                                                               padx=10)
        ctk.CTkButton(top_controls, text="Generate Report", command=self.generate_pdf, width=160,
                      font=("Inter", 16)).grid(row=0, column=4, padx=10)
        ctk.CTkButton(top_controls, text="Generate Chart", command=self.show_bar_chart, width=160,
                      font=("Inter", 16)).grid(row=0, column=5, padx=10)

        # Treeview Styling
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview.Heading", background="#0C5481", foreground="white", font=("Inter", 14, "bold"))
        style.configure("Treeview", background="#eaf9ff", foreground="#057687", rowheight=35, fieldbackground="#eaf9ff",
                        font=("Inter", 13))
        style.map("Treeview", background=[('selected', '#b0d9e6')])

        # Table Frame
        table_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, pady=20, padx=20)

        columns = ("ID", "Item Name", "Category", "Opening Stock", "Closing Stock", "Quantity Sold", "Status")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=180)
        self.tree.column("ID", width=80)
        self.tree.column("Item Name", width=250)

        self.tree.grid(row=0, column=0, sticky="nsew")

        # Scrollbar
        scrollbar = ctk.CTkScrollbar(table_frame, orientation="vertical", command=self.tree.yview,
                                     fg_color="#0C5481", button_color="#cce7f9", button_hover_color="#0882c4")
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Grid expand
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # Treeview Tags
        self.tree.tag_configure('low_stock', foreground='orange')
        self.tree.tag_configure('out_stock', foreground='red')

    def start_blinking(self):
        bg_color = '#FF6666' if self.blink_state else 'white'
        self.tree.tag_configure('low_stock', background=bg_color, foreground='black')
        self.tree.tag_configure('out_stock', background=bg_color, foreground='black')

        self.blink_state = not self.blink_state
        self.after(500, self.start_blinking)

    def fetch_categories(self):
        conn = sqlite3.connect("Trackwise.db")
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT category FROM inventory ORDER BY category")
        categories = [row[0] for row in cursor.fetchall()]
        conn.close()
        return categories

    def refresh_dropdown(self):
        categories = self.fetch_categories()
        categories.insert(0, "All")
        self.dropdown.configure(values=categories)

    def fetch_inventory_data(self, category_filter=None, low_stock=False, low_stock_threshold=5):
        conn = sqlite3.connect("Trackwise.db")
        cursor = conn.cursor()

        query = """
            SELECT
                i.product_id,
                i.item_name,
                i.category,
                i.quantity AS closing_stock,
                IFNULL(SUM(s.quantity_sold), 0) AS quantity_sold
            FROM inventory i
            LEFT JOIN Sales s ON i.product_id = s.product_id
        """

        conditions = []
        params = []

        if category_filter and category_filter != "All":
            conditions.append("i.category = ?")
            params.append(category_filter)
        if low_stock:
            conditions.append("i.quantity < ?")
            params.append(low_stock_threshold)
        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += """
            GROUP BY i.product_id, i.item_name, i.category, i.quantity 
            ORDER BY i.product_id
        """

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return rows

    def populate_treeview(self, rows):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for row in rows:
            product_id_, name, category, closing_stock, quantity_sold = row
            opening_stock = closing_stock + quantity_sold
            status = "Normal"
            if closing_stock == 0:
                status = "Out of Stock"
            elif closing_stock < 5:
                status = "Low"

            tags = ()
            if status == "Low":
                tags = ('low_stock',)
            elif status == "Out of Stock":
                tags = ('out_stock',)

            self.tree.insert("", "end", values=(product_id_, name, category, opening_stock, closing_stock, quantity_sold, status), tags=tags)

    def on_search(self):
        self.refresh_dropdown()
        category = self.category_var.get()
        low_stock_checked = self.var_low_stock.get()
        rows = self.fetch_inventory_data(category_filter=category, low_stock=low_stock_checked)
        self.populate_treeview(rows)

    def generate_pdf(self):
        rows = [self.tree.item(item)["values"] for item in self.tree.get_children()]
        if not rows:
            messagebox.showwarning("No data", "No data to generate PDF.")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile="inventory_report.pdf",
            title="Save Inventory Report"
        )

        if not filename:
            return  # User cancelled the save dialog
        doc = SimpleDocTemplate(filename, pagesize=landscape(letter))
        elements = []

        # Store info
        store_name = "Trackwise"
        store_address = "Address: 13 Lorong 5 Taman Bunga, 15000 Bukit Jambut, Pulau Pinang"
        store_contact = "Phone: 012-345 6789"

        # Custom styles
        store_name_style = ParagraphStyle(name='StoreName', fontSize=20, leading=26, alignment=0,
                                          fontName='Helvetica-Bold')
        left_style = ParagraphStyle(name='LeftStyle', fontSize=14, leading=18, alignment=0)
        report_title_style = ParagraphStyle(name='ReportTitle', fontSize=18, leading=24, alignment=1,
                                            fontName='Helvetica-Bold')

        # Store Info
        elements.append(Paragraph(store_name, store_name_style))
        elements.append(Spacer(1, 20))
        elements.append(Paragraph(store_address, left_style))
        elements.append(Spacer(1, 8))
        elements.append(Paragraph(store_contact, left_style))
        elements.append(Spacer(1, 20))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.black))
        elements.append(Spacer(1, 15))

        # Centered Bold Title
        elements.append(Paragraph("Inventory Report", report_title_style))
        elements.append(Spacer(1, 20))

        # Table data
        headers = ["Product ID", "Name", "Category", "Opening Stock", "Closing Stock", "Quantity Sold", "Status"]
        table_data = [headers]

        for row in rows:
            table_data.append([str(val) for val in row])

        # Create table
        t = Table(table_data, colWidths=[120, 120, 120, 100, 100, 100, 80])
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ])

        for i, row in enumerate(rows, start=1):  # start=1 because 0 is header
            status = row[-1]
            if status == "Low":
                style.add('TEXTCOLOR', (0, i), (-1, i), colors.red)
            elif status == "Out of Stock":
                style.add('TEXTCOLOR', (0, i), (-1, i), colors.red)

        t.setStyle(style)
        elements.append(t)

        doc.build(elements)
        messagebox.showinfo("PDF Generated", f"Inventory report saved as {filename}")

    def show_bar_chart(self):
        rows = [self.tree.item(item)["values"] for item in self.tree.get_children()]
        if not rows:
            messagebox.showwarning("No data", "No data to plot.")
            return

        names = [row[1] for row in rows]
        closing_stock = [row[4] for row in rows]

        # Create popup window
        popup = tk.Toplevel(self)
        popup.title("Inventory Bar Chart")
        popup.geometry("900x600")

        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.barh(names, closing_stock, color='teal')
        ax.set_xlabel("Closing Stock")
        ax.set_ylabel("Item Name")
        ax.set_title("Closing Stock per Item")
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=popup)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
