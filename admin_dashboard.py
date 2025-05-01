import customtkinter as ctk
from PIL import Image, ImageTk
import subprocess, sys

class AdminDashboard(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Admin Dashboard")

        # Make the window resizable and fit the screen
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()
        self.geometry(f"{self.screen_width}x{self.screen_height}")  # Full screen
        self.configure(fg_color="#FFFFFF")
        self.resizable(True, True)  # Allow resizing

        self.create_main_frame()
        self.create_title()
        self.create_buttons()

    def create_main_frame(self):
        self.main_frame = ctk.CTkFrame(
            master=self,
            width=self.screen_width * 0.9,  # 90% of the screen width
            height=self.screen_height * 0.8,  # 80% of the screen height
            corner_radius=0,
            fg_color="#FFFFFF"
        )
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center")  # Center the frame

        # Add background image to main_frame
        img = Image.open("admin_dash1.png").resize(
            (int(self.screen_width * 0.9), int(self.screen_height * 0.8))
        )
        self.main_bg_image = ctk.CTkImage(light_image=img, size=(img.width, img.height))

        self.bg_label = ctk.CTkLabel(
            master=self.main_frame,
            image=self.main_bg_image,
            text=""
        )
        self.bg_label.place(relx=0.5, rely=0.5, anchor="center")

    def create_title(self):
        self.title_label = ctk.CTkLabel(
            master=self,
            text="Admin Dashboard",
            font=("Inter", 40),
            text_color="#000000"
        )
        self.title_label.place(x=self.screen_width * 0.4, y=self.screen_height * 0.1)

    def create_buttons(self):
        button_width = 450
        button_height = 50
        button_font = ("Inter", 20)

        button_info = [
            ("Register Product", 264, self.Register_Product),
            ("Manage Product Details", 400, self.Manage_Product_Details),
            ("Log Out", 536, self.Log_Out)
        ]

        for text, y_pos, command in button_info:
            btn = ctk.CTkButton(
                master=self,
                text=text,
                width=button_width,
                height=button_height,
                font=button_font,
                command=command
            )
            btn.place(x=self.screen_width * 0.36, y=y_pos)

    def Register_Product(self):
        subprocess.Popen([sys.executable, "register_product.py"])
        self.destroy()

    def Manage_Product_Details(self):
        subprocess.Popen([sys.executable, "manage_product_details.py"])
        self.destroy()

    def Log_Out(self):
        subprocess.Popen([sys.executable, "admin_and_cashier_registration.py"])
        self.destroy()

if __name__ == "__main__":
    app = AdminDashboard()
    app.mainloop()
