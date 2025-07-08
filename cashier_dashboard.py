import customtkinter as ctk
from PIL import Image
import sqlite3
import os

# Page imports
from dashboard_page import load_dashboard_content
from profile import UserProfileApp
from sales_report import load_sales_report_content
from categories_pages import CategoriesPage
from datetime import datetime
import sqlite3
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

    def get_user_info(self):
        try:
            conn = sqlite3.connect("Trackwise.db")
            cursor = conn.cursor()
            cursor.execute("SELECT username, photo_path FROM users WHERE id = ?", (self.controller.logged_in_user_id,))
            row = cursor.fetchone()
            conn.close()
            return row if row else ("Cashier", None)
        except:
            return ("Cashier", None)

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

    def load_page(self, name, user_id=None):
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
            page = UserProfileApp(
                parent=self.content_frame,
                controller=self.controller,
                user_id=self.controller.logged_in_user_id
            )
            page.pack(fill="both", expand=True)


        elif name == "edit_profile":
            from profile_edit import EditProfileApp
            page = EditProfileApp(parent=self.content_frame, controller=self.controller, user_id=user_id)
            page.pack(fill="both", expand=True)

        elif name == "sales":
            load_sales_report_content(self.content_frame)

        elif name == "home":
            self.username, photo_path = self.get_user_info()
            now = datetime.now()
            current_time = now.strftime("%d/%m/%Y %H:%M")

            try:
                if photo_path and os.path.exists(photo_path):
                    profile_img = ctk.CTkImage(Image.open(photo_path), size=(160, 160))
                else:
                    fallback = r"C:\Users\User\Documents\Ruxin file\ALL 2\profile_pic.png"
                    profile_img = ctk.CTkImage(Image.open(fallback), size=(160, 160))

                img_label = ctk.CTkLabel(self.content_frame, image=profile_img, text="")
                img_label.pack(pady=(30, 5))
            except Exception as e:
                print("Error loading profile image:", e)

            welcome = ctk.CTkLabel(
                self.content_frame,
                text=f"Welcome, {self.username} 🧾",
                font=("Arial", 28, "bold"),
                text_color="#2d3436"
            )
            welcome.pack(pady=(10, 0))

            time_label = ctk.CTkLabel(
                self.content_frame,
                text=f"Login Time: {current_time}",
                font=("Arial", 16),
                text_color="#636e72"
            )
            time_label.pack(pady=(0, 20))

            slogan = ctk.CTkLabel(
                self.content_frame,
                text="Fast, Accurate, Friendly – That’s Our Checkout Promise.",
                font=("Georgia", 20, "italic"),
                text_color="#0984e3"
            )
            slogan.pack(pady=10)

            rules_frame = ctk.CTkFrame(self.content_frame, fg_color="#f5f6fa", corner_radius=10)
            rules_frame.pack(pady=20, padx=100, fill="x")

            rules_title = ctk.CTkLabel(
                rules_frame,
                text="💼 Cashier Duties & Guidelines",
                font=("Arial", 18, "bold"),
                text_color="#2c3e50"
            )
            rules_title.pack(pady=(15, 5))

            rules_list = [
                "• Always verify item quantity and price before confirming a sale.",
                "• Provide accurate receipts to customers.",
                "• Do not share your login credentials with others.",
                "• Report discrepancies in pricing or stock immediately.",
                "• Log out of the system during breaks or shift changes.",
                "• Keep your workspace clean and organized.",
                "• Be polite and professional to every customer.",
                "• Double-check payment methods before processing.",
                "• Avoid distractions during active transactions.",
                "• Immediately report suspicious activities to a manager."
            ]

            for rule in rules_list:
                rule_label = ctk.CTkLabel(
                    rules_frame,
                    text=rule,
                    font=("Arial", 14),
                    text_color="#636e72",
                    anchor="w",
                    justify="left"
                )
                rule_label.pack(padx=20, anchor="w")

        elif name == "tag":
            CategoriesPage(self.content_frame)

        elif name == "logout":
            self.controller.logged_in_user_id = None
            self.controller.show_frame("LoginPage")
            self.controller.frames["LoginPage"].clear_fields()

        else:
            ctk.CTkLabel(
                self.content_frame,
                text=f"{name.capitalize()} Page Coming Soon...",
                font=("Arial", 20)
            ).pack(pady=50)

