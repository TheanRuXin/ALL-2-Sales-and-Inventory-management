import customtkinter as ctk

# Placeholder functions for each feature
def feature_action(feature_name):
    print(f"Feature clicked: {feature_name}")

# ✅ Updated to accept the extra arguments
def load_home_content(parent, cashier_username=None, cart_items=None, total_price=0.0, on_cart_update=None):
    parent.configure(fg_color="white")

    canvas = ctk.CTkCanvas(parent, bg="white", highlightthickness=0)
    scrollbar = ctk.CTkScrollbar(parent, orientation="vertical", command=canvas.yview)
    scroll_frame = ctk.CTkFrame(canvas, fg_color="white")

    scroll_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    categories = {
        "In-store Management": [
            "Product catalogue",
            "Table layout for F&B merchants",
            "Save, hold, split & merge customer orders",
            "Staff PINs for individual tracking",
            "Manage multiple branches"
        ],
        "Payment Methods": [
            "Multiple secure payment methods",
            "Returns and refunds",
            "Store credit"
        ],
        "Customer Loyalty": [
            "Customer database",
            "Points and rewards",
            "Membership tiers"
        ],
        "Data Analysis and Reports": [
            "Daily sales reports",
            "Sales and inventory forecasting",
            "Top selling items",
            "Peak hours report",
            "Cash flow overview"
        ],
        "Customer Convenience": [
            "QR ordering",
            "Self-ordering kiosk",
            "Online store integration"
        ],
        "Inventory Management": [
            "Low stock alerts",
            "Inventory level tracking",
            "Stock transfers between branches",
            "Product variants and modifiers"
        ],
        "Employee Management": [
            "Employee performance tracking",
            "Shift management"
        ],
        "Support": [
            "Cloud backup",
            "Technical support"
        ]
    }

    button_style = {
        "fg_color": "#0C5481",
        "hover_color": "#2874ed",
        "text_color": "white",
        "font": ("Arial", 13, "bold"),
        "corner_radius": 6,
        "height": 35,
        "width": 300
    }

    for category, features in categories.items():
        header = ctk.CTkLabel(scroll_frame, text=category, font=("Arial", 18, "bold"), text_color="#0C5481")
        header.pack(anchor="w", padx=20, pady=(20, 5))

        for feat in features:
            btn = ctk.CTkButton(scroll_frame, text=feat, command=lambda f=feat: feature_action(f), **button_style)
            btn.pack(anchor="w", padx=40, pady=5)
