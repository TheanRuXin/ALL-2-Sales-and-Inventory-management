import os
import customtkinter as ctk
from PIL import Image
from ViewSalesHistory import SalesHistoryPage
from inventory_report import InventoryReport
from Admin_and_Cashier_registration import Register
import sqlite3
from datetime import datetime

class ManagerDashboard(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.nav_items = {
            "home": "Home",
            "user": "User Profile",
            "saleS": "View Reports",
            "manage product": "Manage Inventory",
            "register": "Registration",
            "logout": "Logout"
        }

        self.icons = {}
        self.buttons = {}
        self.active_button = None

        self.create_sidebar()
        self.create_content_area()
        self.load_page("home")

    def create_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=150, fg_color="#cce7f9", corner_radius=0)
        sidebar.pack(side="left", fill="y")

        btn_container = ctk.CTkFrame(sidebar, fg_color="transparent")
        btn_container.pack(expand=True)

        for item in self.nav_items:
            img_path = os.path.join("images", f"{item}.png")
            self.icons[item] = ctk.CTkImage(Image.open(img_path), size=(40, 40)) if os.path.exists(img_path) else None

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
            return row if row else ("Manager", None)
        except:
            return ("Manager", None)

    def create_content_area(self):
        self.content_frame = ctk.CTkFrame(self, fg_color="white")
        self.content_frame.pack(side="right", expand=True, fill="both")

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def set_active_button(self, name):
        for key, btn in self.buttons.items():
            btn.configure(fg_color="#ffffff" if key == name else "transparent")
        self.active_button = name

    def load_page(self, name, user_id=None):
        self.clear_content()
        self.set_active_button(name)

        if name == "home":
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
                text=f"Welcome, {self.username} 🎯",
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
                text="Leading with Insight, Managing with Precision.",
                font=("Georgia", 20, "italic"),
                text_color="#0984e3"
            )
            slogan.pack(pady=10)

            rules_frame = ctk.CTkFrame(self.content_frame, fg_color="#f5f6fa", corner_radius=10)
            rules_frame.pack(pady=20, padx=100, fill="x")

            rules_title = ctk.CTkLabel(
                rules_frame,
                text="📋 Manager Responsibilities",
                font=("Arial", 18, "bold"),
                text_color="#2c3e50"
            )
            rules_title.pack(pady=(15, 5))

            rules_list = [
                "• Oversee inventory accuracy.",
                "• Assist Admin and Cashier when needed.",
                "• Ensure timely product registration.",
                "• Review daily and weekly sales reports.",
                "• Maintain security and role boundaries.",
                "• Train new users on system features.",
                "• Communicate system issues promptly.",
                "• Encourage data consistency and backups."
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

        elif name == "user":
            from profile import UserProfileApp
            page = UserProfileApp(parent=self.content_frame, controller=self.controller,
                                  user_id=self.controller.logged_in_user_id)
            page.pack(fill="both", expand=True)

        elif name == "edit_profile":
            from profile_edit import EditProfileApp
            page = EditProfileApp(parent=self.content_frame, controller=self.controller, user_id=user_id)
            page.pack(fill="both", expand=True)

        # existing pages
        elif name == "saleS":
            page = SalesHistoryPage(parent=self.content_frame, controller=self.controller)
            page.place(x=0, y=0, relwidth=1, relheight=1)

        elif name == "sales_analysis":
            from sales_analysis import SaleAnalysis
            page = SaleAnalysis(parent=self.content_frame, controller=self.controller)
            page.pack(fill="both", expand=True)

        elif name == "manage product":
            page = InventoryReport(parent=self.content_frame, controller=self.controller)
            page.place(x=0, y=0, relwidth=1, relheight=1)

        elif name == "register":
            page = Register(parent=self.content_frame, controller=self.controller)
            page.place(x=0, y=0, relwidth=1, relheight=1)

        elif name == "logout":
            self.controller.logged_in_user_id = None
            self.controller.show_frame("LoginPage")
            self.controller.frames["LoginPage"].clear_fields()
