import customtkinter as ctk
import sqlite3
from tkinter import ttk, messagebox


class EmployeeListPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(fg_color="#FFFFFF")
        self.selected_user_id = None
        self.selected_role = None
        self.is_archived = False
        self.setup_ui()

    def setup_ui(self):
        ctk.CTkLabel(self, text="Employee Management", font=("Arial", 36, "bold"), text_color="black").pack(pady=20)

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(padx=40, pady=10, fill="both", expand=True)

        # Static Right Sidebar
        detail_frame = ctk.CTkFrame(container, fg_color="#e5e5e5", corner_radius=15, width=400)
        detail_frame.pack(side="right", fill="y", padx=(20, 0))

        ctk.CTkLabel(detail_frame, text="Employee Details", font=("Arial", 26, "bold")).pack(pady=(20, 10))

        self.label_id = ctk.CTkLabel(detail_frame, text="ID: ", font=("Arial", 20))
        self.label_id.pack(pady=5)

        self.label_username = ctk.CTkLabel(detail_frame, text="Username: ", font=("Arial", 20))
        self.label_username.pack(pady=5)

        self.label_email = ctk.CTkLabel(detail_frame, text="Email: ", font=("Arial", 20))
        self.label_email.pack(pady=5)

        self.label_phone = ctk.CTkLabel(detail_frame, text="Phone: ", font=("Arial", 20))
        self.label_phone.pack(pady=5)

        self.label_role = ctk.CTkLabel(detail_frame, text="Role: ", font=("Arial", 20))
        self.label_role.pack(pady=5)

        self.make_admin_btn = ctk.CTkButton(detail_frame, text="Make Admin", command=self.make_admin, width=200)
        self.make_admin_btn.pack(pady=5)

        self.make_cashier_btn = ctk.CTkButton(detail_frame, text="Make Cashier", command=self.make_cashier, width=200)
        self.make_cashier_btn.pack(pady=5)

        self.deactivate_btn = ctk.CTkButton(detail_frame, text="Deactivate", command=self.deactivate_user,
                                            width=200, fg_color="#D32F2F", hover_color="#B71C1C")
        self.deactivate_btn.pack(pady=5)

        self.activate_btn = ctk.CTkButton(detail_frame, text="Activate", command=self.activate_user,
                                          width=200, fg_color="#4CAF50", hover_color="#388E3C")
        self.activate_btn.pack(pady=5)

        table_frame = ctk.CTkFrame(container, fg_color="#f0f0f0", corner_radius=10)
        table_frame.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(table_frame, text="Active Employees", font=("Arial", 20, "bold")).pack()
        columns = ("ID", "Username", "Role", "Email", "Phone")
        self.tree_active = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
        for col in columns:
            self.tree_active.heading(col, text=col)
            self.tree_active.column(col, anchor="center", width=150)
        self.tree_active.bind("<<TreeviewSelect>>", lambda e: self.display_selected_user(e, archived=False))
        self.tree_active.pack(pady=(10, 20), fill="x")

        ctk.CTkLabel(table_frame, text="Archived Employees", font=("Arial", 20, "bold")).pack()
        self.tree_archived = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
        for col in columns:
            self.tree_archived.heading(col, text=col)
            self.tree_archived.column(col, anchor="center", width=150)
        self.tree_archived.bind("<<TreeviewSelect>>", lambda e: self.display_selected_user(e, archived=True))
        self.tree_archived.pack(pady=(10, 10), fill="x")

        self.create_archive_table()
        self.load_employees()

    def create_archive_table(self):
        conn = sqlite3.connect("Trackwise.db")
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS archived_users (
                            id INTEGER PRIMARY KEY,
                            username TEXT NOT NULL,
                            role TEXT NOT NULL,
                            email TEXT, phone TEXT, dob TEXT,
                            password TEXT NOT NULL, photo_path TEXT)''')
        conn.commit()
        conn.close()

    def load_employees(self):
        conn = sqlite3.connect("Trackwise.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, role, email, phone FROM users")
        active_users = cursor.fetchall()
        cursor.execute("SELECT id, username, role, email, phone FROM archived_users")
        archived_users = cursor.fetchall()
        conn.close()

        for tree in [self.tree_active, self.tree_archived]:
            for row in tree.get_children():
                tree.delete(row)

        for row in active_users:
            self.tree_active.insert("", "end", values=row)

        for row in archived_users:
            self.tree_archived.insert("", "end", values=row)

    def display_selected_user(self, event, archived=False):
        tree = self.tree_archived if archived else self.tree_active
        selected_item = tree.selection()
        if not selected_item:
            return
        values = tree.item(selected_item[0], "values")
        self.selected_user_id = values[0]
        self.selected_role = values[2]
        self.is_archived = archived

        self.label_id.configure(text=f"ID: {values[0]}")
        self.label_username.configure(text=f"Username: {values[1]}")
        self.label_email.configure(text=f"Email: {values[3]}")
        self.label_phone.configure(text=f"Phone: {values[4]}")
        self.label_role.configure(text=f"Role: {values[2]}")

    def make_admin(self):
        if self.invalid_for_role_change(): return
        if self.selected_role == "Admin":
            messagebox.showinfo("Info", "Already an Admin.")
            return
        self.update_user_role("Admin")

    def make_cashier(self):
        if self.invalid_for_role_change(): return
        if self.selected_role == "Cashier":
            messagebox.showinfo("Info", "Already a Cashier.")
            return
        self.update_user_role("Cashier")

    def deactivate_user(self):
        if not self.selected_user_id or self.selected_role == "Manager":
            messagebox.showerror("Restricted", "Cannot deactivate this user.")
            return
        if self.is_archived:
            messagebox.showinfo("Already Archived", "This user is already deactivated.")
            return
        if not messagebox.askyesno("Confirm", "Deactivate this employee?"):
            return
        try:
            conn = sqlite3.connect("Trackwise.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (self.selected_user_id,))
            user_data = cursor.fetchone()
            email = user_data[3]
            cursor.execute("INSERT INTO archived_users VALUES (?, ?, ?, ?, ?, ?, ?, ?)", user_data)
            cursor.execute("DELETE FROM users WHERE id = ?", (self.selected_user_id,))
            conn.commit()
            if email:
                subject = "Account Deactivated"
                body = "Dear user,\n\nYour account has been deactivated. Please contact your manager if this was unexpected."
                self.send_email_notification(email, subject, body)

            conn.close()
            messagebox.showinfo("Success", "User archived.")
            self.load_employees()
            self.clear_display()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to deactivate.\n{e}")

    def activate_user(self):
        if not self.selected_user_id or self.selected_role == "Manager":
            messagebox.showerror("Restricted", "Cannot activate this user.")
            return
        if not self.is_archived:
            messagebox.showinfo("Already Active", "This user is already active.")
            return
        if not messagebox.askyesno("Confirm", "Activate this employee?"):
            return
        try:
            conn = sqlite3.connect("Trackwise.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM archived_users WHERE id = ?", (self.selected_user_id,))
            user_data = cursor.fetchone()
            email = user_data[3]
            cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?)", user_data)
            cursor.execute("DELETE FROM archived_users WHERE id = ?", (self.selected_user_id,))
            conn.commit()
            if email:
                subject = "Account Activated"
                body = "Dear user,\n\nYour account has been reactivated. You can now log in again.\n\nThank you."
                self.send_email_notification(email, subject, body)

            conn.close()
            messagebox.showinfo("Success", "User activated.")
            self.load_employees()
            self.clear_display()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to activate.\n{e}")

    def update_user_role(self, new_role):
        try:
            conn = sqlite3.connect("Trackwise.db")
            cursor = conn.cursor()
            cursor.execute("SELECT email FROM users WHERE id = ?", (self.selected_user_id,))
            email_result = cursor.fetchone()
            cursor.execute("UPDATE users SET role = ? WHERE id = ?", (new_role, self.selected_user_id))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", f"Role updated to {new_role}.")
            self.load_employees()
            self.clear_display()

            if email_result and email_result[0]:
                subject = "Your Role Has Been Updated"
                body = f"Dear user,\n\nYour position has been changed to '{new_role}'.\n\nIf you have any inquiry.Please contact your manager if this was unexpected."
                self.send_email_notification(email_result[0], subject, body)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to update role.\n{e}")

    def clear_display(self):
        self.selected_user_id = None
        self.selected_role = None
        self.is_archived = False
        self.label_id.configure(text="ID: ")
        self.label_username.configure(text="Username: ")
        self.label_email.configure(text="Email: ")
        self.label_phone.configure(text="Phone: ")
        self.label_role.configure(text="Role: ")

    def invalid_for_role_change(self):
        if not self.selected_user_id:
            messagebox.showwarning("No Selection", "Select a user.")
            return True
        if self.selected_role == "Manager":
            messagebox.showerror("Restricted", "Cannot change Manager role.")
            return True
        if self.is_archived:
            messagebox.showerror("Archived", "Cannot change role of archived user.")
            return True
        return False

    def send_email_notification(self, to_email, subject, body):
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        sender_email = "ruxinthean@gmail.com"
        sender_password = "vznn pcdo pnol oiqf"  # Use Gmail app password

        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)
            print(f"Email sent to {to_email}")
            messagebox.showinfo("Email Sent", f"Email successfully sent to {to_email}.")

        except Exception as e:
            print(f"Failed to send email: {e}")
            messagebox.showerror("Email Failed", f"Failed to send email to {to_email}.\nError: {e}")


