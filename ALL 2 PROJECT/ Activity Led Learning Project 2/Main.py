import customtkinter as ctk

# Page Imports
from main_page import MainPage
from manager_login import ManagerLoginPage
from cashier_login import CashierLogin
from Admin_login import AdminLoginPage
from admin_dashboard import AdminDashboard
from Manager_dashboard import ManagerDashboard
from Manager_Register import Manager_Register
from Admin_and_Cashier_registration import Register
from Register_Product import RegisterProductPage
from manage_product_details import ManageProductPage
from ViewSalesHistory import SalesHistoryPage
from inventory_report import InventoryReport
from profile import UserPage  # View profile
# EditProfileApp will be imported only when needed to avoid circular import

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class InventoryApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Inventory Management System")
        self.geometry("1574x800")
        self.resizable(True, True)

        self.logged_in_user_id = None
        self.frames = {}

        # Register all primary frames
        for F in (
            MainPage, ManagerLoginPage, CashierLogin, AdminLoginPage,
            AdminDashboard, ManagerDashboard, Manager_Register,
            Register, RegisterProductPage, ManageProductPage,
            SalesHistoryPage, InventoryReport
        ):
            frame = F(parent=self, controller=self)
            self.frames[F.__name__] = frame
            frame.place(x=0, y=0, relwidth=1, relheight=1)

        self.show_frame("MainPage")

    def show_frame(self, page_name):
        frame = self.frames.get(page_name)
        if frame:
            frame.tkraise()
        else:
            print(f"[Error] Frame '{page_name}' not found.")

    def show_profile(self, user_id):
        if "UserProfileApp" in self.frames:
            self.frames["UserProfileApp"].destroy()

        profile_frame = UserPage(parent=self, controller=self, user_id=user_id)
        self.frames["UserProfileApp"] = profile_frame
        profile_frame.place(x=0, y=0, relwidth=1, relheight=1)
        profile_frame.tkraise()

    def show_edit_profile(self, user_id):
        from profile_edit import EditProfileApp  # Dynamic import to avoid circular import
        if "EditProfileApp" in self.frames:
            self.frames["EditProfileApp"].destroy()

        edit_frame = EditProfileApp(parent=self, controller=self, user_id=user_id)
        self.frames["EditProfileApp"] = edit_frame
        edit_frame.place(x=0, y=0, relwidth=1, relheight=1)
        edit_frame.tkraise()

    def show_dashboard(self, dashboard_class):
        frame = dashboard_class(self.container, self)
        frame.place(x=0, y=0, relwidth=1, relheight=1)


if __name__ == "__main__":
    app = InventoryApp()
    app.mainloop()
