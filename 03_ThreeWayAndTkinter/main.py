from tkinter import *
from tkinter import messagebox
import random
import sys

blank = [3, 3]

def get_pos(btn):
    info = btn.grid_info()
    i, j = info["row"] - 1, info["column"]
    return i, j

def is_won():
    for btn in buttons:
        i, j = get_pos(btn)
        n = int(btn['text'])
        if i != n // 4 or j != n % 4:
            return False
    return True

def win_actions(event):
    if is_won():
        messagebox.showinfo("Information", "You won!")
        restart()

def get_clicker(n):
    def clicked(event):
        btn = buttons[n]
        i, j = get_pos(btn)
        diff1 = abs(i - blank[0])
        diff2 = abs(j - blank[1])
        if (diff1 + diff2) == 1:
            buttons[n].grid(column=blank[1], row=blank[0] + 1, sticky="NSEW")
            blank[0] = i
            blank[1] = j
    return clicked

def clicked_new():
    restart()

def clicked_exit():
    sys.exit()

def restart():
    if blank[0] != 3 or blank[1] != 3:
        for btn in buttons:
            i, j = get_pos(btn)
            if i == 3 and j == 3:
                btn.grid(column=blank[1], row=blank[0] + 1)
                break
        blank[0], blank[1] = 3, 3
    numbers = list(range(15))
    random.shuffle(numbers)
    for i, btn in enumerate(buttons):
        btn['text'] = str(numbers[i])

window = Tk()
window.geometry("500x500")

for i in range(1, 5):
    Grid.rowconfigure(window, i, weight=1)
for i in range(0, 4):
    Grid.columnconfigure(window, i, weight=1)

window.title("15 puzzle by A.P.Bespalova")
btn_new = Button(window, text="New", command=clicked_new)
btn_exit = Button(window, text="Exit", command=clicked_exit)
buttons = [Button(window, text=str(i)) for i in range(15)]

for i, btn in enumerate(buttons):
    btn.grid(column=i % 4, row=i // 4 + 1, sticky="NSEW")
    btn.bind('<Button>', get_clicker(i))
    btn.bind('<ButtonRelease>', win_actions)
btn_new.grid(column=1, row=0)
btn_exit.grid(column=2, row=0)
restart()
window.mainloop()