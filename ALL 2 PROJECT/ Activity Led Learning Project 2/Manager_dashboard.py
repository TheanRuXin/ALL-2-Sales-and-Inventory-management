import os
import customtkinter as ctk
from PIL import Image
from ViewSalesHistory import SalesHistoryPage
from inventory_report import InventoryReport
from Admin_and_Cashier_registration import Register
from profile import UserPage


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

    def load_page(self, name):
        self.clear_content()
        self.set_active_button(name)

        if name == "home":
            ctk.CTkLabel(self.content_frame, text="Manager Dashboard", font=("Arial", 32)).pack(pady=50)



        elif name == "user":

            page = UserPage(parent=self.content_frame, controller=self.controller,
                            user_id=self.controller.logged_in_user_id)

            page.pack(fill="both", expand=True)

        elif name == "saleS":
            page = SalesHistoryPage(parent=self.content_frame, controller=self.controller)
            page.place(x=0, y=0, relwidth=1, relheight=1)

        elif name == "manage product":
            page = InventoryReport(parent=self.content_frame, controller=self.controller)
            page.place(x=0, y=0, relwidth=1, relheight=1)

        elif name == "register":
            page = Register(parent=self.content_frame, controller=self.controller)
            page.place(x=0, y=0, relwidth=1, relheight=1)

        elif name == "logout":
            self.controller.logged_in_user_id = None
            self.controller.show_frame("MainPage")

        else:
            ctk.CTkLabel(self.content_frame, text=f"{name.capitalize()} Page Coming Soon...", font=("Arial", 24)).pack(pady=50)
