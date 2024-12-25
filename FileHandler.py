from tkinter import messagebox
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from textwrap import wrap


class FileHandler:
    def load_image(self, path):
        try:
            image = Image.open(path)
            return image
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдається відкрити зображення:\n{e}")
            return None

    def save_text(self, text, file_path):
        try:
            if file_path.endswith(".txt"):
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(text)
            elif file_path.endswith(".docx"):
                from docx import Document

                doc = Document()
                doc.add_paragraph(text)
                doc.save(file_path)
            elif file_path.endswith(".pdf"):
                pdf = canvas.Canvas(file_path, pagesize=A4)
                pdf.setFont("Times-Roman", 12)
                text_object = pdf.beginText(50, 800)

                for line in text.split("\n"):
                    for wrapped_line in wrap(line, 100):
                        text_object.textLine(wrapped_line)

                pdf.drawText(text_object)
                pdf.save()
            messagebox.showinfo("Успіх", "Файл успішно збережено.")
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося зберегти файл:\n{e}")
