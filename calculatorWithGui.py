import tkinter as tk
import math

def on_click(button_text):
    if button_text == "=":
        try:
            expression = entry.get()
            result = str(eval(expression, {"__builtins__": None}, math.__dict__))
            entry.delete(0, tk.END)
            entry.insert(tk.END, result)
        except Exception:
            entry.delete(0, tk.END)
            entry.insert(tk.END, "Error")
    elif button_text == "C":  # Clear all
        entry.delete(0, tk.END)
    elif button_text == "←":  # Backspace
        current = entry.get()
        entry.delete(0, tk.END)
        entry.insert(tk.END, current[:-1])  # remove last char
    else:
        entry.insert(tk.END, button_text)

# Main window
root = tk.Tk()
root.title("Scientific Calculator")
root.geometry("420x520")

# Entry field
entry = tk.Entry(root, font=("Arial", 20), bd=5, relief="solid", justify="right")
entry.pack(fill="both", ipadx=8, ipady=8, padx=10, pady=10)

# Button layout
buttons = [
    ["7", "8", "9", "/", "sqrt"],
    ["4", "5", "6", "*", "log"],
    ["1", "2", "3", "-", "sin"],
    ["0", ".", "=", "+", "cos"],
    ["(", ")", "**", "tan", "pi"],
    ["C", "←", "e"]
]

# Frame for buttons
frame = tk.Frame(root)
frame.pack()

for row in buttons:
    row_frame = tk.Frame(frame)
    row_frame.pack(expand=True, fill="both")
    for btn in row:
        button = tk.Button(
            row_frame, text=btn, font=("Arial", 16), height=2, width=6,
            command=lambda b=btn: on_click(b)
        )
        button.pack(side="left", expand=True, fill="both")

root.mainloop()
