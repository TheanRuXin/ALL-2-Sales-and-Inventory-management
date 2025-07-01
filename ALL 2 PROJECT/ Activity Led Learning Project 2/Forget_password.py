import sqlite3
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import smtplib
import ssl
import certifi
import random
from email.message import EmailMessage
from ResetPassword import Reset_Password

class ForgetPasswordPage(ctk.CTkToplevel):
    def __init__(self, parent,controller=None,on_close_callback=None):
        super().__init__(parent)
        self.controller = controller
        self.on_close_callback = on_close_callback
        self.title("Reset Password")
        self.geometry("974x500")
        self.attributes("-topmost", True)
        self.resizable(False, False)

        self.width = self.winfo_screenwidth()
        self.height = self.winfo_screenheight()


        background_image = ctk.CTkImage(Image.open(r"C:\Users\User\Documents\Ruxin file\ALL 2\forget passsword.png"), size=(974,500))
        background_image_label = ctk.CTkLabel(self, image=background_image, text="")
        background_image_label.place(relx=0, rely=0)

        self.otp_code = ""
        self.email = ""

        self.set_ui()
        self.initialize_db()

    def initialize_db(self):
        conn = sqlite3.connect("Trackwise.db")
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                             id INTEGER PRIMARY KEY AUTOINCREMENT,
                             username TEXT NOT NULL,
                             role TEXT NOT NULL,
                             email TEXT NOT NULL,
                             phone TEXT NOT NULL,
                             dob TEXT NOT NULL,
                             password TEXT NOT NULL,
                             photo_path TEXT NOT NULL
                             )
                          ''')
        conn.commit()
        conn.close()

    def set_ui(self):
        # Username
        self.username_text = ctk.CTkLabel(self, text="Enter Your Username",
                                      font=("Inter", 23),
                                      bg_color="#FFFFFF", fg_color="#FFFFFF",
                                      text_color="black")
        self.username_text.place(x=400 / 1920 * self.width, y=112 / 974 * self.height)

        self.username = ctk.StringVar()
        self.username_entry = ctk.CTkEntry(self, font=("Inter", 18), width=320 / 1536 * self.width,
                                       height=45 / 864 * self.height, bg_color="#FFFFFF",
                                       fg_color="#D9D9D9", border_color="#FFFFFF", text_color="black",
                                       textvariable=self.username)
        self.username_entry.place(x=400 / 1920 * self.width, y=152 / 974 * self.height)

        # Verification Code
        self.code_text = ctk.CTkLabel(self, text="Verification Code",
                                          font=("Inter", 23),
                                          bg_color="#FFFFFF", fg_color="#FFFFFF",
                                          text_color="black")
        self.code_text.place(x=400 / 1920 * self.width, y=300 / 974 * self.height)

        self.code = ctk.StringVar()
        self.code_entry = ctk.CTkEntry(self, font=("Inter", 18), width=320 / 1536 * self.width,
                                           height=45 / 864 * self.height, bg_color="#FFFFFF",
                                           fg_color="#D9D9D9", border_color="#FFFFFF", text_color="black",
                                           textvariable=self.code)
        self.code_entry.place(x=400 / 1920 * self.width, y=350 / 974 * self.height)

        #Buttons
        # Sent OTP
        otp_button = ctk.CTkButton(self, text="Sent OTP", bg_color="white", fg_color="Blue",
                                       text_color="white",
                                       border_color="#1572D3", width=129, height=35,
                                       font=("Iter", 14), command=self.send_otp)
        otp_button.place(x=850 / 1920 * self.winfo_screenwidth(), y=155 / 974 * self.winfo_screenheight())

        # Verify
        reset_button = ctk.CTkButton(self, text="Verify", bg_color="#D9D9D9", fg_color="Blue",
                                       text_color="white",
                                       border_color="#1572D3", width=129, height=35,
                                       font=("Iter", 14), command=self.verify_otp)
        reset_button.place(x=550 / 1920 * self.winfo_screenwidth(), y=450 / 974 * self.winfo_screenheight())

        # Back
        back_button = ctk.CTkButton(self, text="Cancel", bg_color="#D9D9D9", fg_color="Blue",
                                       text_color="white",
                                       border_color="#1572D3", width=129, height=35,
                                       font=("Iter", 14), command=self.cancel)
        back_button.place(x=60 / 1920 * self.winfo_screenwidth(), y= 450/ 974 * self.winfo_screenheight())

    def cancel(self):
        if messagebox.askyesno("Exit", "Are You Sure You Want To Cancel The Process ",parent=self):
            self.destroy()

    def get_email_from_db(self, username):
        try:
            conn = sqlite3.connect("Trackwise.db")
            cursor = conn.cursor()
            cursor.execute("SELECT email FROM users WHERE username = ?", (username,))
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else None
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to retrieve email: {e}",parent=self)
            return None

    def send_otp(self):
        username_input = self.username.get()
        if not username_input:
            messagebox.showwarning("Input Required", "Please enter your username.",parent=self)
            return

        self.email = self.get_email_from_db(username_input)
        if not self.email:
            messagebox.showerror("Error", "Username not found.",parent=self)
            return

        self.otp_code = str(random.randint(100000, 999999))

        sender_email = "ruxinthean@gmail.com"
        password = "vznn pcdo pnol oiqf" # Use Gmail App Password
        subject = "Reset Password OTP"
        body = (f"Hi {username_input},\n\nYour OTP for password reset is: {self.otp_code}"
                f"\n\nDo not give this code to anyone, even if they said they are from Trackwise Inventory."
                f"\n\nThis code can be used to Reset Your Trackwise account."
                f"\n\nIf you didn't request for this code, simply ignore this message"
                f"\n\nThank you.")

        message = EmailMessage()
        message.set_content(body)
        message["From"] = sender_email
        message["To"] = self.email
        message["Subject"] = subject

        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.load_verify_locations(certifi.where())

        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls(context=context)
                server.login(sender_email, password)
                server.send_message(message)
            messagebox.showinfo("Success", f"OTP sent to {self.email}",parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send OTP: {e}",parent=self)

    def verify_otp(self):
        if not self.code.get():
            messagebox.showerror("Error", "OTP field cannot be empty.",parent=self)

        elif self.code.get() == self.otp_code:
            messagebox.showinfo("Success", "OTP verified. Proceed to reset password.",parent=self)

            with open("reset_user.txt", "w") as f:
                f.write(self.username.get())

            self.reset_window = Reset_Password(parent=self.controller, controller=self.controller)
            self.after(100, self.destroy)

        else:
            messagebox.showerror("Error", "Invalid OTP. Please try again.")
            self.code.set("")