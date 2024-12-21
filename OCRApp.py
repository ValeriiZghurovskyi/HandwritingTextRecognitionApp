from tkinter import filedialog

from FileHandler import *
from TextRecognizer import *
from ImageEditor import *
from HistoryWindow import *
from HistoryManager import *
from UI import *


class OCRApp:
    def __init__(self):
        self.text_recognizer = TextRecognizer()
        self.file_handler = FileHandler()
        self.history_manager = HistoryManager()
        self.use_gpu = torch.cuda.is_available()
        self.original_image = None
        self.edited_image = None
        self.recognized_text = ""
        self.ui = UI(self)

    def browse_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")]
        )
        if file_path:
            image = self.file_handler.load_image(file_path)
            if image:
                self.original_image = image
                self.edited_image = image.copy()
                self.history_manager.save_history(self.original_image, "")
                self.ui.display_image(self.edited_image)
                self.ui.update_path_entry(file_path)
                self.recognized_text = ""
                self.ui.hide_text_area()

    def recognize_text(self):
        if self.recognized_text:
            messagebox.showwarning(
                "Помилка",
                "Текст вже розпізнано. Будь ласка, завантажте зображення перед повторним розпізнаванням.",
            )
            return
        if not self.edited_image:
            messagebox.showwarning(
                "Увага", "Спочатку завантажте зображення для розпізнавання."
            )
            return
        try:
            self.ui.update_status_label("Розпізнавання триває...")
            temp_image_path = "temp_image.png"
            self.edited_image.save(temp_image_path)
            use_gpu = (
                torch.cuda.is_available() and self.ui.get_selected_device() == "GPU"
            )

            self.text_recognizer = TextRecognizer(use_gpu=use_gpu)
            self.recognized_text = self.text_recognizer.recognize_text(temp_image_path)

            os.remove(temp_image_path)

            if self.recognized_text.strip():
                self.ui.show_text_area(self.recognized_text)
            else:
                self.recognized_text = " "

            self.ui.show_text_area(self.recognized_text)

            self.ui.update_status_label("Розпізнавання завершено")
            self.history_manager.update_last_history_entry(self.recognized_text)
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося розпізнати текст:\n{e}")
            self.ui.update_status_label("")

    def save_as(self):
        if not self.recognized_text.strip():
            messagebox.showwarning("Увага", "Немає тексту для збереження.")
            return
        file_types = [
            ("Text Document", "*.txt"),
            ("Word Document", "*.docx"),
            ("PDF Document", "*.pdf"),
        ]
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt", filetypes=file_types
        )
        if file_path:
            self.file_handler.save_text(self.recognized_text, file_path)

    def open_history_entry(self, index):
        try:
            history = self.history_manager.get_history()
            entry = history[index]
            img_data = base64.b64decode(entry["image_data"])
            image = Image.open(io.BytesIO(img_data))
            self.original_image = image
            self.edited_image = image.copy()
            self.ui.display_image(self.edited_image)
            self.ui.update_path_entry("Завантажене з історії")
            self.recognized_text = entry["recognized_text"]
            self.ui.show_text_area(self.recognized_text)
        except Exception as e:
            messagebox.showerror(
                "Помилка", f"Не вдалося відкрити запис з історії:\n{e}"
            )

    def set_image(self, image):
        self.original_image = image
        self.edited_image = self.original_image.copy()
        self.recognized_text = ""
        self.ui.display_image(self.edited_image)
        self.ui.update_path_entry("Завантажене з історії")
        self.ui.hide_text_area()
        self.ui.update_status_label("")

    def set_text(self, text):
        self.recognized_text = text
        self.ui.show_text_area(self.recognized_text)
        self.ui.update_status_label("")

    def run(self):
        self.ui.root.mainloop()
