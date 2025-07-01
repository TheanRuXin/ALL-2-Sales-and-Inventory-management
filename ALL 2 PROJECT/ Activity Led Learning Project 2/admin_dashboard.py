import os
import customtkinter as ctk
from PIL import Image
from Register_Product import RegisterProductPage
from manage_product_details import ManageProductPage
from profile import UserPage  # ✅ Make sure profile.py has UserPage properly defined

class AdminDashboard(ctk.CTkFrame):
    def __init__(self, parent, controller, user_data=None):
        super().__init__(parent)
        self.controller = controller
        self.user_data = user_data or ("", "", "")
        self.username = self.user_data[1]
        self.user_id = self.controller.logged_in_user_id

        self.nav_items = {
            "home": "Home",
            "user": "User",
            "register product": "Register Product",
            "manage product": "Manage Products",
            "logout": "Logout"
        }

        self.icons = {}
        self.buttons = {}
        self.active_button = None

        self.create_sidebar()
        self.create_content_area()
        self.load_page("home")

    def create_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=150, fg_color="#cce7f9", corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        btn_container = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        btn_container.pack(expand=True)

        for item in self.nav_items:
            img_path = os.path.join("images", f"{item}.png")
            try:
                if os.path.exists(img_path):
                    self.icons[item] = ctk.CTkImage(Image.open(img_path), size=(40, 40))
                else:
                    self.icons[item] = None
            except Exception as e:
                print(f"Error loading icon for {item}: {e}")
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
        self.content_frame = ctk.CTkFrame(self, fg_color="white")
        self.content_frame.pack(side="right", expand=True, fill="both")

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def set_active_button(self, name):
        for key, btn in self.buttons.items():
            btn.configure(fg_color="#ffffff" if key == name else "transparent")

    def load_page(self, name):
        self.clear_content()
        self.set_active_button(name)

        if name == "home":
            ctk.CTkLabel(self.content_frame, text=f"Welcome, {self.username}!", font=("Arial", 32)).pack(pady=50)

        elif name == "user":
            page = UserPage(
                parent=self.content_frame,
                controller=self.controller,
                user_id=self.user_id
            )
            page.pack(fill="both", expand=True)

        elif name == "register product":
            page = RegisterProductPage(
                parent=self.content_frame,
                controller=self.controller
            )
            page.pack(fill="both", expand=True)

        elif name == "manage product":
            page = ManageProductPage(
                parent=self.content_frame,
                controller=self.controller
            )
            page.pack(fill="both", expand=True)

        elif name == "logout":
            self.controller.logged_in_user_id = None
            self.controller.show_frame("MainPage")

        else:
            ctk.CTkLabel(self.content_frame, text="Page coming soon...", font=("Arial", 24)).pack(pady=50)
