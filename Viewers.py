import customtkinter as ctk

from customtkinter import CTkImage
from PIL import Image

from CropWindow import center_window


class ImageViewer:
    def __init__(self, master, image):
        self.window = ctk.CTkToplevel(master)
        self.window.title("Перегляд Зображення")
        self.window.geometry("500x500")
        center_window(self.window, 500, 500)
        self.window.minsize(500, 500)

        self.window.transient(master)
        self.window.grab_set()
        self.window.focus_set()

        self.label = ctk.CTkLabel(self.window, text="")
        self.label.pack(fill="both", expand=True)

        self.image = image
        self.window.bind("<Configure>", self.on_window_resize)
        self.update_image()

    def on_window_resize(self, event):
        self.update_image()

    def update_image(self):
        window_width = self.window.winfo_width()
        window_height = self.window.winfo_height()
        if window_width <= 1 or window_height <= 1:
            return

        image_ratio = self.image.width / self.image.height
        window_ratio = window_width / window_height

        if image_ratio > window_ratio:
            new_width = window_width
            new_height = int(window_width / image_ratio)
        else:
            new_height = window_height
            new_width = int(window_height * image_ratio)

        resized_image = self.image.resize((new_width, new_height), Image.LANCZOS)
        self.imgtk = CTkImage(resized_image, size=(new_width, new_height))
        self.label.configure(image=self.imgtk)
        self.label.image = self.imgtk


class TextViewer:
    def __init__(self, master, text):
        self.window = ctk.CTkToplevel(master)
        self.window.title("Перегляд Тексту")
        self.window.geometry("500x500")
        center_window(self.window, 500, 500)
        self.window.minsize(500, 500)

        self.window.transient(master)
        self.window.grab_set()
        self.window.focus_set()

        text_area = ctk.CTkTextbox(self.window)
        text_area.pack(fill="both", expand=True)
        text_area.insert("end", text)
        text_area.configure(state="disabled")
