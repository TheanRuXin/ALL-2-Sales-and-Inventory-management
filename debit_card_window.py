import customtkinter as ctk
from tkinter import messagebox


class DebitCardWindow(ctk.CTkToplevel):
    def __init__(self, master, amount_due, on_submit_callback):
        super().__init__(master)
        self.title("Debit Card Payment")
        self.geometry("400x420")
        self.configure(fg_color="white")
        self.resizable(True, True)

        # --- Encapsulated properties ---
        self._amount_due = amount_due
        self._on_submit_callback = on_submit_callback
        self._card_info = {}

        # --- Modal behavior ---
        self.attributes("-topmost", True)
        self.grab_set()
        self.update_idletasks()
        self._center_window(master)

        # --- Initialize UI ---
        self._create_widgets()

    def _center_window(self, master):
        """Center the toplevel window over its master."""
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

    def _create_widgets(self):
        """Create and layout all widgets."""
        ctk.CTkLabel(self, text="Debit Card Payment", font=("Arial", 20, "bold"), text_color="#0C5481").pack(pady=15)

        self._name_entry = ctk.CTkEntry(self, placeholder_text="Card Holder Name", width=300)
        self._name_entry.pack(pady=10)

        self._card_entry = ctk.CTkEntry(self, placeholder_text="Card Number (16 digits)", width=300)
        self._card_entry.pack(pady=10)

        expiry_cvv_frame = ctk.CTkFrame(self, fg_color="transparent")
        expiry_cvv_frame.pack(pady=10)

        self._expiry_entry = ctk.CTkEntry(expiry_cvv_frame, placeholder_text="Expiry (MM/YY)", width=140)
        self._expiry_entry.pack(side="left", padx=(0, 10))

        self._cvv_entry = ctk.CTkEntry(expiry_cvv_frame, placeholder_text="CVV", width=140, show="*")
        self._cvv_entry.pack(side="left")

        ctk.CTkLabel(self, text=f"Amount to Pay: RM {self._amount_due:.2f}",
                     font=("Arial", 16, "bold"), text_color="green").pack(pady=15)

        ctk.CTkButton(self, text="Pay Now", command=self._submit_payment,
                      fg_color="#0C5481", hover_color="#2874ed", text_color="white").pack(pady=10)

    def _submit_payment(self):
        """Validate and process the payment."""
        name = self._name_entry.get().strip()
        card = self._card_entry.get().strip()
        expiry = self._expiry_entry.get().strip()
        cvv = self._cvv_entry.get().strip()

        if not (name and card and expiry and cvv):
            messagebox.showerror("Missing Info", "Please fill in all fields.")
            return

        if not (card.isdigit() and len(card) == 16):
            messagebox.showerror("Card Error", "Card number must be 16 digits.")
            return

        if not (cvv.isdigit() and len(cvv) == 3):
            messagebox.showerror("CVV Error", "CVV must be 3 digits.")
            return

        self._card_info = {
            "name": name,
            "card_number": card,
            "expiry": expiry,
            "cvv": cvv
        }

        self.destroy()
        self.after(100, self._after_destroy_callback)

    def _after_destroy_callback(self):
        """Handle actions after window is destroyed."""
        try:
            messagebox.showinfo("Payment Success", f"RM {self._amount_due:.2f} paid with Debit Card.")
            if self._on_submit_callback:
                self._on_submit_callback(self._card_info)
        except Exception as e:
            print("Callback error:", e)

    # Optional: controlled getter
    def get_card_info(self):
        """Return card info if needed externally."""
        return self._card_info