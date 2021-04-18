import cv2
import torch
import tkinter
import numpy as np
from transformer_net import TransformerNet
from PIL import ImageTk, Image
import scipy.stats as st

r = 15

RectID = None
img = None
lambd = None

def create_circular_mask(r):
    w, h = 2 * r, 2 * r
    radius = r
    center = (int(w/2), int(h/2))
    radius = min(center[0], center[1], w-center[0], h-center[1])

    Y, X = np.ogrid[:h, :w]
    dist_from_center = np.sqrt((X - center[0])**2 + (Y-center[1])**2)

    mask = dist_from_center <= radius
    return mask

def get_kernel(r, nsig=0.1):
    """Returns a 2D Gaussian kernel."""

    x = np.linspace(-nsig * r, nsig * r, 2 * r + 1)
    kern1d = np.diff(st.norm.cdf(x))
    kern2d = np.outer(kern1d, kern1d)
    m = create_circular_mask(r)
    return m * kern2d/kern2d.sum()

def update():
    global RectID
    global lambd
    global img_id
    global x
    global y
    global res_
    #print(lambd)
    res_ = Image.fromarray(np.round(res * lambd[:,:,np.newaxis] + img_orig * (1-lambd[:,:,np.newaxis])).clip(0, 255).astype("uint8"))

    res_ = ImageTk.PhotoImage(res_)
    my_canvas.delete(img_id)
    if RectID is not None:
        my_canvas.delete(RectID)
    img_id = my_canvas.create_image(0, 0, image=res_, anchor=tkinter.NW)
    RectID = my_canvas.create_oval(x - r, y - r, x + r, y + r)
    my_canvas.update_idletasks()


def OnLeftMouseDown(event):
    global lambd,x, y,r
    x, y = event.x, event.y
    lambd[y - r: y + r, x - r: x + r] -= kernel
    lambd = lambd.clip(0, 1)
    update()
def OnLeftMouseMove(event):
    global x, y
    x, y = event.x, event.y
    update()


def round64(x):
    return (int(x / 64) + 1) * 64

def save_image(filename, data, h, w):
    img = data.detach().clamp(0, 255).numpy()[0]
    img = img.transpose(1, 2, 0).astype("uint8")
    img = Image.fromarray(img[:h,:w,:])
    img.save(filename)


def get_res(img):
    h, w, c = img.shape
    h_, w_ = round64(h), round64(w)
    img_ = np.zeros((h_, w_, c))
    img_[:h,:w,:] = img
    img = img_[:,:,::-1].copy().swapaxes(1, 2).swapaxes(0, 1)
    img = torch.Tensor(img)[None,:,:,:]
    print(img.shape)
    weights_name = 'saved_models/mosaic.pth'
    net = TransformerNet()
    weights = torch.load(weights_name)
    net.load_state_dict(weights)
    net.eval()

    with torch.no_grad():
        res = net(img)

    save_image('res.jpg', res, h, w)
    return res[:,:,:h,:w]

root = tkinter.Tk()
img_orig = cv2.imread('./images/grape.jpg')
h, w, _ = img_orig.shape
lambd = np.ones((h, w))

kernel = get_kernel(r, 0.000000000000001) * 200
print(kernel)
res = get_res(img_orig.copy()).detach().clamp(0, 255).numpy()[0]
img_orig = img_orig[:,:,::-1].copy()

res = res.transpose(1, 2, 0)

res_ = Image.fromarray(res.astype("uint8"))

res_ = ImageTk.PhotoImage(res_)

my_canvas = tkinter.Canvas(root, bg="white", height=300, width=300)

my_canvas.pack(expand=tkinter.YES, fill=tkinter.BOTH)

img_id = my_canvas.create_image(0, 0, image=res_, anchor=tkinter.NW)

my_canvas.config(cursor="plus")

my_canvas.bind("<Motion>", OnLeftMouseMove)
my_canvas.bind("<B1-Motion>", OnLeftMouseDown)
root.mainloop()
