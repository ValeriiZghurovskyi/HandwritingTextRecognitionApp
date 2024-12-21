import pickle
import io
import os
import base64
import datetime

from tkinter import messagebox


class HistoryManager:
    def save_history(self, image, recognized_text):
        try:
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            history = self.load_history()
            history.append(
                {
                    "timestamp": timestamp,
                    "image_data": img_str,
                    "recognized_text": recognized_text,
                }
            )
            with open("history.bin", "wb") as f:
                pickle.dump(history, f)
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося зберегти історію:\n{e}")

    def load_history(self):
        try:
            if not os.path.exists("history.bin"):
                return []
            with open("history.bin", "rb") as f:
                history = pickle.load(f)
            valid_history = []
            for entry in history:
                if "image_data" in entry and "recognized_text" in entry:
                    valid_history.append(entry)
            return valid_history
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося завантажити історію:\n{e}")
            return []

    def update_last_history_entry(self, recognized_text):
        try:
            history = self.load_history()
            if history:
                history[-1]["recognized_text"] = recognized_text
                with open("history.bin", "wb") as f:
                    pickle.dump(history, f)
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося оновити історію:\n{e}")

    def clear_history(self):
        try:
            with open("history.bin", "wb") as f:
                pickle.dump([], f)
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося очистити історію:\n{e}")

    def get_history(self):
        return self.load_history()
