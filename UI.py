import customtkinter as ctk
import torch
import tkinter as tk

from PIL import Image, ImageTk
from tkinter import messagebox

from HistoryWindow import *
from ImageEditor import *


class UI:
    def __init__(self, controller):
        self.controller = controller
        self.root = ctk.CTk()
        self.root.title("Розпізнавання рукописного тексту")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)
        self.setup_ui()

    def setup_ui(self):
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True)

        left_frame = ctk.CTkFrame(main_frame)
        left_frame.pack(side="left", fill="both", expand=True)

        right_frame = ctk.CTkFrame(main_frame, width=200)
        right_frame.pack(side="right", fill="y")

        self.canvas = ctk.CTkCanvas(left_frame, bg="white")
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self.on_canvas_resize)

        self.text_area = ctk.CTkTextbox(left_frame)
        self.text_area.pack(fill="both", expand=True, padx=10, pady=10)
        self.text_area.pack_forget()

        path_label = ctk.CTkLabel(right_frame, text="Шлях до зображення:")
        path_label.pack(pady=(20, 5))

        self.path_entry = ctk.CTkEntry(right_frame, width=160, state="readonly")
        self.path_entry.pack(pady=5)

        self.browse_button = ctk.CTkButton(
            right_frame, text="Відкрити файл", command=self.controller.browse_file
        )
        self.browse_button.pack(pady=5)

        self.edit_button = ctk.CTkButton(
            right_frame, text="Редагувати зображення", command=self.edit_image
        )
        self.edit_button.pack(pady=5)

        self.recognize_button = ctk.CTkButton(
            right_frame, text="Розпізнати текст", command=self.controller.recognize_text
        )
        self.recognize_button.pack(pady=5)

        self.save_button = ctk.CTkButton(
            right_frame, text="Зберегти як", command=self.controller.save_as
        )
        self.save_button.pack(pady=5)

        self.history_button = ctk.CTkButton(
            right_frame, text="Історія", command=self.open_history
        )
        self.history_button.pack(pady=5, side="bottom")

        self.status_label = ctk.CTkLabel(right_frame, text="")
        self.status_label.pack(pady=5)

        if torch.cuda.is_available():
            device_label = ctk.CTkLabel(right_frame, text="Обрати пристрій:")
            device_label.pack(pady=(30, 2))

            self.device_var = tk.StringVar(value="GPU")
            device_optionmenu = ctk.CTkOptionMenu(
                right_frame,
                variable=self.device_var,
                values=["GPU", "CPU"],
                width=100,
                height=25,
                corner_radius=5,
            )
            device_optionmenu.pack(pady=(2, 5))

    def display_image(self, image):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        if canvas_width <= 1 or canvas_height <= 1:
            return

        image_ratio = image.width / image.height
        canvas_ratio = canvas_width / canvas_height

        if image_ratio > canvas_ratio:
            new_width = canvas_width
            new_height = int(canvas_width / image_ratio)
        else:
            new_height = canvas_height
            new_width = int(canvas_height * image_ratio)

        resized_image = image.resize((new_width, new_height), Image.LANCZOS)
        self.imgtk = ImageTk.PhotoImage(resized_image)
        self.canvas.delete("all")
        self.canvas.create_image(
            canvas_width / 2, canvas_height / 2, image=self.imgtk, anchor="center"
        )

    def on_canvas_resize(self, event):
        if self.controller.edited_image:
            self.display_image(self.controller.edited_image)

    def update_path_entry(self, path):
        self.path_entry.configure(state="normal")
        self.path_entry.delete(0, "end")
        self.path_entry.insert(0, path)
        self.path_entry.configure(state="readonly")

    def hide_text_area(self):
        self.text_area.pack_forget()
        self.canvas.pack(fill="both", expand=True)

    def show_text_area(self, text):
        self.text_area.pack(fill="both", expand=True, padx=10, pady=10)
        self.canvas.pack_forget()
        self.text_area.delete("1.0", "end")
        self.text_area.insert("end", text)

    def update_status_label(self, text):
        self.status_label.configure(text=text)

    def get_selected_device(self):
        return self.device_var.get()

    def open_history(self):
        HistoryWindow(self.root, self.controller)

    def edit_image(self):
        if not self.controller.edited_image or not self.canvas.winfo_ismapped():
            messagebox.showwarning("Увага", "Немає зображення для редагування.")
            return
        editor = ImageEditor(self.root, self.controller)
        self.root.wait_window(editor.window)
