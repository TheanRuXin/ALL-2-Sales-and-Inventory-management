import customtkinter as ctk
from customtkinter import CTkImage
from PIL import Image
from tkinter import ttk, messagebox, filedialog
import sqlite3
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import ParagraphStyle
import subprocess

class InventoryDetails(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("View Inventory Details")
        self.geometry("1920x974")
        self.configure(fg_color="#FFFFFF")
        self.resizable(True, True)

        # Load background image
        self.original_bg_image = Image.open("inventory_report_bg.png")
        self.bg_photo = CTkImage(light_image=self.original_bg_image, size=(1600, 800))

        self.bg_label = ctk.CTkLabel(self, text="", image=self.bg_photo)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.frame = ctk.CTkFrame(self, fg_color="white", width=1300, height=550)
        self.frame.place(relx=0.45, rely=0.78, anchor="s")

        self.create_widgets()

    def create_widgets(self):
        # Control variables
        self.category_var = ctk.StringVar(value="All")
        self.var_low_stock = ctk.BooleanVar(value=False)

        # Label and Dropdown
        self.label = ctk.CTkLabel(self.frame, text="Category:", font=("Inter", 28), text_color="black")
        self.label.place(x=50, y=30)

        categories = self.fetch_categories()
        categories.insert(0, "All")  # Add "All" at the top of the list

        self.dropdown = ctk.CTkOptionMenu(self.frame, variable=self.category_var,
                                          values=categories,
                                          width=200, height=30, font=("Inter", 18))
        self.dropdown.place(x=180, y=35)

        self.checkbox = ctk.CTkCheckBox(self.frame, text="Low Stock / Out of Stock",
                                        font=("Inter", 20), text_color="black",
                                        variable=self.var_low_stock)
        self.checkbox.place(x=50, y=90)

        # Buttons
        self.button_search = ctk.CTkButton(self.frame, text="Search", command=self.on_search,
                                           width=140, height=35, font=("Inter", 16))
        self.button_search.place(x=450, y=35)

        self.button_report = ctk.CTkButton(self.frame, text="Generate Report", command=self.generate_pdf,
                                           width=150, height=35, font=("Inter", 16))
        self.button_report.place(x=1100, y=35)

        self.button_chart = ctk.CTkButton(self.frame, text="Generate Chart", command=self.show_bar_chart,
                                          width=150, height=35, font=("Inter", 16))
        self.button_chart.place(x=1100, y=100)

        self.button_back = ctk.CTkButton(self, text="Back", command=self.go_back,
                                         width=140, height=35, font=("Inter", 16))
        self.button_back.place(x=50, y=680)

        # Treeview
        style = ttk.Style()
        style.configure("Treeview",rowheight=35, font=("Inter", 14))  # Font for rows
        style.configure("Treeview.Heading", font=("Inter", 15, "bold"))  # Font for column headers

        columns = ("ID", "Item Name", "Category", "Opening Stock", "Closing Stock", "Quantity Sold", "Status")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=11)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor="center")
            self.tree.column("ID", width=80)
            self.tree.column("Item Name", width=250)
            self.tree.column("Category", width=250)
            self.tree.column("Opening Stock", width=250)
            self.tree.column("Closing Stock", width=250)
            self.tree.column("Quantity Sold", width=250)
            self.tree.column("Status", width=250)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.place(x=120, y=340)
        scrollbar.place(x=1750, y=390, height=330)

        self.tree.tag_configure('low_stock', foreground='orange')
        self.tree.tag_configure('out_stock', foreground='red')

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
                i.id,
                i.item_name,
                i.category,
                i.quantity AS closing_stock,
                IFNULL(SUM(s.quantity_sold), 0) AS quantity_sold
            FROM inventory i
            LEFT JOIN sales s ON i.id = s.item_id
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
            GROUP BY i.id, i.item_name, i.category, i.quantity 
            ORDER BY i.id
        """

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return rows

    def populate_treeview(self, rows):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for row in rows:
            id_, name, category, closing_stock, quantity_sold = row
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

            self.tree.insert("", "end", values=(id_, name, category, opening_stock, closing_stock, quantity_sold, status), tags=tags)

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
        headers = ["ID", "Name", "Category", "Opening Stock", "Closing Stock", "Quantity Sold", "Status"]
        table_data = [headers]

        for row in rows:
            table_data.append([str(val) for val in row])

        # Create table
        t = Table(table_data, colWidths=[60, 120, 120, 100, 100, 100, 80])
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
                style.add('TEXTCOLOR', (0, i), (-1, i), colors.orange)
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

        plt.figure(figsize=(10, 6))
        plt.barh(names, closing_stock, color='teal')
        plt.xlabel("Closing Stock")
        plt.ylabel("Item Name")
        plt.title("Closing Stock")
        plt.tight_layout()
        plt.show()

    def go_back(self):
        try:
            subprocess.Popen(["python", "manager_dash.py"])
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Manager Dashboard: {e}")


if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    app = InventoryDetails()
    app.mainloop()
