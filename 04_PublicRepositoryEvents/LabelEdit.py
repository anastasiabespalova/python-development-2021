import tkinter as tk
import sys

class InputLabel(tk.Label):
    def __init__(self, root):
        super().__init__(root, text="", font=("Courier", 20), relief="groove",
                            borderwidth=1, width=9, anchor=tk.W)
        self.root = root
        self.cursor_pos = 0
        self.char_num = 0
        self.step = 12
        self.cursor = tk.Frame(self, height=30, width=1, borderwidth=4, bg='black')
        self.cursor.place(x=1, y=0)
        self.bind("<Button-1>", self.leftclick)
        self.bind("<Key>", self.input_char)
        self.place(x=0, y=0)
        self.root_width = 123
        self.bind("<BackSpace>", self.delete_char)
        self.bind('<Left>', self.left_key)
        self.bind('<Right>', self.right_key)
        #self.bind('<Home>', self.left_key)
        #self.bind('<End>', self.right_key)

    def leftclick(self, event):
        self.focus_set()
        self.config(borderwidth=2)
        self.cursor_pos = min(round(event.x / self.step) * self.step, len(self['text']) * self.step)
        self.char_num = min(self.cursor_pos // self.step, len(self['text']))
        self.cursor.place(x=self.cursor_pos, y=0)

    def input_char(self, event):
        self['text'] = self['text'][:self.char_num] + event.char + self['text'][self.char_num:]
        self.char_num += 1
        if len(self['text']) >= self['width']:
            self['width'] += 1
            self.root_width += (self.step - 1)
            self.root.geometry("{}x60".format(self.root_width))
        self.cursor_pos += self.step
        self.cursor.place(x=self.cursor_pos, y=0)

    def delete_char(self, event):
        self['text'] = self['text'][:max(self.char_num - 1, 0)] + self['text'][self.char_num:]
        if self.char_num > 0:
            self.char_num -= 1
        self.cursor_pos -= self.step
        self.cursor.place(x=self.cursor_pos, y=0)

    def left_key(self, event):
        if self.char_num > 0:
            self.char_num -= 1
        self.cursor_pos -= self.step
        self.cursor.place(x=self.cursor_pos, y=0)

    def right_key(self, event):
        if self.char_num < len(self['text']) - 1:
            self.char_num += 1
        self.cursor_pos += self.step
        self.cursor.place(x=self.cursor_pos, y=0)


if __name__ == '__main__':
    root = tk.Tk()
    root.maxsize(-1, 60)
    root.minsize(60, 60)
    root.title("Custom Enter by A.P.Bespalova")
    root.geometry("123x60")
    my_entry = InputLabel(root)
    button1 = tk.Button(root, text="Quit", command=lambda: sys.exit(), pady=5, width=10)
    button1.place(x=50, y=30)
    root.mainloop()
