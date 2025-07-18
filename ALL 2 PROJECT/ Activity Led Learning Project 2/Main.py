import customtkinter as ctk

from Manager_dashboard import ManagerDashboard
from admin_dashboard import AdminDashboard
from manage_product_details import ManageProductPage
from manager_login import LoginPage
from Admin_and_Cashier_registration import Register
from Register_Product import RegisterProductPage
from ViewSalesHistory import SalesHistoryPage
from inventory_report import InventoryReport
from cashier_dashboard import CashierDashboard
from sales_analysis import SaleAnalysis


class InventoryApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Inventory Management System")
        self.geometry("1574x800")
        ctk.set_appearance_mode("light")
        self.logged_in_user_id = None
        self.frames = {}


        for F in ( AdminDashboard, LoginPage, ManagerDashboard,Register,RegisterProductPage,ManageProductPage, SalesHistoryPage,InventoryReport,CashierDashboard,SaleAnalysis):
            page_name = F.__name__
            frame = F(parent=self, controller=self)
            self.frames[page_name] = frame
            frame.place(x=0, y=0, relwidth=1, relheight=1)

        self.show_frame("LoginPage")

    def show_frame(self, page_name):
        # Destroy and refresh dashboards only
        if "Dashboard" in page_name and page_name in self.frames:
            self.frames[page_name].destroy()
            page_class = globals()[page_name]
            new_frame = page_class(parent=self, controller=self)
            self.frames[page_name] = new_frame
            new_frame.place(x=0, y=0, relwidth=1, relheight=1)

        # Raise the frame
        frame = self.frames.get(page_name)
        if frame:
            # Unbind Enter key from all other pages
            for name, f in self.frames.items():
                if hasattr(f, "unbind_enter_key"):
                    f.unbind_enter_key()

            # Bind Enter key ONLY if the frame supports it (like LoginPage)
            if hasattr(frame, "bind_enter_key"):
                frame.bind_enter_key()

            self.current_dashboard = frame if "Dashboard" in page_name else None
            frame.tkraise()
        else:
            print(f"[Error] Frame '{page_name}' not found.")

    def show_profile(self, user_id):
        from profile import UserProfileApp
        if "UserProfileApp" in self.frames:
            self.frames["UserProfileApp"].destroy()

        profile_frame = UserProfileApp(parent=self, controller=self, user_id=user_id)
        self.frames["UserProfileApp"] = profile_frame
        profile_frame.place(x=0, y=0, relwidth=1, relheight=1)
        profile_frame.tkraise()

    def show_edit_profile(self, user_id):
        from profile_edit import EditProfileApp
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
