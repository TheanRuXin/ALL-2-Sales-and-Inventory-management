import customtkinter as ctk
from PIL import Image

class MainPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.width = 1574
        self.height = 800

        background_image = ctk.CTkImage(Image.open(r"main.png"), size=(self.width, self.height))
        background_label = ctk.CTkLabel(self, image=background_image, text="")
        background_label.place(x=0, y=0)

        bold_font = ctk.CTkFont(family="Arial", size=50, weight="bold")

        ctk.CTkButton(self, text="Manager", font=bold_font, fg_color="#2A50CB",
                      width=550, height=100, text_color="#FFFFFF",
                      corner_radius=50, command=lambda: controller.show_frame("ManagerLoginPage")
                      ).place(x=500, y=200)
        ctk.CTkButton(self, text="Admin", font=bold_font, fg_color="#2A50CB",
                      width=550, height=100, text_color="#FFFFFF",
                      corner_radius=50, command=lambda: controller.show_frame("AdminLoginPage")
                      ).place(x=500, y=350)
        ctk.CTkButton(self, text="Cashier", font=bold_font, fg_color="#2A50CB",
                      width=550, height=100, text_color="#FFFFFF",
                      corner_radius=50, command=lambda: controller.show_frame("CashierLogin")
                      ).place(x=500, y=500)