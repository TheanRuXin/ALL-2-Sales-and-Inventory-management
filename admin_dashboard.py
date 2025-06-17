import customtkinter as ctk
from PIL import Image

class AdminDashboard(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.screen_width = 1920
        self.screen_height = 974
        self.configure(fg_color="#FFFFFF", width=self.screen_width, height=self.screen_height)

        self.create_main_frame()
        self.create_title()
        self.create_buttons()

    def create_main_frame(self):
        self.main_frame = ctk.CTkFrame(master=self, width=1547, height=800, fg_color="#FFFFFF")
        self.main_frame.place(x=0, y=0)

        try:
            img = Image.open(r"C:\Users\User\Documents\Ruxin file\ALL 2\admin_dash1.png").resize((1547, 800))
            self.main_bg_image = ctk.CTkImage(light_image=img, size=(1547, 800))

            self.bg_label = ctk.CTkLabel(
                master=self.main_frame,
                image=self.main_bg_image,
                text=""
            )
            self.bg_label.place(x=0, y=0)
        except Exception as e:
            print(f"Error loading background image: {e}")

    def create_title(self):
        self.title_label = ctk.CTkLabel(
            master=self,
            text="Admin Dashboard",
            font=("Arial", 50),
            text_color="#000000"
        )
        self.title_label.place(x=550, y=100)

    def create_buttons(self):
        button_width = 600
        button_height = 80
        button_font = ("Arial", 30)

        button_info = [
            ("Register Product", 50, self.register_product),
            ("Manage Product Details", 200, self.manage_product_details),
            ("Log Out", 350, self.logout)
        ]

        for text, y_pos, command in button_info:
            btn = ctk.CTkButton(
                master=self,
                text=text,
                width=button_width,
                height=button_height,
                font=button_font,
                fg_color="#2A50CB",
                hover_color="#1a39a3",
                command=command
            )
            btn.place(x=450, y=y_pos + 200)

    def register_product(self):
        self.controller.show_frame("RegisterProductPage")

    def manage_product_details(self):
        self.controller.show_frame("ManageProductPage")

    def logout(self):
        self.controller.show_frame("AdminLoginPage")
