import sqlite3
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import subprocess

class Manager_Login:
    def __init__(self,root):
        self.root = root
        self.root.title("Inventory Management System")
        self.root.geometry("1920x974")

        self.width = self.root.winfo_screenwidth()
        self.height = self.root.winfo_screenheight()

        background_image = ctk.CTkImage(Image.open("assets/Manager_Login.png"), size=(self.width, self.height - 71))
        background_image_label = ctk.CTkLabel(self.root, image=background_image, text="")
        background_image_label.place(relx=0, rely=0)

        #self.initialize_db()
        self.setup_ui()

    def login(self):
        username = self.username.get()
        password = self.password.get()

        conn = sqlite3.connect("Trackwise.db")
        cursor = conn.cursor()
        cursor.execute("SELECT role from users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            role = user[0]
            messagebox.showinfo("login Successful", f"Welcome {role.capitalize()}!")
            self.root.destroy()

            if role == "Admin":
                subprocess.Popen(["python", "Admin_Dashboard.py"])
            elif role == "Cashier":
                subprocess.Popen(["python", "Cashier_Dashboard.py"])
            elif role == "Manager":
                subprocess.Popen(["python", "Manager_Dashboard.py"])
            else:
                messagebox.showerror("Error", "Unknown user role. Please contact Manager.")
        else:
            messagebox.showerror("Error","Invalid Username or Password")

    #def forgot_password(self):

    def register(self):
        self.root.destroy()
        subprocess.Popen(["python", "register.py"])

    def setup_ui(self):
        #Welcome

        # Username
        username_label = ctk.CTkLabel(self.root, text="Username:",
                                    font=("Inter",22),
                                    bg_color="#D9D9D9",
                                    text_color="Black")
        username_label.place(x=150 / 1920 * self.width, y=380/ 974 * self.height)

        self.username = ctk.StringVar()
        username_entry = ctk.CTkEntry(self.root, width=395 / 1536 * self.width,
                                   height=45 / 864 * self.height, bg_color="#D9D9D9",
                                   fg_color="white", border_color="#D9D9D9", text_color="black",
                                   textvariable=self.username)
        username_entry.place(x=148 / 1920 * self.width, y=418 / 974 * self.height)

        #Password
        password_label = ctk.CTkLabel(self.root, text="Password:",
                                    font=("Inter",22),
                                    bg_color="#D9D9D9", fg_color="#D9D9D9",
                                    text_color="black")
        password_label.place(x=152 / 1920 * self.width, y=490 / 974 * self.height)

        self.password = ctk.StringVar()
        password_entry = ctk.CTkEntry(self.root, width=395 / 1536 * self.width,
                                   height=45 / 864 * self.height, bg_color="#D9D9D9",
                                   fg_color="white", border_color="#D9D9D9", text_color="black",
                                   textvariable=self.password)
        password_entry.place(x=148 / 1920 * self.width, y=528 / 974 * self.height)

        #Forget Password
        forgot_label = ctk.CTkLabel(self.root, text="Forgot Password?",
                                    font=("Inter",15),
                                    bg_color="#D9D9D9",text_color="Blue")
        forgot_label.place(x=451 / 1920 * self.width, y=580 / 974 * self.height)

        #Login
        login_button = ctk.CTkButton(self.root, text="Login", bg_color="#D9D9D9", fg_color="Blue",
                                                 text_color="white",
                                                 border_color="#1572D3", width=160, height=44,
                                                 font=("Iter", 18))
        login_button.place(x=273 / 1920 * root.winfo_screenwidth(), y=645 / 974 * root.winfo_screenheight())

        #Don't have an Account
        account_label = ctk.CTkLabel(self.root, text="Don't have an account?",
                                      font=("Inter", 15),
                                      bg_color="#D9D9D9", fg_color="#D9D9D9",
                                      text_color="black")
        account_label.place(x=285 / 1920 * self.width, y=715 / 974 * self.height)

        #New Account
        new_label = ctk.CTkLabel(self.root, text="Create a New Account", font=("Arial", 17), bg_color="#D9D9D9",
                                    text_color="#5885F0")
        new_label.place(x=266 / 1920 * self.width, y=740 / 974 * self.height)

        #I'm Cashier
        cashier_button = ctk.CTkButton(self.root, text="I'm Cashier", bg_color="#D9D9D9", fg_color="Blue",
                                                 text_color="white",
                                                 border_color="#1572D3", width=159, height=44,
                                                 font=("Iter", 18))
        cashier_button.place(x=866 / 1920 * root.winfo_screenwidth(), y=759 / 974 * root.winfo_screenheight())

        #I'm Admin
        admin_button = ctk.CTkButton(root, text="I'm Admin", bg_color="#D9D9D9", fg_color="Blue",
                                       text_color="white",
                                       border_color="#1572D3", width=159, height=44,
                                       font=("Iter", 18))
        admin_button.place(x=1623 / 1920 * root.winfo_screenwidth(), y=759 / 974 * root.winfo_screenheight())


root = ctk.CTk()

app = Manager_Login(root)

root.mainloop()