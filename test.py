#!/usr/bin/python3
# -*- coding: utf-8 -*-

try:
    import tkinter as tk # Python 3 tkinter modules
except ImportError:
    import Tkinter as tk # Python 2 tkinter modules

from PIL import Image, ImageTk 
#from PIL import Image, ImageTk, ImageGrab  # For Windows & OSx
import pyscreenshot as ImageGrab # For Linux

class App(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent=parent

        file = "card files/catphie.png"
        self.img = Image.open(file)
        #self.img.show() #Check to proof image can be read in and displayed correctly.
        self.photo = ImageTk.PhotoImage(self.img)
        print('size of self.img =', self.img.size)
        centerx= self.img.size[0]//2
        centery= self.img.size[1]//2
        print ('center of self.img = ', centerx, centery)

        self.cv = tk.Canvas(self)
        self.cv.create_image(centerx, centery, image=self.photo)
        self.cv.create_rectangle(centerx*0.5,centery*0.5,centerx*1.5,centery*1.5,
                                 outline='blue')
        self.cv.grid(row=0, column=0, columnspan=3, sticky='nsew') 

        self.snappic=tk.Button(self, text='SNAP', command=self._snapCanvas)
        self.snappic.grid(row=1, column=0, sticky='nsew')

        self.savepic=tk.Button(self, text='SAVE', command=self._save)
        self.savepic.grid(row=1, column=1, sticky='nsew')

        self.directsavepic=tk.Button(self, text='Grab_to_File', command=self._grabtofile)
        self.directsavepic.grid(row=1, column=2, sticky='nsew')

        self.snapsave=tk.Button(self, text='SNAP & SAVE', command=self._snapsaveCanvas)
        self.snapsave.grid(row=2, column=0, columnspan=2, sticky='nsew')

    def _snapCanvas(self):
        print('\n def _snapCanvas(self):')
        canvas = self._canvas() # Get Window Coordinates of Canvas
        self.grabcanvas = ImageGrab.grab(bbox=canvas)
        self.grabcanvas.show()

    def _save(self):
        self.grabcanvas.save("out.jpg")
        print('Screenshoot of tkinter.Canvas saved in "out.jpg"')

    def _grabtofile(self):
        '''Remark: The intension was to directly save a screenshoot of the canvas in
                   "out_grabtofile.png".
                   Issue 1: Only a full screenshot was save.
                   Issue 2: Saved image format defaults to .png. Other format gave errors. 
                   Issue 3: "ImageGrab.grab_to_file" only able to return full screenshoot
                            and not just the canvas. '''
        print('\n def _grabtofile(self):')
        canvas = self._canvas()  # Get Window Coordinates of Canvas
        print('canvas = ', canvas)
        ImageGrab.grab_to_file("out_grabtofile.png", ImageGrab.grab(bbox=canvas))
        print('Screenshoot of tkinter.Canvas directly saved in "out_grabtofile.png"')

    def _snapsaveCanvas(self):
        print('\n def _snapsaveCanvas(self):')
        canvas = self._canvas()  # Get Window Coordinates of Canvas
        self.grabcanvas = ImageGrab.grab(bbox=canvas).save("out_snapsave.jpg")
        print('Screencshot tkinter canvas and saved as "out_snapsave.jpg w/o displaying screenshoot."')

    def _canvas(self):
        print('  def _canvas(self):')
        print('self.cv.winfo_rootx() = ', self.cv.winfo_rootx())
        print('self.cv.winfo_rooty() = ', self.cv.winfo_rooty())
        print('self.cv.winfo_x() =', self.cv.winfo_x())
        print('self.cv.winfo_y() =', self.cv.winfo_y())
        print('self.cv.winfo_width() =', self.cv.winfo_width())
        print('self.cv.winfo_height() =', self.cv.winfo_height())
        x=self.cv.winfo_rootx()+self.cv.winfo_x()
        y=self.cv.winfo_rooty()+self.cv.winfo_y()
        x1=x+self.cv.winfo_width()
        y1=y+self.cv.winfo_height()
        box=(x,y,x1,y1)
        print('box = ', box)
        return box


if __name__ == '__main__':
    root = tk.Tk()
    root.title('App'), root.geometry('300x300')
    app = App(root)
    app.grid(row=0, column=0, sticky='nsew')

    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    app.rowconfigure(0, weight=10)
    app.rowconfigure(1, weight=1)
    app.columnconfigure(0, weight=1)
    app.columnconfigure(1, weight=1)
    app.columnconfigure(2, weight=1)

    app.mainloop()