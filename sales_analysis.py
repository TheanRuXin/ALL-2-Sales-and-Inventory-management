import os, sqlite3, tempfile
from datetime import datetime, date, timedelta
import matplotlib,mplcursors
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,NavigationToolbar2Tk
from matplotlib import colormaps
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer, Image as RLImage,PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib import colors
import customtkinter as ctk
from tkcalendar import DateEntry
from tkinter.filedialog import asksaveasfilename
import tkinter as tk
import matplotlib.dates as mdates
from tkinter import messagebox
from PIL import Image
from customtkinter import CTkImage
matplotlib.rcParams['font.family'] = 'Arial'
matplotlib.rcParams['font.size'] = 13
matplotlib.use('Agg')

class SaleAnalysis(ctk.CTkFrame):
    def __init__(self,parent,controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(fg_color="white")
        self.create_sales_table()
        self.setup_ui()

    def setup_ui(self):
        title_label = ctk.CTkLabel(self, text="Sales Analysis", font=("Arial", 32, "bold"), text_color="black")
        title_label.place(x=50, y=20)
        filter_frame = ctk.CTkFrame(self, fg_color="white", bg_color="white")
        filter_frame.pack(pady=(80,50))
        logo_image = CTkImage(light_image=Image.open(r"C:\Users\User\Documents\Ruxin file\ALL 2\logo.png"), size=(90, 80))
        logo_label = ctk.CTkLabel(self, image=logo_image, text="")
        logo_label.place(relx=1.0, x=-60, y=20, anchor="ne")

        today = datetime.today()
        one_week_ago = today - timedelta(days=7)

        self.from_var = ctk.StringVar()
        self.to_var = ctk.StringVar()
        self.cat_var = ctk.StringVar(value="All")

        ctk.CTkLabel(filter_frame, text="From:", font=("Arial", 20)).pack(side="left", padx=5)
        from_entry = DateEntry(filter_frame, textvariable=self.from_var, date_pattern="yyyy-mm-dd", font=("Arial", 18),
                               width=12)
        from_entry.set_date(one_week_ago)
        from_entry.pack(side="left", padx=5)
        ctk.CTkLabel(filter_frame, text="To:", font=("Arial", 20)).pack(side="left", padx=5)
        to_entry = DateEntry(filter_frame, textvariable=self.to_var, date_pattern="yyyy-mm-dd", font=("Arial", 18),
                             width=12)
        to_entry.set_date(today)
        to_entry.pack(side="left", padx=5)
        ctk.CTkLabel(filter_frame, text="Category:", font=("Arial", 20)).pack(side="left", padx=5)
        ctk.CTkComboBox(filter_frame, variable=self.cat_var, values=self.fetch_categories(), font=("Arial", 18)).pack(
            side="left", padx=5)

        ctk.CTkButton(filter_frame, text="Apply Filter", command=self.refresh_charts,font=("Arial",16),height=35, width=160).pack(side="left", padx=10)
        ctk.CTkButton(filter_frame, text="Export All to PDF", command=self.export_all_charts_pdf,font=("Arial",16),height=35, width=160).pack(side="left",
                                                                                                       padx=5)
        self.summary_frame = ctk.CTkFrame(self, fg_color="#fff7e6", bg_color="#fff7e6")
        self.summary_frame.pack(pady=(0, 25))  # Right below filter_frame
        self.chart_frame = ctk.CTkFrame(self, fg_color="white", bg_color="white")
        self.chart_frame.pack(fill="both", expand=True, padx=20, pady=(30,10))
        self.refresh_charts()

    def refresh_charts(self):
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        from_date = self.from_var.get()
        to_date = self.to_var.get()
        category = self.cat_var.get()
        try:
            from_dt = datetime.strptime(from_date, "%Y-%m-%d")
            to_dt = datetime.strptime(to_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Invalid Format", "Date format must be YYYY-MM-DD.")
            return
        if not from_date or not to_date:
            messagebox.showwarning("Missing Dates", "Please select both From and To dates.")
            return
        if from_date > to_date:
            messagebox.showerror("Invalid Date Range", "The 'From' date cannot be later than the 'To' date.")
            return
        if from_dt > datetime.today() or to_dt > datetime.today():
            messagebox.showwarning("Future Dates", "Future dates are not allowed.")
            return

        chart1 = self.create_chart_frame(
            "Top Selling Products",
            lambda f=None, ax=None, limit=4, **kwargs: self.plot_top_selling(f, from_date, to_date, category, ax,
                                                             limit=limit, **kwargs))
        chart2 = self.create_chart_frame(
            "Sales Trend Over Time",
            lambda f=None, ax=None, limit=4, **kwargs: self.plot_sales_trend(f, from_date, to_date, category, ax,
                                                                             limit=limit, **kwargs))
        chart3 = self.create_chart_frame(
            "Sales Breakdown by Category",
            lambda f=None, ax=None, **kwargs: self.plot_category_breakdown(f, from_date, to_date, ax))
        chart1.pack(side="left", expand=True, fill="both", padx=10)
        chart2.pack(side="left", expand=True, fill="both", padx=10)
        chart3.pack(side="left", expand=True, fill="both", padx=10)
        self.create_summary_table()

    def create_chart_frame(self, title, plot_func):
        frame = ctk.CTkFrame(self.chart_frame, fg_color="white", bg_color="white")
        ctk.CTkLabel(frame, text=title, font=("Arial", 20, "bold")).pack(pady=5,anchor="center")
        canvas_frame = ctk.CTkFrame(frame, fg_color="white", bg_color="white")
        canvas_frame.pack(fill="both", expand=True)
        plot_func(canvas_frame, show_tooltip=False)

        button_frame = ctk.CTkFrame(frame, fg_color="white", bg_color="white")
        button_frame.pack(pady=(0, 50), padx=(30, 0))

        # Fullscreen version uses all data (no limit)
        ctk.CTkButton(button_frame, text="View",font=("Arial",16),height=35, width=80, command=lambda: self.show_fullscreen_chart(
            title, lambda f=None, ax=None: plot_func(f, ax=ax, limit=None, show_tooltip=True)
        )).pack(side="left", padx=5)
        return frame

    def show_fullscreen_chart(self, title, plot_func):
        win = ctk.CTkToplevel(self)
        win.title(title)
        win.geometry("1000x700")

        # Create a Matplotlib figure
        fig, ax = plt.subplots(figsize=(9, 5))  # or a size you prefer

        # Let your plotting function draw on the given Axes
        plot_func(ax=ax)

        # Embed the figure in the Tkinter window
        canvas = FigureCanvasTkAgg(fig, master=win)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Add Matplotlib's navigation toolbar (optional)
        toolbar_frame = tk.Frame(master=win)
        toolbar_frame.pack(side=tk.BOTTOM, fill=tk.X)
        NavigationToolbar2Tk(canvas, toolbar_frame)

    def export_all_charts_pdf(self):
        from_date = self.from_var.get()
        to_date = self.to_var.get()
        category = self.cat_var.get()
        try:
            from_dt = datetime.strptime(from_date, "%Y-%m-%d")
            to_dt = datetime.strptime(to_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Invalid Format", "Date format must be YYYY-MM-DD.")
            return
        if not from_date or not to_date:
            messagebox.showwarning("Missing Dates", "Please select both From and To dates.")
            return
        if from_date > to_date:
            messagebox.showerror("Invalid Date Range", "The 'From' date cannot be later than the 'To' date.")
            return
        if from_dt > datetime.today() or to_dt > datetime.today():
            messagebox.showwarning("Future Dates", "Future dates are not allowed.")
            return

        chart_data = [
            ("Top Selling Products",lambda ax=None: self.plot_top_selling(None, from_date, to_date, category, ax)),
            ("Sales Trend Over Time",lambda ax=None: self.plot_sales_trend(None, from_date, to_date, category=category, ax=ax, limit=None)),
            ("Sales Breakdown by Category",lambda ax=None: self.plot_category_breakdown(None, from_date, to_date, ax))
        ]
        styles = getSampleStyleSheet()
        styles["Title"].fontSize = 22
        styles["Normal"].fontSize = 14
        styles["Normal"].leading = 16

        elements = []
        image_paths = []

        for idx, (title, plot_func) in enumerate(chart_data):
            fig, ax = plt.subplots(figsize=(11, 5.5))
            plot_func(ax=ax)

            tmp_img = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            fig.savefig(tmp_img.name, bbox_inches='tight')
            plt.close(fig)
            tmp_img.close()
            image_paths.append(tmp_img.name)

            report_title = f"Sales Report: {title}"
            details = f"Date Range: {from_date} to {to_date} | Category: {category}"

            elements.append(Paragraph(report_title, styles["Title"]))
            elements.append(Spacer(1, 25))
            elements.append(Paragraph(details, styles["Normal"]))
            elements.append(Spacer(1, 50))
            elements.append(RLImage(tmp_img.name, width=9.5 * inch, height=4.5 * inch))

            if idx < len(chart_data) - 1:
                elements.append(PageBreak())

        # summary
        elements.append(PageBreak())
        elements.append(Paragraph("Summary", styles["Title"]))
        elements.append(Spacer(1, 20))

        summary_table_data = [[label, value] for label, value in self.summary_data]
        summary_table = Table(summary_table_data, colWidths=[3.5 * inch, 5 * inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 16),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(summary_table)

        pdf_path = asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile="Sales_Report.pdf",
            title="Save Sales Report PDF"
        )
        if not pdf_path:
            messagebox.showinfo("Export Cancelled", "PDF export was cancelled.")
            return
        doc = SimpleDocTemplate(pdf_path, pagesize=landscape(letter), topMargin=36, bottomMargin=36)
        doc.build(elements)
        try:
            if os.name == "nt":
                os.system(f'start "" "{pdf_path}"')
            else:
                os.system(f'open "{pdf_path}"')
        except Exception as e:
            print(f"Error opening file: {e}")
        for img_path in image_paths:
            try:
                os.remove(img_path)
            except Exception as e:
                print(f"Warning: Could not delete temp file: {e}")
        messagebox.showinfo("Export Success", "Sales report exported successfully.")

    def plot_top_selling(self, container, from_date, to_date, category, ax=None, limit=None, show_tooltip=True):
        plt.close('all')
        items, quantities = self.query_sales_data(from_date, to_date, category)
        if limit:
            items = items[:limit]
            quantities = quantities[:limit]

        if ax is None:
            fig, ax = plt.subplots(figsize=(6, 4))
            canvas = FigureCanvasTkAgg(fig, master=container)
            canvas.draw()
            canvas.get_tk_widget().pack()

        if not items:
            ax.set_title("No sales data in selected range", fontsize=14, fontname='Arial')
            ax.set_xlabel("Item Name", fontsize=14, fontname='Arial')
            ax.set_ylabel("Quantity Sold", fontsize=14, fontname='Arial')
            ax.set_xticks([])
            ax.set_yticks([])
            plt.tight_layout()
        else:
            colors = [colormaps['tab20'](i / len(items)) for i in range(len(items))]
            bars = ax.bar(items, quantities, color=colors)
            ax.set_xlabel("Item Name", fontsize=14, fontname='Arial')
            ax.set_ylabel("Quantity Sold", fontsize=14, fontname='Arial')
            ax.tick_params(axis='x', labelsize=12)
            ax.tick_params(axis='y', labelsize=12)
            ax.set_xticks(range(len(items)))
            ax.set_xticklabels(items, rotation=45, ha="right", fontsize=12, fontname='Arial')
            plt.tight_layout()

        if items:
            colors = plt.cm.tab10.colors
            bar_colors = [colors[i % len(colors)] for i in range(len(items))]
            bars = ax.bar(items, quantities, color=bar_colors)

            if show_tooltip:
                cursor = mplcursors.cursor(bars, hover=True)
                cursor.connect("add", lambda sel:
                sel.annotation.set_text(f"{items[sel.index]}\nQuantity: {quantities[sel.index]}"))
        else:
            ax.set_title("No data available for selected range", fontsize=14, fontname='Arial')

    def plot_sales_trend(self, container, from_date, to_date, category=None, ax=None, limit=4, show_tooltip=True):
        plt.close('all')
        data = self.query_sales_over_time(from_date, to_date, category)

        fig = None
        if ax is None:
            fig, ax = plt.subplots(figsize=(6, 4))
            canvas = FigureCanvasTkAgg(fig, master=container)
            canvas.draw()
            canvas.get_tk_widget().pack()

        if not data:
            ax.set_title("No sales data in selected range", fontsize=14, fontname='Arial')
            ax.set_xlabel("Date", fontsize=14, fontname='Arial')
            ax.set_ylabel("Quantity Sold", fontsize=14, fontname='Arial')
            ax.grid(True)
            plt.tight_layout()
            return

        if limit is not None:
            product_totals = {product: sum(sales.values()) for product, sales in data.items()}
            top_products = sorted(product_totals.items(), key=lambda x: x[1], reverse=True)[:limit]
            data = {product: data[product] for product, _ in top_products}

        from_dt = datetime.strptime(from_date, "%Y-%m-%d")
        to_dt = datetime.strptime(to_date, "%Y-%m-%d")

        all_dt_objects = [from_dt + timedelta(days=i) for i in range((to_dt - from_dt).days + 1)]

        for product, sales_data in data.items():
            sales_data_dt = {datetime.strptime(k, "%Y-%m-%d"): v for k, v in sales_data.items()}
            quantities = [sales_data_dt.get(dt, 0) for dt in all_dt_objects]
            line, = ax.plot(all_dt_objects, quantities, marker='o', label=product)
            if show_tooltip:
                cursor = mplcursors.cursor([line], hover=True)
                cursor.connect("add", lambda sel, prod=product, dts=all_dt_objects, qts=quantities:
                sel.annotation.set_text(f"{prod}\n{dts[int(sel.index)].strftime('%Y-%m-%d')}: {qts[int(sel.index)]}"))

        if fig is not None and fig.get_size_inches()[0] >= 7:
            # Fullscreen: show full dates
            ax.xaxis.set_major_locator(mdates.AutoDateLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        else:
            # Small view: avoid crowding
            locator = mdates.AutoDateLocator()
            ax.xaxis.set_major_locator(locator)
            ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))

        ax.set_xlim([from_dt, to_dt])

        if fig is not None:
            fig.autofmt_xdate(rotation=45)
            fig.tight_layout(pad=3.0)

        ax.set_xlabel("Date", fontsize=14, fontname='Arial')
        ax.set_ylabel("Quantity Sold", fontsize=14, fontname='Arial')
        ax.tick_params(axis='x', labelsize=12)
        ax.tick_params(axis='y', labelsize=12)
        ax.legend(fontsize=12, prop={'family': 'Arial'})
        ax.grid(True)
        plt.tight_layout()

    def plot_category_breakdown(self, container, from_date, to_date, ax=None):
        plt.close('all')
        conn = sqlite3.connect("Trackwise.db")
        cursor = conn.cursor()
        cursor.execute("""
               SELECT category, SUM(quantity_sold)
               FROM sales
               WHERE substr(sale_date,1,10) BETWEEN ? AND ?
               GROUP BY category
           """, (from_date, to_date))
        rows = cursor.fetchall()
        conn.close()

        if ax is None:
            fig, ax = plt.subplots(figsize=(6, 4))
            canvas = FigureCanvasTkAgg(fig, master=container)
            canvas.draw()
            canvas.get_tk_widget().pack()

        if not rows:
            ax.text(0.5, 0.5, "No sales data in selected range",
                    fontsize=14, fontname='Arial', ha='center', va='center', transform=ax.transAxes)
            ax.axis('off')
            return

        labels = [row[0] for row in rows]
        sizes = [row[1] for row in rows]

        ax.pie(
            sizes,
            labels=labels,
            autopct='%1.1f%%',
            startangle=140,
            colors=colormaps['tab20'].colors[:len(labels)],
            textprops={'fontsize': 12, 'fontname': 'Arial'}
        )
        ax.axis('equal')
        plt.tight_layout()

    def create_sales_table(self):
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
        conn.close()

    def fetch_categories(self):
        conn = sqlite3.connect("Trackwise.db")
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT category FROM sales")
        categories = [row[0] for row in cursor.fetchall()]
        conn.close()
        return ["All"] + categories

    def query_sales_data(self, from_date, to_date, category=None):
        conn = sqlite3.connect("Trackwise.db")
        cursor = conn.cursor()
        query = "SELECT item_name, SUM(quantity_sold) FROM sales WHERE 1=1"
        params = []

        if from_date and to_date:
            query += " AND substr(sale_date,1,10) BETWEEN ? AND ?"
            params.extend([from_date, to_date])

        if category and category != "All":
            query += " AND category = ?"
            params.append(category)

        query += " GROUP BY item_name ORDER BY SUM(quantity_sold) DESC"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        items = [r[0] for r in rows]
        quantities = [r[1] for r in rows]
        return items, quantities

    def query_sales_over_time(self, from_date, to_date, category=None):
        conn = sqlite3.connect("Trackwise.db")
        cursor = conn.cursor()
        query = """
                SELECT
                    item_name,
                    substr(sale_date,1,10) AS sale_day,   
                    SUM(quantity_sold)
                FROM sales
                WHERE substr(sale_date,1,10) BETWEEN ? AND ?
            """
        params = [from_date, to_date]

        if category and category != "All":
            query += " AND category = ?"
            params.append(category)

        query += """
                GROUP BY item_name, substr(sale_date,1,10)
                ORDER BY item_name, substr(sale_date,1,10)
            """
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        data = {}
        for item_name, sale_day, qty in rows:
            data.setdefault(item_name, {})[sale_day] = qty
        return data

    def create_summary_table(self):
        from_date = self.from_var.get()
        to_date = self.to_var.get()
        category = self.cat_var.get()
        conn = sqlite3.connect("Trackwise.db")
        cursor = conn.cursor()
        base_query =  """
            SELECT
                SUM(total_price)   AS total_revenue,
                SUM(quantity_sold) AS total_quantity
            FROM sales
            WHERE substr(sale_date,1,10) BETWEEN ? AND ?
        """
        params = [from_date, to_date]
        if category and category != "All":
            base_query += " AND category = ?"
            params.append(category)
        cursor.execute(base_query, params)
        result = cursor.fetchone()
        total_revenue = result[0] or 0
        total_quantity = result[1] or 0
        average_price = total_revenue / total_quantity if total_quantity else 0 #Average price per unit sold
        # Get top product
        top_product_query = """
            SELECT item_name, SUM(quantity_sold) AS total_qty
        FROM sales
        WHERE substr(sale_date,1,10) BETWEEN ? AND ?
        """
        top_params = [from_date, to_date]
        if category and category != "All":
            top_product_query += " AND category = ?"
            top_params.append(category)
        top_product_query += " GROUP BY item_name ORDER BY total_qty  DESC LIMIT 1"

        cursor.execute(top_product_query, top_params)
        top_row = cursor.fetchone()
        top_product = top_row[0] if top_row else "N/A"
        conn.close()
        for widget in self.summary_frame.winfo_children():
            widget.destroy()
        # Data to display
        self.summary_data = [
            ("Selected Period", f"{from_date} → {to_date}"),
            ("Selected Category", category if category else "All"),
            ("Total Revenue", f"RM{total_revenue:,.2f}"),
            ("Total Quantity Sold", f"{total_quantity:,}"),
            ("Average Price", f"RM{average_price:,.2f}"),
            ("Top Product", top_product)
        ]
        for label, value in self.summary_data:
            item_frame = ctk.CTkFrame(self.summary_frame, fg_color="#fff7e6", bg_color="#fff7e6")
            item_frame.pack(side="left", padx=30)

            ctk.CTkLabel(item_frame, text=label, font=("Arial", 16, "bold"), text_color="black").pack()
            ctk.CTkLabel(item_frame, text=value, font=("Arial", 16), text_color="gray20").pack()
