import tkinter as tk

def on_click(button_text):
    if button_text == "=":
        try:
            expression = entry.get()
            result = str(eval(expression))  # evaluate the expression
            entry.delete(0, tk.END)
            entry.insert(tk.END, result)
        except Exception:
            entry.delete(0, tk.END)
            entry.insert(tk.END, "Error")
    elif button_text == "C":
        entry.delete(0, tk.END)
    else:
        entry.insert(tk.END, button_text)

# Main window
root = tk.Tk()
root.title("Calculator")
root.geometry("300x400")

# Entry field
entry = tk.Entry(root, font=("Arial", 20), bd=5, relief="solid", justify="right")
entry.pack(fill="both", ipadx=8, ipady=8, padx=10, pady=10)

# Button layout
buttons = [
    ["7", "8", "9", "/"],
    ["4", "5", "6", "*"],
    ["1", "2", "3", "-"],
    ["0", ".", "=", "+"],
    ["C"]
]

# Frame for buttons
frame = tk.Frame(root)
frame.pack()

for row in buttons:
    row_frame = tk.Frame(frame)
    row_frame.pack(expand=True, fill="both")
    for btn in row:
        button = tk.Button(
            row_frame, text=btn, font=("Arial", 18), height=2, width=5,
            command=lambda b=btn: on_click(b)
        )
        button.pack(side="left", expand=True, fill="both")

root.mainloop()
