import customtkinter as ctk

from Manager_dashboard import ManagerDashboard
from admin_dashboard import AdminDashboard
from manage_product_details import ManageProductPage
from manager_login import LoginPage
from Admin_and_Cashier_registration import Register
from Register_Product import RegisterProductPage
from ViewSalesHistory import SalesHistoryPage
from inventory_report import InventoryReport
from cashier_main import POSApp
from profile import UserProfileApp

class InventoryApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Inventory Management System")
        self.geometry("1574x800")
        ctk.set_appearance_mode("light")
        self.logged_in_user_id = None

        self.frames = {}
        for F in ( AdminDashboard, LoginPage, ManagerDashboard,Register,RegisterProductPage,ManageProductPage, SalesHistoryPage,InventoryReport,POSApp):
            page_name = F.__name__
            frame = F(parent=self, controller=self)
            self.frames[page_name] = frame
            frame.place(x=0, y=0, relwidth=1, relheight=1)

        self.show_frame("LoginPage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

    def show_profile(self, user_id):
        if "UserProfileApp" in self.frames:
            self.frames["UserProfileApp"].destroy()
        profile_frame = UserProfileApp(parent=self, controller=self,user_id=self)
        self.frames["UserProfileApp"] = profile_frame
        profile_frame.place(x=0, y=0, relwidth=1, relheight=1)
        profile_frame.tkraise()

if __name__ == "__main__":
    app = InventoryApp()
    app.mainloop()
