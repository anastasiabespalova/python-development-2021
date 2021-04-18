import cv2
import torch
import tkinter
import numpy as np
from transformer_net import TransformerNet
from PIL import ImageTk, Image
import scipy.stats as st


RectID = None
img = None
lambd = None

def get_kernel(r, nsig=3):
    """Returns a 2D Gaussian kernel."""

    x = np.linspace(-nsig, nsig, 2 * r + 1)
    kern1d = np.diff(st.norm.cdf(x))
    kern2d = np.outer(kern1d, kern1d)
    return kern2d/kern2d.sum()

def OnLeftMouseMove(event):
    global RectID
    x, y = event.x, event.y
    res_ = Image.fromarray(round(res * lambd[:,:,np.newaxis] + img_orig * (1-lambd[:,:,np.newaxis])).clip(0, 255).astype("uint8"))

    res_ = ImageTk.PhotoImage(res_)

    my_canvas.create_image(0, 0, image=res_, anchor=tkinter.NW)
    #my_canvas.update_idletasks()
    if RectID:
        my_canvas.delete(RectID)
    RectID = my_canvas.create_oval(x - 20, y - 20, x + 20, y + 20)


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


res = get_res(img_orig.copy()).detach().clamp(0, 255).numpy()[0]
img_orig = img_orig[:,:,::-1].copy().swapaxes(1, 2).swapaxes(0, 1)

res = res.transpose(1, 2, 0)

res_ = Image.fromarray(res.astype("uint8"))

res_ = ImageTk.PhotoImage(res_)

my_canvas = tkinter.Canvas(root, bg="white", height=300, width=300)

my_canvas.pack(expand=tkinter.YES, fill=tkinter.BOTH)

my_canvas.create_image(0, 0, image=res_, anchor=tkinter.NW)

my_canvas.config(cursor="plus")

my_canvas.bind("<Motion>", OnLeftMouseMove)

root.mainloop()
