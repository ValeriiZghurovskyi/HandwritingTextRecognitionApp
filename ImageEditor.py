from PIL import ImageEnhance

from CropWindow import *


class ImageEditor:
    def __init__(self, master, app):
        self.app = app
        self.original_image = app.edited_image.copy()
        self.base_image = app.edited_image.copy()
        self.edited_image = app.edited_image.copy()
        self.window = ctk.CTkToplevel(master)
        self.window.transient(master)
        self.window.grab_set()
        self.window.focus_set()
        try:
            master.attributes("-disabled", True)
        except:
            pass
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        self.window.title("Редагування зображення")
        self.window.geometry("600x900")
        center_window(self.window, 600, 900)
        self.window.minsize(600, 900)

        self.create_widgets()
        self.update_image()

    def on_close(self):
        try:
            self.window.master.attributes("-disabled", False)
        except:
            pass
        self.window.destroy()

    def create_widgets(self):
        self.canvas = ctk.CTkCanvas(self.window, width=500, height=500)
        self.canvas.pack(pady=10, fill="both", expand=True)
        self.canvas.bind("<Configure>", self.on_canvas_resize)

        sliders_frame = ctk.CTkFrame(self.window)
        sliders_frame.pack(pady=10, padx=10, fill="x", expand=True)

        rotation_label = ctk.CTkLabel(sliders_frame, text="Кут повороту")
        rotation_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.rotation_scale = ctk.CTkSlider(
            sliders_frame, from_=-180, to=180, command=self.adjust_image
        )
        self.rotation_scale.set(0)
        self.rotation_scale.grid(
            row=0, column=1, columnspan=3, padx=5, pady=5, sticky="we"
        )

        sep = ctk.CTkLabel(sliders_frame, text="")
        sep.grid(row=1, column=0, columnspan=4, pady=10)

        contrast_label = ctk.CTkLabel(sliders_frame, text="Контрастність")
        contrast_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.contrast_scale = ctk.CTkSlider(
            sliders_frame, from_=0.5, to=2.0, command=self.adjust_image
        )
        self.contrast_scale.set(1.0)
        self.contrast_scale.grid(row=2, column=1, padx=5, pady=5, sticky="we")

        brightness_label = ctk.CTkLabel(sliders_frame, text="Яскравість")
        brightness_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.brightness_scale = ctk.CTkSlider(
            sliders_frame, from_=0.5, to=2.0, command=self.adjust_image
        )
        self.brightness_scale.set(1.0)
        self.brightness_scale.grid(row=3, column=1, padx=5, pady=5, sticky="we")

        color_label = ctk.CTkLabel(sliders_frame, text="Колір")
        color_label.grid(row=2, column=2, padx=5, pady=5, sticky="w")
        self.color_scale = ctk.CTkSlider(
            sliders_frame, from_=0.0, to=2.0, command=self.adjust_image
        )
        self.color_scale.set(1.0)
        self.color_scale.grid(row=2, column=3, padx=5, pady=5, sticky="we")

        sharpness_label = ctk.CTkLabel(sliders_frame, text="Різкість")
        sharpness_label.grid(row=3, column=2, padx=5, pady=5, sticky="w")
        self.sharpness_scale = ctk.CTkSlider(
            sliders_frame, from_=0.0, to=2.0, command=self.adjust_image
        )
        self.sharpness_scale.set(1.0)
        self.sharpness_scale.grid(row=3, column=3, padx=5, pady=5, sticky="we")

        sliders_frame.columnconfigure(1, weight=1)
        sliders_frame.columnconfigure(3, weight=1)

        buttons_frame = ctk.CTkFrame(self.window)
        buttons_frame.pack(pady=10)

        crop_button = ctk.CTkButton(
            buttons_frame, text="Обрізати", command=self.crop_image
        )
        crop_button.grid(row=0, column=0, padx=10)

        reset_button = ctk.CTkButton(
            buttons_frame, text="Скинути", command=self.reset_image
        )
        reset_button.grid(row=0, column=1, padx=10)

        save_button = ctk.CTkButton(
            buttons_frame, text="Застосувати", command=self.apply_changes
        )
        save_button.grid(row=0, column=2, padx=10)

    def on_canvas_resize(self, event):
        self.update_image()

    def update_image(self):
        self.canvas.delete("all")

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        image_ratio = self.edited_image.width / self.edited_image.height
        canvas_ratio = canvas_width / canvas_height

        if image_ratio > canvas_ratio:
            new_width = canvas_width
            new_height = int(canvas_width / image_ratio)
        else:
            new_height = canvas_height
            new_width = int(canvas_height * image_ratio)

        new_width = max(1, new_width)
        new_height = max(1, new_height)

        resized_image = self.edited_image.resize((new_width, new_height), Image.LANCZOS)
        self.imgtk = ImageTk.PhotoImage(resized_image)
        self.canvas.create_image(
            canvas_width / 2, canvas_height / 2, image=self.imgtk, anchor="center"
        )

    def adjust_image(self, _=None):
        image = self.base_image.copy()

        angle = self.rotation_scale.get()
        image = image.rotate(angle, expand=True, fillcolor="white")

        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(self.contrast_scale.get())

        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(self.brightness_scale.get())

        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(self.color_scale.get())

        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(self.sharpness_scale.get())

        self.edited_image = image
        self.update_image()

    def crop_image(self):
        crop_window = CropWindow(self.window, self)
        self.window.wait_window(crop_window.window)

    def reset_image(self):
        self.edited_image = self.original_image.copy()
        self.base_image = self.original_image.copy()
        self.rotation_scale.set(0)
        self.contrast_scale.set(1.0)
        self.brightness_scale.set(1.0)
        self.color_scale.set(1.0)
        self.sharpness_scale.set(1.0)
        self.update_image()

    def apply_changes(self):
        self.app.edited_image = self.edited_image.copy()
        self.app.ui.display_image(self.app.edited_image)
        try:
            self.window.master.attributes("-disabled", False)
        except:
            pass
        self.window.destroy()
