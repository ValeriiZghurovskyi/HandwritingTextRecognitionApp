import customtkinter as ctk

from OCRApp import OCRApp

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

if __name__ == "__main__":
    app = OCRApp()
    app.run()
