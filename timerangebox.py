import tkinter as tk
from tkinter import simpledialog, ttk, messagebox

class TimeRangeDialog(simpledialog.Dialog):
    def body(self, master):
        self.title("Select Start and End Time")

        def add_time_row(label, row, prefix):
            ttk.Label(master, text=label).grid(row=row, column=0, columnspan=6, pady=(10 if row else 0, 5))
            ttk.Label(master, text="HH:").grid(row=row+1, column=0)
            setattr(self, f"{prefix}_hour", tk.Spinbox(master, from_=0, to=23, width=5, format="%02.0f"))
            getattr(self, f"{prefix}_hour").grid(row=row+1, column=1)

            ttk.Label(master, text="MM:").grid(row=row+1, column=2)
            setattr(self, f"{prefix}_minute", tk.Spinbox(master, from_=0, to=59, width=5, format="%02.0f"))
            getattr(self, f"{prefix}_minute").grid(row=row+1, column=3)

            ttk.Label(master, text="SS:").grid(row=row+1, column=4)
            setattr(self, f"{prefix}_second", tk.Spinbox(master, from_=0, to=59, width=5, format="%02.0f"))
            getattr(self, f"{prefix}_second").grid(row=row+1, column=5)

        add_time_row("Start Time", 0, "start")
        add_time_row("End Time", 2, "end")
        return self.start_hour  # Initial focus

    def validate(self):
        try:
            self.start_seconds = self._to_seconds(
                self.start_hour.get(), self.start_minute.get(), self.start_second.get()
            )
            self.end_seconds = self._to_seconds(
                self.end_hour.get(), self.end_minute.get(), self.end_second.get()
            )
            if self.end_seconds <= self.start_seconds:
                raise ValueError("End time must be after start time")
            return True
        except Exception as e:
            messagebox.showerror("Invalid input", str(e))
            return False

    def _to_seconds(self, h, m, s):
        return int(h) * 3600 + int(m) * 60 + int(s)

    def apply(self):
        self.result = (self.start_seconds, self.end_seconds)

# Example usage
def ask_time_range():
    root = tk.Tk()
    root.withdraw()
    dialog = TimeRangeDialog(root)
    return dialog.result

# Example: call and print result
if __name__ == "__main__":
    time_range = ask_time_range()
    if time_range:
        print(f"⏱️ Start: {time_range[0]}s | End: {time_range[1]}s")
