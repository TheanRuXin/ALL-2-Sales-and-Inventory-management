import customtkinter as ctk
from PIL import Image
import os

# Page imports
from dashboard_page import load_dashboard_content
from user_page import UserPage
from inventory_page import load_inventory_content
from home_page import load_home_content
from settings_page import load_settings_content
from categories_pages import load_categories_content



ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class POSApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Trackwise")
        self.geometry("1200x700")
        self.iconbitmap("images/favicon (3).ico")
        self.nav_items = ["dashboard", "user", "inventory", "home", "tag", "settings"]
        self.icons = {}
        self.buttons = {}
        self.active_button = None

        self.create_sidebar()
        self.create_content_area()
        self.load_page("dashboard")

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
        self.active_button_name = name

    def load_page(self, name):
        self.clear_content()
        self.set_active_button(name)

        if name == "dashboard":
            load_dashboard_content(self.content_frame)
        elif name == "user":
            UserPage(self.content_frame)
        elif name == "inventory":
            load_inventory_content(self.content_frame)
        elif name == "home":
            load_home_content(self.content_frame)
        elif name == "tag":
            load_categories_content(self.content_frame)
        elif name == "settings":
            load_settings_content(self.content_frame)
        else:
            ctk.CTkLabel(self.content_frame, text=f"{name.capitalize()} Page Coming Soon...",
                         font=("Arial", 20)).pack(pady=50)


if __name__ == "__main__":
    app = POSApp()
    app.mainloop()
