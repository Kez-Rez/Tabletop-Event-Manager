"""Test zoom scaling for dialogs"""
import customtkinter as ctk

class TestApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Zoom Test")
        self.geometry("600x400")

        self.current_scale = 1.0

        # Controls
        frame = ctk.CTkFrame(self)
        frame.pack(pady=20, padx=20)

        ctk.CTkLabel(frame, text="Test Window and Dialog Scaling",
                    font=("Arial", 20, "bold")).pack(pady=10)

        # Zoom buttons
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(pady=10)

        ctk.CTkButton(btn_frame, text="Zoom In (150%)",
                     command=lambda: self.set_zoom(1.5)).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Normal (100%)",
                     command=lambda: self.set_zoom(1.0)).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Zoom Out (75%)",
                     command=lambda: self.set_zoom(0.75)).pack(side="left", padx=5)

        # Open dialog button
        ctk.CTkButton(frame, text="Open Test Dialog",
                     command=self.open_dialog,
                     width=200, height=40).pack(pady=20)

        self.zoom_label = ctk.CTkLabel(frame, text=f"Current Zoom: {int(self.current_scale * 100)}%",
                                       font=("Arial", 14))
        self.zoom_label.pack(pady=10)

    def set_zoom(self, scale):
        self.current_scale = scale
        ctk.set_widget_scaling(scale)
        ctk.set_window_scaling(scale)
        self.zoom_label.configure(text=f"Current Zoom: {int(scale * 100)}%")
        print(f"Set zoom to {scale}")

    def open_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Test Dialog")
        dialog.geometry("400x300")

        ctk.CTkLabel(dialog, text="This is a test dialog",
                    font=("Arial", 16, "bold")).pack(pady=20)
        ctk.CTkLabel(dialog, text=f"Should be scaled to {int(self.current_scale * 100)}%",
                    font=("Arial", 12)).pack(pady=10)
        ctk.CTkButton(dialog, text="Close", command=dialog.destroy).pack(pady=20)

if __name__ == "__main__":
    app = TestApp()
    app.mainloop()
