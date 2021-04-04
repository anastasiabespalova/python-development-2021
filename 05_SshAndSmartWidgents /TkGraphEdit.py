import tkinter as tk

class CanvasWindow:
    def __init__(self, master):
        self.master = master
        self.frame = tk.Frame(self.master)
        self.frame.pack()
        self.newWindow = tk.Toplevel(self.master)
        self.app = TextWindow(self.newWindow, self)
        canvas_width = 640
        canvas_height = 360
        self.canvas = tk.Canvas(self.frame, width=canvas_width, height=canvas_height)
        self.canvas.bind("<Button-1>", self.left_click)
        self.canvas.bind("<B1-Motion>", self.motion)
        self.canvas.bind("<ButtonRelease>", self.left_click_up)
        self.canvas.pack()
        self.objects = []
        self.color = '#000000'
        self.new_oval = True
        self.last_xy = (0, 0)
        self.text_infos = dict()
        self.counter = 0

    def get_oval_params(self, x0, y0, x1, y1):
        a = max(abs(x1 - x0), 1e-6) / 2
        b = max(abs(y1 - y0), 1e-6) / 2
        x_c = (x0 + x1) / 2
        y_c = (y0 + y1) / 2
        return a, b, x_c, y_c

    def check_in_oval(self, x, y, a, b, x_c, y_c):
        return (((x - x_c) / a) ** 2 + ((y - y_c) / b) ** 2) <= 1

    def left_click(self, event):
        x, y = event.x, event.y
        candidates = []
        for o in self.objects:
            if self.check_in_oval(x, y, *self.get_oval_params(*o[1:5])):
                candidates.append(o)
        if not candidates:
            self.new_oval = True
            id = self.canvas.create_oval(x, y, x, y, outline=self.color, fill="", width=2.0)
            self.objects.append([id, x, y, x, y, 2.0, self.color, ""])
        else:
            self.last_xy = (x, y)
            self.new_oval = False
            oval = max(candidates, key=lambda x: x[0])
            self.objects.remove(oval)
            self.objects.append(oval)

    def left_click_up(self, event):
        if self.new_oval:
            self.text_infos[self.objects[-1][0]] = [self.counter, *self.objects[-1]]
            self.counter += 1
        else:
            obj = self.objects[-1]
            info = self.text_infos[obj[0]]
            info[2], info[3], info[4], info[5] = obj[1:5]
            self.text_infos[obj[0]] = info
        self.update_text()

    def motion(self, event):
        x, y = event.x, event.y
        id, x0, y0, x1, y1, wd, color_frame, color_fill = self.objects.pop()
        self.canvas.delete(id)
        if self.new_oval:
            id = self.canvas.create_oval(x0, y0, x, y, outline=color_frame, fill=color_fill, width=wd)
            self.objects.append([id, x0, y0, x, y, wd, color_frame, color_fill])
        else:
            dw, dh = x - self.last_xy[0], y - self.last_xy[1]
            x0_, y0_, x1_, y1_ = x0 + dw, y0 + dh, x1 + dw, y1 + dh
            old = self.text_infos[id][0]
            del self.text_infos[id]
            id = self.canvas.create_oval(x0_, y0_, x1_, y1_, outline=color_frame, fill=color_fill, width=wd)
            self.objects.append([id, x0_, y0_, x1_, y1_, wd, color_frame, color_fill])
            self.text_infos[id] = [old, *self.objects[-1]]
            self.last_xy = (x, y)

    def update_text(self):
        self.app.text.delete(1.0, tk.END)
        ks = self.text_infos.keys()
        ks = sorted(ks, key=lambda x: self.text_infos[x][0])
        for id_ in ks:
            info = self.text_infos[id_]
            self.app.text.insert(tk.END, "{};{};{};{};{};{};{}.\n".format(*info[2:]))

    def update_by_text(self):
        for i, obj in enumerate(self.objects):
            self.canvas.delete(obj[0])
            info = self.text_infos[obj[0]]
            del self.text_infos[obj[0]]
            id = self.canvas.create_oval(info[2],
                                         info[3],
                                         info[4],
                                         info[5],
                                         outline=info[7],
                                         fill=info[8],
                                         width=info[6])
            info[1] = id
            self.objects[i] = info[1:]
            self.text_infos[id] = info
            print(self.objects, id)

class TextWindow:
    def __init__(self, master, canvas):
        self.canvas = canvas
        self.master = master
        self.frame = tk.Frame(self.master)
        self.text = tk.Text(self.frame)
        self.update = tk.Button(self.frame, text='Update', command=self.update)
        self.update.pack()
        self.text.pack()
        self.frame.pack()

    def check_single_line(self, line):
        elems = line.split(';')
        if len(elems) != 7:
            return False
        if line[-1] != '.':
            return False
        elems[-1] = elems[-1].rstrip('.')
        res = True
        res = res and elems[0].isnumeric()
        res = res and elems[1].isnumeric()
        res = res and elems[2].isnumeric()
        res = res and elems[3].isnumeric()
        try:
            float(elems[4])
        except:
            return False
        res = res and self.check_color(elems[5])
        res = res and self.check_color(elems[6])
        return res

    def check_color(self, s):
        if not s:
            return True
        if len(s) != 7:
            return False
        if s[:1] != '#':
            return False
        res = True
        for c in s[1:]:
            res = res and (c.isnumeric() or (c in 'abcdef'))
        return res

    def check_lines(self):
        lines = self.text.get(1.0, tk.END).split('\n')
        lines = [l for l in lines if l]
        to_mark = []
        for i, l in enumerate(lines):
            check = self.check_single_line(l)
            if not check:
                to_mark.append([i, len(l)])

        for tag in self.text.tag_names():
            self.text.tag_delete(tag)
        for i, end in to_mark:
            self.text.tag_add(str(i), "{}.0".format(i + 1), "{}.{}".format(i + 1, end))
            self.text.tag_config(str(i), background="red")
        if not to_mark:
            return True
        return False

    def update(self):
        objs = [self.canvas.text_infos[k] for k in self.canvas.text_infos.keys()]
        objs = sorted(objs, key=lambda x: x[0])
        if self.check_lines():
            lines = self.text.get(1.0, tk.END).split('\n')
            lines = [l.split(';') for l in lines if l]
            for i, l in enumerate(lines):
                info = objs[i]
                info[2:] = int(l[0]), int(l[1]), int(l[2]), int(l[3]), float(l[4]), l[5], l[6].rstrip('.')
                self.canvas.text_infos[info[1]] = info
            self.canvas.update_by_text()


def main():
    root = tk.Tk()
    CanvasWindow(root)
    root.mainloop()

if __name__ == '__main__':
    main()