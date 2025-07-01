import customtkinter as ctk
from PIL import Image
import sqlite3
import os

# Page imports
from dashboard_page import load_dashboard_content
from profile import UserPage
from sales_report import load_sales_report_content
from home_page import load_home_content
from categories_pages import CategoriesPage

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class CashierDashboard(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.user_id = controller.logged_in_user_id
        self.username = self.get_username()

        self.dashboard_cart_items = []
        self.dashboard_total_price = 0.0

        # Removed "settings" from the nav items
        self.nav_items = ["dashboard", "user", "home", "sales", "tag", "logout"]
        self.icons = {}
        self.buttons = {}
        self.active_button = None

        self.create_sidebar()
        self.create_content_area()
        self.load_page("home")

    def get_username(self):
        conn = sqlite3.connect("Trackwise.db")
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users WHERE id = ?", (self.user_id,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else "Cashier"

    def create_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=150, fg_color="#cce7f9", corner_radius=0)
        sidebar.pack(side="left", fill="y")

        btn_container = ctk.CTkFrame(sidebar, fg_color="transparent")
        btn_container.pack(expand=True)

        for item in self.nav_items:
            img_path = os.path.join("images", f"{item}.png")
            if os.path.exists(img_path):
                self.icons[item] = ctk.CTkImage(Image.open(img_path), size=(40, 40))
            else:
                self.icons[item] = None

            btn = ctk.CTkButton(
                btn_container,
                image=self.icons[item],
                text="",
                width=50,
                height=50,
                fg_color="transparent",
                hover=True,
                command=lambda name=item: self.load_page(name)
            )
            btn.pack(pady=10)
            self.buttons[item] = btn

    def create_content_area(self):
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(side="right", expand=True, fill="both")

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def set_active_button(self, name):
        for key, btn in self.buttons.items():
            if key == name:
                btn.configure(corner_radius=0, fg_color="#ffffff", width=61, height=60)
            else:
                btn.configure(corner_radius=0, fg_color="transparent", width=50, height=50)
        self.active_button = name

    def update_dashboard_cart(self, cart_items, total_price):
        self.dashboard_cart_items = cart_items
        self.dashboard_total_price = total_price

    def load_page(self, name):
        if hasattr(self, "dashboard_instance"):
            self.dashboard_cart_items = self.dashboard_instance.cart_items
            self.dashboard_total_price = self.dashboard_instance.total_price

        self.clear_content()
        self.set_active_button(name)

        if name == "dashboard":
            self.dashboard_instance = load_dashboard_content(
                self.content_frame,
                self.username,
                cart_items=self.dashboard_cart_items,
                total_price=self.dashboard_total_price,
                on_cart_update=self.update_dashboard_cart
            )



        elif name == "user":

            page = UserPage(parent=self.content_frame, controller=self.controller,
                            user_id=self.controller.logged_in_user_id)

            page.pack(fill="both", expand=True)



        elif name == "sales":
            load_sales_report_content(self.content_frame)

        elif name == "home":
            load_home_content(self.content_frame)

        elif name == "tag":
            CategoriesPage(self.content_frame)

        elif name == "logout":
            self.controller.logged_in_user_id = None
            self.controller.show_frame("MainPage")

        else:
            ctk.CTkLabel(
                self.content_frame,
                text=f"{name.capitalize()} Page Coming Soon...",
                font=("Arial", 20)
            ).pack(pady=50)
