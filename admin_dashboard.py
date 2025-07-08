import customtkinter as ctk
from PIL import Image
from Register_Product import RegisterProductPage
from manage_product_details import ManageProductPage
from profile import UserProfileApp
import os
import sqlite3
from datetime import datetime
class AdminDashboard(ctk.CTkFrame):
    def __init__(self, parent, controller,user_data = None):
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

    def get_user_info(self):
        try:
            conn = sqlite3.connect("Trackwise.db")
            cursor = conn.cursor()
            cursor.execute("SELECT username, photo_path FROM users WHERE id = ?", (self.user_id,))
            row = cursor.fetchone()
            conn.close()
            if row:
                return row[0], row[1]
            else:
                return "Admin", None
        except Exception as e:
            print("Error fetching user info:", e)
            return "Admin", None

    def load_page(self, name, user_id=None):
        self.clear_content()
        self.set_active_button(name)

        if name == "home":
            self.user_id = self.controller.logged_in_user_id
            self.username, photo_path = self.get_user_info()
            self.clear_content()

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

            # ✅ Welcome title
            welcome = ctk.CTkLabel(
                self.content_frame,
                text=f"Welcome, {self.username} 👑",
                font=("Arial", 28, "bold"),
                text_color="#2d3436"
            )
            welcome.pack(pady=(10, 0))

            # 🕒 Login time
            time_label = ctk.CTkLabel(
                self.content_frame,
                text=f"Login Time: {current_time}",
                font=("Arial", 16),
                text_color="#636e72"
            )
            time_label.pack(pady=(0, 20))

            # ✨ Slogan or mission
            slogan = ctk.CTkLabel(
                self.content_frame,
                text="Empowering Inventory, Simplifying Success.",
                font=("Georgia", 20, "italic"),
                text_color="#0984e3"
            )
            slogan.pack(pady=10)

            # 🧾 Admin rules/policies
            rules_frame = ctk.CTkFrame(self.content_frame, fg_color="#f5f6fa", corner_radius=10)
            rules_frame.pack(pady=20, padx=100, fill="x")

            rules_title = ctk.CTkLabel(
                rules_frame,
                text="🔒 Admin Panel Usage Rules",
                font=("Arial", 18, "bold"),
                text_color="#2c3e50"
            )
            rules_title.pack(pady=(15, 5))

            rules_list = [
                "• Only authorized personnel can access admin features.",
                "• Ensure data accuracy before updates.",
                "• Do not share login credentials.",
                "• Always log out after use.",
                "• Contact IT support for technical issues.",
                "• Regularly back up data to prevent loss.",
                "• Monitor sales and inventory reports weekly.",
                "• Verify product details before registering.",
                "• Deactivate accounts when employees leave.",
                "• Maintain professionalism in all records."
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
            page = UserProfileApp(
                parent=self.content_frame,
                controller=self.controller,
                user_id=self.controller.logged_in_user_id
            )
            page.pack(fill="both", expand=True)

        elif name == "edit_profile":
            if user_id is None:
                user_id = self.controller.logged_in_user_id

            from profile_edit import EditProfileApp
            page = EditProfileApp(
                parent=self.content_frame,
                controller=self.controller,
                user_id=user_id
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
            self.controller.show_frame("LoginPage")
            self.controller.frames["LoginPage"].clear_fields()

        else:
            ctk.CTkLabel(self.content_frame, text="Page coming soon...", font=("Arial", 24)).pack(pady=50)
