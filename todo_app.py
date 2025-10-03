import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog
import json
from pathlib import Path
import datetime
import os

# ---------- Config ----------
APP_NAME = "Simple To-Do"
AUTOSAVE = True
AUTOSAVE_INTERVAL_MS = 30_000  # autosave every 30s
DATA_FILENAME = "todo.json"

# Use a platform-appropriate user data directory (home/.local/share or %APPDATA% on Windows).
def get_data_path():
    if os.name == "nt":
        base = Path(os.getenv("APPDATA", Path.home()))
    else:
        base = Path(os.getenv("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    app_dir = base / "simple_todo_app"
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir / DATA_FILENAME

DATA_PATH = get_data_path()


# ---------- Data model ----------
# Each task is a dict: {"id": int, "text": str, "done": bool, "created": iso, "modified": iso}
class TodoModel:
    def __init__(self):
        self.tasks = []
        self._next_id = 1

    def add(self, text):
        now = datetime.datetime.utcnow().isoformat()
        task = {"id": self._next_id, "text": text, "done": False, "created": now, "modified": now}
        self._next_id += 1
        self.tasks.append(task)
        return task

    def delete(self, task_id):
        before = len(self.tasks)
        self.tasks = [t for t in self.tasks if t["id"] != task_id]
        return len(self.tasks) < before

    def update_text(self, task_id, new_text):
        for t in self.tasks:
            if t["id"] == task_id:
                t["text"] = new_text
                t["modified"] = datetime.datetime.utcnow().isoformat()
                return True
        return False

    def toggle_done(self, task_id):
        for t in self.tasks:
            if t["id"] == task_id:
                t["done"] = not t["done"]
                t["modified"] = datetime.datetime.utcnow().isoformat()
                return t["done"]
        return None

    def clear_all(self):
        self.tasks = []

    def to_dict(self):
        return {"tasks": self.tasks, "next_id": self._next_id}

    def from_dict(self, data):
        self.tasks = data.get("tasks", [])
        self._next_id = data.get("next_id", max((t["id"] for t in self.tasks), default=0) + 1)


# ---------- Persistence ----------
def save_model(model, path=DATA_PATH):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(model.to_dict(), f, indent=2, ensure_ascii=False)
        return True, None
    except Exception as e:
        return False, str(e)

def load_model(model, path=DATA_PATH):
    if not path.exists():
        return False, "No file"
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        model.from_dict(data)
        return True, None
    except Exception as e:
        return False, str(e)


# ---------- GUI ----------
class TodoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("520x600")
        self.resizable(True, True)

        self.model = TodoModel()
        # load at startup if available
        ok, err = load_model(self.model)
        if not ok and err != "No file":
            messagebox.showwarning("Load failed", f"Could not load saved tasks:\n{err}")

        self.create_widgets()
        self.render_list()

        if AUTOSAVE:
            self.after(AUTOSAVE_INTERVAL_MS, self._autosave_job)

    def create_widgets(self):
        top_frame = tk.Frame(self)
        top_frame.pack(fill="x", padx=8, pady=8)

        self.entry = tk.Entry(top_frame, font=("Segoe UI", 14))
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.entry.bind("<Return>", lambda e: self.add_task())

        add_btn = tk.Button(top_frame, text="Add", width=10, command=self.add_task)
        add_btn.pack(side="right")

        # Middle: list with scrollbar
        mid_frame = tk.Frame(self)
        mid_frame.pack(fill="both", expand=True, padx=8, pady=4)

        self.canvas = tk.Canvas(mid_frame)
        self.canvas.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(mid_frame, orient="vertical", command=self.canvas.yview)
        scrollbar.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.list_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.list_frame, anchor="nw")
        self.list_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Bottom: actions
        bottom_frame = tk.Frame(self)
        bottom_frame.pack(fill="x", padx=8, pady=8)

        save_btn = tk.Button(bottom_frame, text="Save", command=self.save)
        save_btn.pack(side="left", padx=4)

        load_btn = tk.Button(bottom_frame, text="Load", command=self.load)
        load_btn.pack(side="left", padx=4)

        export_btn = tk.Button(bottom_frame, text="Export...", command=self.export_json)
        export_btn.pack(side="left", padx=4)

        clear_btn = tk.Button(bottom_frame, text="Clear All", command=self.clear_all)
        clear_btn.pack(side="right", padx=4)

        # status bar
        self.status = tk.StringVar()
        self.status.set("Ready")
        status_label = tk.Label(self, textvariable=self.status, anchor="w")
        status_label.pack(fill="x", padx=6, pady=(0,6))

    def render_list(self):
        # wipe
        for child in self.list_frame.winfo_children():
            child.destroy()

        if not self.model.tasks:
            lbl = tk.Label(self.list_frame, text="No tasks — add one!", font=("Segoe UI", 12), pady=10)
            lbl.pack()
            return

        for task in sorted(self.model.tasks, key=lambda x: (-int(x["done"]), x["id"])):
            frame = tk.Frame(self.list_frame, bd=1, relief="solid", padx=6, pady=6)
            frame.pack(fill="x", pady=4, padx=4)

            var = tk.BooleanVar(value=task["done"])
            chk = tk.Checkbutton(frame, variable=var, command=lambda tid=task["id"], v=var: self.toggle_done(tid, v))
            chk.pack(side="left")

            text = tk.Label(frame, text=task["text"], anchor="w", justify="left", font=("Segoe UI", 12))
            text.pack(side="left", fill="x", expand=True, padx=6)

            # style done items
            if task["done"]:
                text.config(fg="gray", font=("Segoe UI", 12, "overstrike"))
            else:
                text.config(fg="black")

            edit_btn = tk.Button(frame, text="Edit", width=8, command=lambda tid=task["id"]: self.edit_task(tid))
            edit_btn.pack(side="right", padx=(6,0))

            del_btn = tk.Button(frame, text="Delete", width=8, command=lambda tid=task["id"]: self.delete_task(tid))
            del_btn.pack(side="right")

    # ---------- Actions ----------
    def add_task(self):
        text = self.entry.get().strip()
        if not text:
            messagebox.showinfo("Input required", "Please type a task before adding.")
            return
        self.model.add(text)
        self.entry.delete(0, tk.END)
        self.render_list()
        self.status.set("Task added")
        if not AUTOSAVE:
            self.save()

    def delete_task(self, task_id):
        confirm = messagebox.askyesno("Delete", "Delete this task?")
        if not confirm:
            return
        self.model.delete(task_id)
        self.render_list()
        self.status.set("Task deleted")
        if not AUTOSAVE:
            self.save()

    def edit_task(self, task_id):
        task = next((t for t in self.model.tasks if t["id"] == task_id), None)
        if not task:
            return
        new_text = simpledialog.askstring("Edit Task", "Update task text:", initialvalue=task["text"], parent=self)
        if new_text is None:
            return
        new_text = new_text.strip()
        if not new_text:
            messagebox.showwarning("Empty", "Task text cannot be empty.")
            return
        self.model.update_text(task_id, new_text)
        self.render_list()
        self.status.set("Task updated")
        if not AUTOSAVE:
            self.save()

    def toggle_done(self, task_id, var):
        self.model.toggle_done(task_id)
        self.render_list()
        self.status.set("Toggled status")
        if not AUTOSAVE:
            self.save()

    def clear_all(self):
        confirm = messagebox.askyesno("Clear all", "Remove ALL tasks? This cannot be undone.")
        if not confirm:
            return
        self.model.clear_all()
        self.render_list()
        self.status.set("All tasks cleared")
        if not AUTOSAVE:
            self.save()

    def save(self):
        ok, err = save_model(self.model)
        if ok:
            self.status.set(f"Saved to {DATA_PATH}")
        else:
            messagebox.showerror("Save failed", f"Could not save tasks:\n{err}")
            self.status.set("Save failed")

    def load(self):
        ok, err = load_model(self.model)
        if ok:
            self.render_list()
            self.status.set(f"Loaded from {DATA_PATH}")
        else:
            messagebox.showerror("Load failed", f"Could not load tasks:\n{err}")
            self.status.set("Load failed")

    def export_json(self):
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files","*.json")], title="Export tasks to JSON")
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.model.to_dict(), f, indent=2, ensure_ascii=False)
            self.status.set(f"Exported to {path}")
            messagebox.showinfo("Exported", f"Tasks exported to:\n{path}")
        except Exception as e:
            messagebox.showerror("Export failed", str(e))
            self.status.set("Export failed")

    def _autosave_job(self):
        ok, err = save_model(self.model)
        if ok:
            self.status.set(f"Autosaved at {datetime.datetime.now().strftime('%H:%M:%S')}")
        else:
            self.status.set("Autosave failed")
        self.after(AUTOSAVE_INTERVAL_MS, self._autosave_job)


if __name__ == "__main__":
    app = TodoApp()
    app.mainloop()
