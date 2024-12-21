import torch
import cv2
import easyocr

from tkinter import messagebox


class TextRecognizer:
    def __init__(self, use_gpu=None):
        if use_gpu is None:
            self.use_gpu = torch.cuda.is_available()
        else:
            self.use_gpu = use_gpu
        self.reader = easyocr.Reader(["en"], gpu=self.use_gpu)

    def recognize_text(self, image_path):
        try:
            image = cv2.imread(image_path)
            results = self.reader.readtext(image, detail=0, paragraph=True)
            formatted_text = "\n\n".join(results)

            return formatted_text
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося розпізнати текст:\n{e}")
            return ""
