import customtkinter as ctk
from PIL import Image
from tkinter import messagebox
import sqlite3
import bcrypt
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class Register(ctk.CTkFrame):
    def __init__(self,parent,controller):
        super().__init__(parent)
        self.controller = controller
        self.screen_width = 1920
        self.screen_height = 974
        self.configure(fg_color="#FFFFFF", width=self.screen_width, height=self.screen_height)

        self.Trackwise_db()

        try:
            logo_image = Image.open(r"C:\Users\User\Documents\Ruxin file\ALL 2\logo.png").resize((80, 80))
            ctk_logo_image = ctk.CTkImage(light_image=logo_image, dark_image=logo_image, size=(80, 80))
            logo_frame = ctk.CTkFrame(self, fg_color="transparent")
            logo_frame.place(x=10, y=10)

            logo_label = ctk.CTkLabel(logo_frame, image=ctk_logo_image, text="")
            logo_label.pack()
        except Exception as e:
            print(f"Error loading bot image: {e}")

        # Main Frame for "Create Account"
        main_frame = ctk.CTkFrame(self, fg_color="#D9D9D9", border_width=0, corner_radius=15)
        main_frame.pack(pady=(50,50), padx=200, fill="both", expand=True)

        ctk.CTkLabel(main_frame, text="Register New Account", font=("Arial", 40, "bold")).pack(pady=10)

        second_frame = ctk.CTkFrame(main_frame, fg_color="#FFFFFF", corner_radius=15)
        second_frame.pack(pady=(20, 50), padx=100, fill="both", expand=True)

        # Split into two columns inside second_frame
        left_frame = ctk.CTkFrame(second_frame, fg_color="transparent")
        left_frame.grid(row=0, column=0, padx=50, pady=20, sticky="n")

        right_frame = ctk.CTkFrame(second_frame, fg_color="transparent")
        right_frame.grid(row=0, column=1, padx=50, pady=20, sticky="n")

        # Left side: Username, Email, Role
        ctk.CTkLabel(left_frame, text="Username:", font=("Arial", 24)).pack(pady=(10,5), anchor="w")
        self.username_entry = ctk.CTkEntry(left_frame, placeholder_text="Username", width=350, height=35,justify="center", font=("Arial", 24))
        self.username_entry.pack(pady=(0, 30))

        ctk.CTkLabel(left_frame, text="Email:", font=("Arial", 24)).pack(pady=(10,5), anchor="w")
        self.email_entry = ctk.CTkEntry(left_frame, placeholder_text="Email", width=350, height=35, justify="center",font=("Arial", 24))
        self.email_entry.pack(pady=(0, 30))

        ctk.CTkLabel(left_frame, text="Select User Type:", font=("Arial", 24)).pack(pady=(10,5), anchor="w")
        self.role_var = ctk.StringVar(value="Select User Type")
        self.role_dropdown = ctk.CTkComboBox(left_frame, values=["Admin", "Cashier"], variable=self.role_var, width=350,height=35)
        self.role_dropdown.pack(pady=(0, 30))

        # Right side: Password and Confirm Password
        ctk.CTkLabel(right_frame, text="Phone Number:", font=("Arial", 24)).pack(pady=(10, 5), anchor="w")
        self.phone_entry = ctk.CTkEntry(right_frame, placeholder_text="ex:+60121234567", width=350, height=35,justify="center", font=("Arial", 24))
        self.phone_entry.pack(pady=(0, 30))

        ctk.CTkLabel(right_frame, text="Password:", font=("Arial", 24)).pack(pady=(10,5), anchor="w")
        self.password_entry = ctk.CTkEntry(right_frame, placeholder_text="Password", show="*", width=350, height=35,justify="center", font=("Arial", 24))
        self.password_entry.pack(pady=(0, 30))

        ctk.CTkLabel(right_frame, text="Confirm Password:", font=("Arial", 24)).pack(pady=(10,5), anchor="w")
        self.confirm_password_entry = ctk.CTkEntry(right_frame, placeholder_text="Confirm Password", show="*",width=350, height=35, justify="center", font=("Arial", 24))
        self.confirm_password_entry.pack(pady=(0, 30))

        # Back button
        self.register_button = ctk.CTkButton(main_frame, text="Register", width=250, height=40, font=("Arial", 24),hover_color="#1a39a3", command=self.register_user)
        self.register_button.pack(pady=(1, 20), anchor='center')

        self.view_employee_button = ctk.CTkButton(main_frame, text="View Employee", width=250, height=40,
                                                  font=("Arial", 20), corner_radius=10, fg_color="#1a73e8",
                                                  hover_color="#1a39a3", text_color="white",
                                                  command=self.view_employee
                                                  )
        self.view_employee_button.pack(pady=(1,20),anchor="ne")

    def Trackwise_db(self):
        conn = sqlite3.connect("Trackwise.db")
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    role TEXT NOT NULL,
                    email TEXT, phone TEXT, dob TEXT,
                    password TEXT NOT NULL, photo_path TEXT)''')
        conn.commit()
        conn.close()

    def hash_password(self,password):
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    def send_email(self, username, password, recipient_email):
        sender_email = "ruxinthean@gmail.com"  # Replace with your email
        sender_password = "vznn pcdo pnol oiqf"  # Replace with your email password (use app password for Gmail)
        subject = "Account Registration"
        body = f"Dear {username},\n\nYour account has been successfully created.\n\nUsername: {username}\nPassword: {password}\n\nPlease keep your login credentials safe.\n\nBest Regards,\nTrackwise Support"

        # Create the email
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        # Connect to the server and send email
        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, recipient_email, msg.as_string())
                print("Email sent successfully!")
        except Exception as e:
            print(f"Error sending email: {e}")

    def validate_email(self, email):
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            messagebox.showerror("Error", "Invalid email format.")
            return False
        conn = sqlite3.connect("Trackwise.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        result = cursor.fetchone()
        conn.close()
        if result:
            messagebox.showerror("Error", "Email already registered.")
            return False

        return True

    def validate_phone(self, phone):
        if not phone.startswith("+60"):
            messagebox.showerror("Error", "Phone number must start with +60.")
            return False
        if not phone[1:].isdigit():  # skip the '+' sign
            messagebox.showerror("Error", "Phone number must be digits.")
            return False
        return True

    def register_user(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        phone = self.phone_entry.get().strip()
        confirm_password = self.confirm_password_entry.get().strip()
        email = self.email_entry.get().strip()
        role = self.role_var.get()

        if not username or not password or not confirm_password or not email or not phone:
            messagebox.showerror("Error", "Fields cannot be empty!")
            return

        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match!")
            return

        if role == "Select User Type":
            messagebox.showerror("Error", "Please select a user role!")
            return

        if len(password) < 8 or not re.search(r'\d', password) or not re.search(r'[A-Z]', password):
            messagebox.showerror("Error",
                                 "Password must be at least 8 characters long, with one number and one uppercase letter.")
            return
        if email and not self.validate_email(email):
            return
        if phone and not self.validate_phone(phone):
            return

        conn = sqlite3.connect('Trackwise.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))

        if cursor.fetchone():
            messagebox.showerror("Error", "Username already exists!")
            conn.close()
            return

        hashed_pw = self.hash_password(password)

        cursor.execute("""INSERT INTO users (username, password,role,email,phone) VALUES (?,?,?,?,?)""", (username, hashed_pw,role,email,phone))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "User registered successfully!")
        recipient_email = email
        self.send_email(username, password, recipient_email)
        self.username_entry.delete(0, 'end')
        self.email_entry.delete(0, 'end')
        self.role_var.set("Select User Type")
        self.phone_entry.delete(0, 'end')
        self.password_entry.delete(0, 'end')
        self.confirm_password_entry.delete(0, 'end')

    def view_employee(self):
        messagebox.showinfo("View Employee", "This will take you to the employee list page.")
        if self.controller.current_dashboard:
            self.controller.current_dashboard.load_page("Employee_List")
        else:
            self.controller.show_frame("EmployeeListPage")
