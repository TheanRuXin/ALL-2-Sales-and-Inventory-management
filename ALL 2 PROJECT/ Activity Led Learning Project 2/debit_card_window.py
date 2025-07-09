import customtkinter as ctk
from tkinter import messagebox


class DebitCardWindow(ctk.CTkToplevel):
    def __init__(self, master, amount_due, on_submit_callback):
        super().__init__(master)
        self.title("Debit Card Payment")
        self.geometry("400x420")
        self.amount_due = amount_due
        self.on_submit_callback = on_submit_callback
        self.configure(fg_color="white")
        self.resizable(False, False)

        ctk.CTkLabel(self, text="Debit Card Payment", font=("Arial", 20, "bold"), text_color="#0C5481").pack(pady=15)

        self.name_entry = ctk.CTkEntry(self, placeholder_text="Card Holder Name", width=300)
        self.name_entry.pack(pady=10)

        self.card_entry = ctk.CTkEntry(self, placeholder_text="Card Number (16 digits)", width=300)
        self.card_entry.pack(pady=10)

        # Frame for expiry and CVV side by side
        expiry_cvv_frame = ctk.CTkFrame(self, fg_color="transparent")
        expiry_cvv_frame.pack(pady=10)

        self.expiry_entry = ctk.CTkEntry(expiry_cvv_frame, placeholder_text="Expiry (MM/YY)", width=140)
        self.expiry_entry.pack(side="left", padx=(0, 10))

        self.cvv_entry = ctk.CTkEntry(expiry_cvv_frame, placeholder_text="CVV", width=140, show="*")
        self.cvv_entry.pack(side="left")

        self.amount_label = ctk.CTkLabel(self, text=f"Amount to Pay: RM {self.amount_due:.2f}",
                                         font=("Arial", 16, "bold"), text_color="green")
        self.amount_label.pack(pady=15)

        self.submit_btn = ctk.CTkButton(self, text="Pay Now", command=self.submit_payment,
                                        fg_color="#0C5481", hover_color="#2874ed", text_color="white")
        self.submit_btn.pack(pady=10)

    def submit_payment(self):
        name = self.name_entry.get().strip()
        card = self.card_entry.get().strip()
        expiry = self.expiry_entry.get().strip()
        cvv = self.cvv_entry.get().strip()

        if not (name and card and expiry and cvv):
            messagebox.showerror("Missing Info", "Please fill in all fields.")
            return

        if not (card.isdigit() and len(card) == 16):
            messagebox.showerror("Card Error", "Card number must be 16 digits.")
            return

        if not (cvv.isdigit() and len(cvv) == 3):
            messagebox.showerror("CVV Error", "CVV must be 3 digits.")
            return

        card_info = {
            "name": name,
            "card_number": card,
            "expiry": expiry,
            "cvv": cvv
        }

        self.on_submit_callback(card_info)
        messagebox.showinfo("Payment Success", f"RM {self.amount_due:.2f} paid with Debit Card.")
        self.destroy()
