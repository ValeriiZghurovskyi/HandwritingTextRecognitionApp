import tkinter as tk
import customtkinter as ctk

from tkinter import messagebox
from PIL import Image, ImageTk


def center_window(window, width, height):
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")


class CropWindow:
    def __init__(self, master, editor):
        self.editor = editor
        self.window = ctk.CTkToplevel(master)
        self.window.transient(master)
        self.window.grab_set()
        self.window.focus_set()
        try:
            master.attributes("-disabled", True)
        except:
            pass
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        self.window.title("Обрізка зображення")
        self.window.geometry("500x800")
        center_window(self.window, 500, 800)
        self.window.minsize(500, 800)

        self.window.lift()
        self.window.focus_force()

        self.canvas = tk.Canvas(self.window, width=500, height=500)
        self.canvas.pack(fill="both", expand=True)

        self.canvas_width = 500
        self.canvas_height = 500

        resized_image = self.resize_image_proportionally(
            self.editor.edited_image, self.canvas_width, self.canvas_height
        )
        self.imgtk = ImageTk.PhotoImage(resized_image)
        self.canvas_image = self.canvas.create_image(
            0, 0, anchor="nw", image=self.imgtk
        )

        self.display_width, self.display_height = resized_image.size

        self.rect = None
        self.start_x = None
        self.start_y = None

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

        crop_button = ctk.CTkButton(self.window, text="Обрізати", command=self.crop)
        crop_button.pack(pady=5)

        self.canvas.bind("<Configure>", self.on_window_resize)

    def on_close(self):
        try:
            self.window.master.attributes("-disabled", False)
        except:
            pass
        self.window.destroy()

    def resize_image_proportionally(self, image, max_width, max_height):
        image_ratio = image.width / image.height
        max_ratio = max_width / max_height

        if image_ratio > max_ratio:
            new_width = max_width
            new_height = int(max_width / image_ratio)
        else:
            new_height = max_height
            new_width = int(max_height * image_ratio)

        resized = image.resize((new_width, new_height), Image.LANCZOS)
        self.display_width, self.display_height = resized.size
        return resized

    def on_button_press(self, event):
        self.start_x = event.x
        self.start_y = event.y

        if not self.rect:
            self.rect = self.canvas.create_rectangle(
                self.start_x, self.start_y, self.start_x, self.start_y, outline="red"
            )

    def on_move_press(self, event):
        cur_x = event.x
        cur_y = event.y

        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_button_release(self, event):
        if self.rect:
            self.start_x = None
            self.start_y = None

    def crop(self):
        if self.rect is None:
            messagebox.showwarning("Увага", "Будь ласка, виділіть область для обрізки.")
            return
        coords = self.canvas.coords(self.rect)
        if not coords or len(coords) != 4:
            messagebox.showwarning("Увага", "Будь ласка, виділіть область для обрізки.")
            return
        x0, y0, x1, y1 = coords
        if (x1 - x0 <= 0) or (y1 - y0 <= 0):
            messagebox.showwarning(
                "Увага",
                "Обрана некоректна область для обрізки. Будь ласка, спробуйте знову.",
            )
            return

        x0 = max(0, min(x0, self.display_width))
        y0 = max(0, min(y0, self.display_height))
        x1 = max(0, min(x1, self.display_width))
        y1 = max(0, min(y1, self.display_height))

        x_ratio = self.editor.edited_image.width / self.display_width
        y_ratio = self.editor.edited_image.height / self.display_height

        left = int(min(x0, x1) * x_ratio)
        upper = int(min(y0, y1) * y_ratio)
        right = int(max(x0, x1) * x_ratio)
        lower = int(max(y0, y1) * y_ratio)

        left = max(0, min(left, self.editor.edited_image.width))
        upper = max(0, min(upper, self.editor.edited_image.height))
        right = max(0, min(right, self.editor.edited_image.width))
        lower = max(0, min(lower, self.editor.edited_image.height))

        new_cropped_image = self.editor.edited_image.crop((left, upper, right, lower))
        if new_cropped_image.width == 0 or new_cropped_image.height == 0:
            messagebox.showwarning(
                "Увага",
                "Обрана некоректна область для обрізки. Будь ласка, спробуйте знову.",
            )
            return

        self.editor.edited_image = new_cropped_image
        self.editor.base_image = self.editor.edited_image.copy()
        self.editor.rotation_scale.set(0)
        self.editor.update_image()
        try:
            self.window.master.attributes("-disabled", False)
        except:
            pass
        self.window.destroy()

    def on_window_resize(self, event):
        self.update_image()

    def update_image(self):
        self.canvas.delete("all")

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        resized_image = self.resize_image_proportionally(
            self.editor.edited_image, canvas_width, canvas_height
        )
        self.imgtk = ImageTk.PhotoImage(resized_image)
        self.canvas.create_image(0, 0, anchor="nw", image=self.imgtk)
        self.canvas.image = self.imgtk
