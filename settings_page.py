import customtkinter as ctk

def load_settings_content(parent):
    # Clear previous content
    for widget in parent.winfo_children():
        widget.destroy()

    parent.configure(fg_color="white")

    # Main Frame
    settings_frame = ctk.CTkFrame(parent, fg_color="white")
    settings_frame.place(relx=0.5, rely=0.5, anchor="center")

    # Title
    ctk.CTkLabel(
        settings_frame,
        text="Settings",
        font=("Arial", 28, "bold"),
        text_color="#0C5481"
    ).pack(pady=(20, 10))

    # Appearance Mode Label
    ctk.CTkLabel(
        settings_frame,
        text="Appearance Mode",
        font=("Arial", 20)
    ).pack(pady=(10, 5))

    # Option Menu
    appearance_mode_menu = ctk.CTkOptionMenu(
        settings_frame,
        values=["Light", "Dark", "System"],
        command=change_appearance_mode,
        width=180,
        height=35
    )
    appearance_mode_menu.pack(pady=10)
    appearance_mode_menu.set(ctk.get_appearance_mode().capitalize())

def change_appearance_mode(mode):
    ctk.set_appearance_mode(mode)