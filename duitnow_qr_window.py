import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk
import os


class DuitNowQRWindow(ctk.CTkToplevel):
    def __init__(self, master, amount_due, on_submit_callback):
        super().__init__(master)
        self.title("DuitNow QR Payment")
        self.geometry("400x400")
        self.amount_due = amount_due
        self.on_submit_callback = on_submit_callback
        self.configure(fg_color="white")
        self.resizable(False, False)

        # --- Modal + Always on Top + Center ---
        self.attributes("-topmost", True)
        self.grab_set()
        self.update_idletasks()
        self.center_window(master)

        # --- Title Label ---
        ctk.CTkLabel(
            self,
            text="Scan to Pay (DuitNow QR)",
            font=("Arial", 20, "bold"),
            text_color="#0C5481"
        ).pack(pady=15)

        # --- QR Code Image ---
        qr_path = os.path.join("images", "duitnow_qr.png")
        print("QR Path:", qr_path)  # Debugging path print

        if os.path.exists(qr_path):
            image = Image.open(qr_path).resize((220, 220), Image.LANCZOS)
            self.qr_image = ImageTk.PhotoImage(image)
            qr_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
            qr_frame.pack(pady=10)
            ctk.CTkLabel(qr_frame, image=self.qr_image, text="").pack()
        else:
            ctk.CTkLabel(self, text="QR Code not found", text_color="red").pack(pady=10)

        # --- Amount Display ---
        ctk.CTkLabel(
            self,
            text=f"Amount to Pay: RM {self.amount_due:.2f}",
            font=("Arial", 16, "bold"),
            text_color="green"
        ).pack(pady=20)

        # --- Done Button ---
        self.done_btn = ctk.CTkButton(
            self,
            text="✓ Payment Done",
            command=self.submit_payment,
            fg_color="#0C5481",
            hover_color="#2874ed",
            text_color="white"
        )
        self.done_btn.pack(pady=10)

    def center_window(self, master):
        """Centers this window over the parent window."""
        self.update_idletasks()
        parent_x = master.winfo_rootx()
        parent_y = master.winfo_rooty()
        parent_w = master.winfo_width()
        parent_h = master.winfo_height()

        window_w = self.winfo_width()
        window_h = self.winfo_height()

        pos_x = parent_x + (parent_w // 2) - (window_w // 2)
        pos_y = parent_y + (parent_h // 2) - (window_h // 2)

        self.geometry(f"+{pos_x}+{pos_y}")

    def submit_payment(self):
        self.destroy()  # Close the window immediately

        # Schedule the message and callback AFTER destruction
        self.after(100, self.after_destroy_callback)

    def after_destroy_callback(self):
        try:
            messagebox.showinfo("Payment Success", f"RM {self.amount_due:.2f} paid via DuitNow QR.")
            if self.on_submit_callback:
                self.on_submit_callback({})
        except Exception as e:
            print("Error in callback:", e)


# OPTIONAL: Test the window independently
if __name__ == "__main__":
    def dummy_callback(data):
        print("Payment callback received:", data)

    root = ctk.CTk()
    root.withdraw()  # Hide main window
    DuitNowQRWindow(root, amount_due=25.00, on_submit_callback=dummy_callback)
    root.mainloop()