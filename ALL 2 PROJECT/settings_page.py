import customtkinter as ctk

def load_settings_content(parent):
    label = ctk.CTkLabel(parent, text="Settings Page", font=("Arial", 24))
    label.pack(pady=20)

    def change_mode(choice):
        parent.winfo_toplevel().change_theme_mode(choice)

    mode_label = ctk.CTkLabel(parent, text="Select Theme Mode:", font=("Arial", 16))
    mode_label.pack(pady=10)

    mode_option = ctk.CTkOptionMenu(parent, values=["Light", "Dark", "System"], command=change_mode)
    mode_option.set("System")
    mode_option.pack(pady=10)
