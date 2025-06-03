import customtkinter as ctk
from tkinter import messagebox

# Sample inventory data
inventory_data = [
    {"name": "Jeans", "quantity": 20, "price": 79.90},
    {"name": "Shirt", "quantity": 35, "price": 45.50},
    {"name": "Shoes", "quantity": 15, "price": 120.00},
    {"name": "Hat", "quantity": 50, "price": 25.00},
]


def load_inventory_content(parent):
    ctk.CTkLabel(parent, text="Inventory Items", font=("Arial", 24, "bold")).pack(pady=20)

    inventory_frame = ctk.CTkFrame(parent)
    inventory_frame.pack(padx=20, pady=10, fill="both", expand=True)

    headers = ["Item Name", "Quantity", "Price (RM)"]
    for idx, header in enumerate(headers):
        label = ctk.CTkLabel(inventory_frame, text=header, font=("Arial", 14, "bold"))
        label.grid(row=0, column=idx, padx=10, pady=10, sticky="w")

    for row_idx, item in enumerate(inventory_data, start=1):
        ctk.CTkLabel(inventory_frame, text=item["name"], font=("Arial", 12)).grid(row=row_idx, column=0, padx=10,
                                                                                  pady=5, sticky="w")
        ctk.CTkLabel(inventory_frame, text=str(item["quantity"]), font=("Arial", 12)).grid(row=row_idx, column=1,
                                                                                           padx=10, pady=5)
        ctk.CTkLabel(inventory_frame, text=f"RM {item['price']:.2f}", font=("Arial", 12)).grid(row=row_idx, column=2,
                                                                                               padx=10, pady=5)


# Optional: Remove the standalone window code unless needed for testing
if __name__ == "__main__":
    root = ctk.CTk()
    root.geometry("600x400")
    load_inventory_content(root)
    root.mainloop()
