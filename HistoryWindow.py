import base64
import io
import tkinter as tk
import datetime
from tkinter import messagebox
from tkcalendar import Calendar

from Viewers import *


class HistoryWindow:
    def __init__(self, master, app):
        self.history_manager = app.history_manager
        self.history = list(reversed(self.history_manager.get_history()))
        self.window = ctk.CTkToplevel(master)
        self.window.title("Історія")
        self.window.geometry("600x450")
        center_window(self.window, 600, 450)
        self.window.minsize(600, 450)
        self.app = app

        self.window.transient(master)
        self.window.grab_set()
        self.window.focus_set()

        self.filtered_entries = self.history
        self.selected_date = None

        date_frame = ctk.CTkFrame(self.window)
        date_frame.pack(pady=5)

        self.date_button = ctk.CTkButton(
            date_frame, text="Вибрати дату", command=self.open_date_picker
        )
        self.date_button.pack(side=tk.LEFT, padx=5)

        self.clear_date_button = ctk.CTkButton(
            date_frame, text="Скинути дату", command=self.clear_date_filter
        )
        self.clear_date_button.pack(side=tk.LEFT, padx=5)

        self.sort_order = "newest"
        self.sort_button = ctk.CTkButton(
            self.window,
            text="Сортувати: Від новіших до старіших",
            command=self.toggle_sort_order,
        )
        self.sort_button.pack(pady=5)

        self.listbox = tk.Listbox(self.window, width=50)
        self.listbox.pack(pady=10)
        self.populate_listbox(self.filtered_entries)

        view_image_button = ctk.CTkButton(
            self.window, text="Переглянути Зображення", command=self.view_image
        )
        view_image_button.pack(pady=5)

        view_text_button = ctk.CTkButton(
            self.window, text="Переглянути Текст", command=self.view_text
        )
        view_text_button.pack(pady=5)

        open_program_button = ctk.CTkButton(
            self.window, text="Відкрити в програмі", command=self.open_in_program
        )
        open_program_button.pack(pady=5)

        clear_history_button = ctk.CTkButton(
            self.window, text="Очистити історію", command=self.clear_history
        )
        clear_history_button.pack(pady=5)

        self.update_sort()

    def open_date_picker(self):
        calendar_window = ctk.CTkToplevel(self.window)
        calendar_window.title("Виберіть дату")
        calendar_window.geometry("300x300")
        calendar_window.transient(self.window)
        calendar_window.grab_set()
        calendar_window.focus_set()

        calendar = Calendar(
            calendar_window, selectmode="day", date_pattern="yyyy-mm-dd"
        )
        calendar.pack(pady=10)

        select_button = ctk.CTkButton(
            calendar_window,
            text="Вибрати",
            command=lambda: self.on_date_select(calendar, calendar_window),
        )
        select_button.pack(pady=5)

    def on_date_select(self, calendar, calendar_window):
        self.selected_date = calendar.selection_get()
        self.date_button.configure(
            text=f"Дата: {self.selected_date.strftime('%Y-%m-%d')}"
        )
        calendar_window.destroy()
        self.filter_entries()

    def filter_entries(self):
        if self.selected_date:
            self.filtered_entries = [
                entry
                for entry in self.history
                if datetime.datetime.strptime(
                    entry["timestamp"], "%Y-%m-%d %H:%M:%S"
                ).date()
                == self.selected_date
            ]
        else:
            self.filtered_entries = self.history
        self.update_sort()

    def clear_date_filter(self):
        self.selected_date = None
        self.date_button.configure(text="Вибрати дату")
        self.filter_entries()

    def toggle_sort_order(self):
        if self.sort_order == "newest":
            self.sort_order = "oldest"
            self.sort_button.configure(text="Сортувати: Від старіших до новіших")
        else:
            self.sort_order = "newest"
            self.sort_button.configure(text="Сортувати: Від новіших до старіших")
        self.update_sort()

    def update_sort(self):
        if self.sort_order == "newest":
            sorted_entries = sorted(
                self.filtered_entries, key=lambda e: e["timestamp"], reverse=True
            )
        else:
            sorted_entries = sorted(self.filtered_entries, key=lambda e: e["timestamp"])
        self.populate_listbox(sorted_entries)

    def populate_listbox(self, entries):
        self.listbox.delete(0, tk.END)
        for idx, entry in enumerate(entries):
            display_text = f"{entry['timestamp']}"
            self.listbox.insert(tk.END, display_text)

    def clear_history(self):
        confirm = messagebox.askyesno(
            "Підтвердження", "Ви дійсно хочете очистити історію?"
        )
        if confirm:
            self.history_manager.clear_history()
            self.history = []
            self.filtered_entries = []
            self.listbox.delete(0, tk.END)
            messagebox.showinfo("Успіх", "Історія очищена.")

    def view_image(self):
        selection = self.listbox.curselection()
        if selection:
            index = selection[0]
            entry = self.filtered_entries[index]
            img_data = base64.b64decode(entry["image_data"])
            image = Image.open(io.BytesIO(img_data))
            ImageViewer(self.window, image)

    def view_text(self):
        selection = self.listbox.curselection()
        if selection:
            index = selection[0]
            entry = self.filtered_entries[index]
            text = entry.get("recognized_text", "")
            if text:
                TextViewer(self.window, text)
            else:
                messagebox.showinfo(
                    "Інформація",
                    "Для цього зображення немає розпізнаного тексту, оскільки розпізнавання не було запущено.",
                )

    def open_in_program(self):
        selection = self.listbox.curselection()
        if selection:
            index = selection[0]
            entry = self.filtered_entries[index]
            text = entry.get("recognized_text", "")

            if not text:
                img_data = base64.b64decode(entry["image_data"])
                image = Image.open(io.BytesIO(img_data))
                self.app.set_image(image)
                self.window.destroy()
                return
            try:
                choice_window = ctk.CTkToplevel(self.window)
                choice_window.title("Вибір перегляду")
                choice_window.geometry("400x150")
                choice_window.transient(self.window)
                choice_window.grab_set()
                choice_window.focus_set()

                prompt_label = ctk.CTkLabel(
                    choice_window,
                    text="Бажаєте відкрити як розпізнаний текст чи як зображення?",
                )
                prompt_label.pack(pady=20)

                buttons_frame = ctk.CTkFrame(choice_window)
                buttons_frame.pack(pady=10)

                def open_as_image():
                    img_data = base64.b64decode(entry["image_data"])
                    image = Image.open(io.BytesIO(img_data))
                    self.app.set_image(image)
                    choice_window.destroy()
                    self.window.destroy()

                def open_as_text():
                    text = entry["recognized_text"]
                    self.app.set_text(text)
                    choice_window.destroy()
                    self.window.destroy()

                image_button = ctk.CTkButton(
                    buttons_frame, text="Зображення", command=open_as_image
                )
                image_button.grid(row=0, column=0, padx=10)

                text_button = ctk.CTkButton(
                    buttons_frame, text="Текст", command=open_as_text
                )
                text_button.grid(row=0, column=1, padx=10)

            except Exception as e:
                messagebox.showerror(
                    "Помилка", f"Не вдалося відкрити вікно перегляду:\n{e}"
                )

    def set_image(self, image):
        self.app.set_image(image)
        messagebox.showwarning("Увага", "Немає тексту для збереження.")
