from tkinter import *
from tkinter import filedialog
from PIL import ImageTk, Image
from pdf2image import convert_from_path
from PyPDF2 import PdfFileReader, PdfFileWriter


class PdfApp():
    def __init__(self, master):
        master.title("PDF Cropper")
        title_icon = PhotoImage(file="icons/picture.png")
        master.tk.call('wm', 'iconphoto', master._w, title_icon)
        
        # define
        self.window_width = 1500
        self.window_height = 800
        self.toolbar = Frame(master)
        self.ori_pdf_img = None
        self.pdf_img = None
        self.canvas = Canvas(master, height=self.window_height, width=self.window_width, bg="gray")
        self.canvas_img = None

        # pdf variables
        self.img_x = 0
        self.img_y = 0
        self.img_w = 0
        self.img_h = 0
        self.pdf2img_factor = 1
        
        # crop
        self.crop = False
        self.rect = None
        self.start_x = None
        self.start_y = None
        self.cur_x = None
        self.cur_y = None

        # mouse events
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        
        # button
        self.open_tk  = ImageTk.PhotoImage(Image.open("icons/folder.png").resize((30, 30)))
        self.crop_tk  = ImageTk.PhotoImage(Image.open("icons/crop.png").resize((30, 30)))
        self.button_open  = Button(self.toolbar, text="open",  image=self.open_tk,  command=self.open_pdf)
        self.button_crop  = Button(self.toolbar, text="crop",  image=self.crop_tk,  command=self.crop_pdf, state=DISABLED)

        # position
        self.canvas.pack(side=TOP)
        self.button_open.pack(side=LEFT, padx=10, pady=10)
        self.button_crop.pack(side=LEFT, padx=10, pady=10)
        self.toolbar.pack(side=TOP)


    """Utils"""    
    # update img variables
    def update_img_var(self):
        w, h = self.pdf_img.size
        self.img_x = self.window_width/2 - w/2
        self.img_y = self.window_height/2 - h/2
        self.img_w = w
        self.img_h = h

    # refresh canvas images
    def refresh_canvas(self):
        self.img_in_tk = ImageTk.PhotoImage(self.pdf_img)
        if not self.canvas_img: 
            self.canvas.delete(self.canvas_img)
        self.canvas_img = self.canvas.create_image(self.window_width/2, self.window_height/2, anchor=CENTER, image=self.img_in_tk)

    # make sure only 1 function is currently using
    def reset_flag(self):
        self.crop = False
        self.canvas.config(cursor="")


    """Interface"""
    # method for mouse function
    def on_button_press(self, event):
        # print("Crop pdf ==========")
        if self.rect:
            self.canvas.delete(self.rect)
            self.rect = None
        self.canvas.config(cursor="cross")
        print("Drag for desired crop box")
        self.crop = True
        self.button_crop["state"] = DISABLED

        # save mouse drag start position
        self.start_x = self.canvas.canvasx(event.x) - self.img_x
        self.start_y = self.canvas.canvasy(event.y) - self.img_y
        if self.start_x < 0: self.start_x = 0
        elif self.start_x > self.img_w: self.start_x = self.img_w
        if self.start_y < 0: self.start_y = 0   
        elif self.start_y > self.img_h: self.start_y = self.img_h
        
        # create rectangle if not yet exist
        print("Start at (%4d, %4d)" % (self.start_x, self.start_y))
        self.rect = self.canvas.create_rectangle(0, 0, 1, 1, width=5, outline='black')


    def on_move_press(self, event):
        self.cur_x = self.canvas.canvasx(event.x) - self.img_x
        self.cur_y = self.canvas.canvasy(event.y) - self.img_y
        if self.cur_x < 0: self.cur_x = 0
        elif self.cur_x > self.img_w: self.cur_x = self.img_w
        if self.cur_y < 0: self.cur_y = 0
        elif self.cur_y > self.img_h: self.cur_y = self.img_h

        print("\rEnd at   (%4d, %4d)" % (self.cur_x, self.cur_y), end="")
        self.canvas.coords(self.rect, self.start_x + self.img_x, self.start_y + self.img_y,\
            self.cur_x + self.img_x, self.cur_y + self.img_y)


    def on_button_release(self, event):
        if self.crop:
            print("\n")
            self.button_crop["state"] = NORMAL
            self.canvas.config(cursor="")
            crop = False

    
    """Button Functions"""
    # open and fit the input pdf to the window
    def open_pdf(self):
        # print("Open pdf ==========")
        in_fname = filedialog.askopenfilename(title="Select pdf")

        in_f = open(in_fname, "rb")
        self.pdf_page = PdfFileReader(in_f).getPage(0)
        self.pdf_width = self.pdf_page.cropBox.getUpperRight_x()
        self.pdf_height = self.pdf_page.cropBox.getUpperRight_y()
        print(f"Original pdf size: {self.pdf_width}x{self.pdf_height}")

        # convert pdf into image
        img_pages = convert_from_path(in_fname)
        w, h = img_pages[0].size
        print(f"Original pdf_img size: {w}x{h}")

        resize_flag = False
        if w > self.window_width:
            h = int(h * self.window_width / w)
            w = self.window_width
            resize_flag = True

        if h > self.window_height:
            w = int(w * self.window_height / h)
            h = self.window_height
            resize_flag = True

        if resize_flag:
            print(f"Resize pdf_img size: {w}x{h}")
            self.pdf2img_factor = self.pdf_width / w
            print(f"Pdf to img resize factor: {self.pdf2img_factor}")
            self.ori_pdf_img = self.pdf_img = img_pages[0].resize((w, h))
        else:
            self.ori_pdf_img = self.pdf_img = img_pages[0]

        self.update_img_var()
        self.refresh_canvas()
        self.button_crop["state"] = DISABLED

        print("PDF opened ==========\n")


    # method for crop
    def crop_pdf(self):
        self.reset_flag()
        self.pdf_img = self.pdf_img.crop((self.start_x, self.start_y, self.cur_x, self.cur_y))
            
        pdf_start_x = float(self.start_x) * float(self.pdf2img_factor)
        pdf_start_y = float(self.pdf_height) - self.start_y * float(self.pdf2img_factor)
        pdf_cur_x = float(self.cur_x) * float(self.pdf2img_factor)
        pdf_cur_y = float(self.pdf_height) - self.cur_y * float(self.pdf2img_factor)
        print(f"Convert back to pdf coordinates = ({pdf_start_x}, {pdf_start_y}), ({pdf_cur_x}, {pdf_cur_y})")

        if pdf_start_x < pdf_cur_x:
            self.pdf_page.cropBox.lowerLeft = (pdf_start_x, pdf_cur_y)
            self.pdf_page.cropBox.upperRight = (pdf_cur_x, pdf_start_y)
        else:
            self.pdf_page.cropBox.lowerLeft = (pdf_cur_x, pdf_start_y)
            self.pdf_page.cropBox.upperRight = (pdf_start_x, pdf_cur_y)


        print("PDF cropped ==========\n")
        self.save_pdf()

    # method for save
    def save_pdf(self):
        self.reset_flag()
        fname = filedialog.asksaveasfile()
        if not fname:
            return
        out_pdf = PdfFileWriter()
        out_pdf.addPage(self.pdf_page)
        out_f = open(fname.name, "wb")
        out_pdf.write(out_f)
        print("PDF saved ===========\n")


if __name__ == "__main__":
    print("******************* Tutorial ********************")
    print("1. Press folder to open pdf file.")
    print("2. After open a pdf file, drag for desired crop box position.")
    print("3. Press crop button to crop and save if the crop box is correctly positioned.")
    print("*************************************************")
    root = Tk()
    app = PdfApp(root)
    root.mainloop()