"""
Quiz App (Open Trivia DB)
Requires: requests
Install: pip install requests
Run: python quiz_app.py
"""

import tkinter as tk
from tkinter import ttk, messagebox
import requests
import html
import random

API_BASE = "https://opentdb.com"

class QuizApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Quiz App — Open Trivia DB")
        self.geometry("700x480")
        self.resizable(False, False)

        self.questions = []  # list of dicts from API
        self.current_index = 0
        self.score = 0
        self.user_answer = tk.StringVar()

        self._build_ui()
        self._load_categories()

    # ---------- UI ----------
    def _build_ui(self):
        # Top: settings frame
        settings = ttk.LabelFrame(self, text="Settings")
        settings.pack(fill="x", padx=12, pady=(12, 6))

        ttk.Label(settings, text="Questions:").grid(row=0, column=0, padx=6, pady=6, sticky="w")
        self.num_spin = ttk.Spinbox(settings, from_=1, to=50, width=6)
        self.num_spin.set(10)
        self.num_spin.grid(row=0, column=1, padx=6, pady=6, sticky="w")

        ttk.Label(settings, text="Difficulty:").grid(row=0, column=2, padx=6, pady=6, sticky="w")
        self.diff_combo = ttk.Combobox(settings, values=["Any", "easy", "medium", "hard"], width=10, state="readonly")
        self.diff_combo.set("Any")
        self.diff_combo.grid(row=0, column=3, padx=6, pady=6, sticky="w")

        ttk.Label(settings, text="Type:").grid(row=0, column=4, padx=6, pady=6, sticky="w")
        self.type_combo = ttk.Combobox(settings, values=["Any", "multiple", "boolean"], width=10, state="readonly")
        self.type_combo.set("Any")
        self.type_combo.grid(row=0, column=5, padx=6, pady=6, sticky="w")

        ttk.Label(settings, text="Category:").grid(row=1, column=0, padx=6, pady=6, sticky="w")
        self.cat_combo = ttk.Combobox(settings, values=["Loading..."], width=30, state="readonly")
        self.cat_combo.set("Any")
        self.cat_combo.grid(row=1, column=1, columnspan=3, padx=6, pady=6, sticky="w")

        fetch_btn = ttk.Button(settings, text="Fetch Questions", command=self.fetch_questions)
        fetch_btn.grid(row=1, column=5, padx=6, pady=6, sticky="e")

        # Middle: question display
        qframe = ttk.Frame(self)
        qframe.pack(fill="both", expand=True, padx=12, pady=(6,12))

        # Question label
        self.question_label = tk.Label(qframe, text="Press 'Fetch Questions' to start", wraplength=640, justify="left",
                                       font=("Segoe UI", 12), anchor="w")
        self.question_label.pack(pady=(8, 12), anchor="w")

        # Options (radio buttons)
        self.option_vars = []
        self.radio_buttons = []
        for i in range(4):
            var = tk.StringVar(value="")
            rb = ttk.Radiobutton(qframe, text="", variable=self.user_answer, value=str(i))
            rb.pack(fill="x", anchor="w", padx=8, pady=4)
            self.radio_buttons.append(rb)
            self.option_vars.append(var)

        # For boolean type there are only 2 options; we will hide unused radio buttons automatically.

        # Feedback / navigation
        nav = ttk.Frame(self)
        nav.pack(fill="x", padx=12, pady=(0,12))

        self.feedback_label = ttk.Label(nav, text="", anchor="w")
        self.feedback_label.pack(side="left", padx=6)

        self.next_btn = ttk.Button(nav, text="Next", state="disabled", command=self.next_question)
        self.next_btn.pack(side="right", padx=6)

        self.submit_btn = ttk.Button(nav, text="Submit Answer", state="disabled", command=self.submit_answer)
        self.submit_btn.pack(side="right", padx=6)

        self.progress_label = ttk.Label(nav, text="0 / 0")
        self.progress_label.pack(side="right", padx=12)

    # ---------- API interactions ----------
    def _load_categories(self):
        """Fetch trivia categories from API and populate category combobox."""
        try:
            r = requests.get(API_BASE + "/api_category.php", timeout=8)
            r.raise_for_status()
            data = r.json()
            cats = data.get("trivia_categories", [])
            # make values list with Any first
            values = ["Any"]
            self.cat_map = {"Any": None}
            for c in cats:
                name = c.get("name")
                cid = c.get("id")
                if name and cid:
                    values.append(name)
                    self.cat_map[name] = cid
            self.cat_combo["values"] = values
            self.cat_combo.set("Any")
        except Exception:
            # fallback to just Any
            self.cat_combo["values"] = ["Any"]
            self.cat_combo.set("Any")
            self.cat_map = {"Any": None}

    def fetch_questions(self):
        """Call Open Trivia DB to fetch questions based on settings."""
        # Clear old state
        self.questions = []
        self.current_index = 0
        self.score = 0
        self.user_answer.set("")
        self.feedback_label.config(text="")
        self.next_btn.config(state="disabled")
        self.submit_btn.config(state="disabled")
        self.question_label.config(text="Fetching questions...")

        amount = int(self.num_spin.get())
        params = {"amount": amount}
        # category
        cat_name = self.cat_combo.get()
        cat_id = self.cat_map.get(cat_name)
        if cat_id:
            params["category"] = cat_id
        # difficulty
        diff = self.diff_combo.get()
        if diff != "Any":
            params["difficulty"] = diff
        # type
        typ = self.type_combo.get()
        if typ != "Any":
            params["type"] = typ

        try:
            r = requests.get(API_BASE + "/api.php", params=params, timeout=10)
            r.raise_for_status()
            payload = r.json()
        except Exception as e:
            messagebox.showerror("Network error", f"Failed to fetch questions:\n{e}")
            self.question_label.config(text="Failed to fetch questions.")
            return

        code = payload.get("response_code")
        if code != 0:
            # 1 = no results, 2 = invalid parameter, etc.
            messagebox.showerror("API error", f"No questions available for the selected filters (response_code={code}). Try adjusting settings.")
            self.question_label.config(text="No questions available.")
            return

        raw = payload.get("results", [])
        if not raw:
            messagebox.showerror("No questions", "No questions returned by API.")
            self.question_label.config(text="No questions returned.")
            return

        # Prepare questions: decode HTML entities, shuffle answers
        self.questions = []
        for item in raw:
            q = html.unescape(item.get("question", ""))
            correct = html.unescape(item.get("correct_answer", ""))
            incorrect = [html.unescape(x) for x in item.get("incorrect_answers", [])]
            choices = incorrect + [correct]
            random.shuffle(choices)
            # store index of correct answer as string index (0..n-1)
            correct_index = choices.index(correct)
            self.questions.append({
                "question": q,
                "choices": choices,
                "correct_index": correct_index,
                "type": item.get("type", "multiple")
            })

        # start quiz
        self.current_index = 0
        self.score = 0
        self._show_question()

    # ---------- Question flow ----------
    def _show_question(self):
        if self.current_index >= len(self.questions):
            self._show_result()
            return

        qobj = self.questions[self.current_index]
        self.user_answer.set("")  # clear selection
        self.feedback_label.config(text="")
        self.next_btn.config(state="disabled")
        self.submit_btn.config(state="normal")

        q_text = f"Q{self.current_index + 1}. {qobj['question']}"
        self.question_label.config(text=q_text)

        choices = qobj["choices"]
        # show choices in radio buttons; hide unused ones
        for i, rb in enumerate(self.radio_buttons):
            if i < len(choices):
                rb.config(text=choices[i], value=str(i))
                rb.pack_configure(fill="x", anchor="w", padx=8, pady=4)
                rb.state(["!disabled"])
            else:
                rb.pack_forget()

        self.progress_label.config(text=f"{self.current_index + 1} / {len(self.questions)}")

    def submit_answer(self):
        selected = self.user_answer.get()
        if selected == "":
            messagebox.showinfo("Choose an answer", "Please select an option before submitting.")
            return
        qobj = self.questions[self.current_index]
        try:
            sel_idx = int(selected)
        except ValueError:
            sel_idx = None

        correct_idx = qobj["correct_index"]

        # Disable submit, enable next
        self.submit_btn.config(state="disabled")
        self.next_btn.config(state="normal")

        # Disable choices so user can't change
        for rb in self.radio_buttons:
            rb.state(["disabled"])

        if sel_idx == correct_idx:
            self.score += 1
            self.feedback_label.config(text="Correct ✅", foreground="green")
        else:
            correct_text = qobj["choices"][correct_idx]
            self.feedback_label.config(text=f"Wrong ❌ — Correct: {correct_text}", foreground="red")

    def next_question(self):
        self.current_index += 1
        self._show_question()

    def _show_result(self):
        total = len(self.questions)
        msg = f"You scored {self.score} out of {total}."
        # Show simple dialog with option to play again
        if messagebox.askyesno("Quiz Finished", msg + "\n\nPlay again?"):
            self.fetch_questions()
        else:
            self.question_label.config(text="Quiz finished. Press 'Fetch Questions' to start again.")
            # reset UI
            self.progress_label.config(text=f"{total} / {total}")
            self.feedback_label.config(text=f"Final score: {self.score}/{total}")
            self.submit_btn.config(state="disabled")
            self.next_btn.config(state="disabled")

if __name__ == "__main__":
    app = QuizApp()
    app.mainloop()
