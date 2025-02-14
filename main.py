import os
import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from ctypes import windll

windll.shcore.SetProcessDpiAwareness(1)

class ImageGallery:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Gallery")
        self.root.attributes('-fullscreen', True)  # Start in fullscreen mode

        # Variables
        self.image_paths = [] #list of image file paths
        self.current_index = 0 #track the curretly displayed image
        self.scale = 1.0 #zoom level
        self.offset_x = 0 #horizontal movement offset
        self.offset_y = 0 #vertical
        self.is_dragging = False # track if the image is being dragged
        self.start_x = 0 #store staring x position for dragging
        self.start_y = 0 #for y position
        self.slideshow_active = False# track slideshow mode

        # UI
        self.canvas = tk.Canvas(root, bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True) #Makes the canvas fill the whole window

       # Add Import Button
        self.buttonImport = tk.Button(root, 
                                      text="Import Image Folder", 
                                      command=self.load_folder,
                                      bg="white")
        self.buttonImport.pack(side=tk.LEFT, padx=20, pady=20, fill=tk.X)

        self.buttonImport = tk.Button(root, 
                                      text="Next Image", 
                                      command=self.next_image,
                                      bg="white")
        self.buttonImport.pack(side=tk.RIGHT, padx=20, pady=20, fill=tk.X)

        self.buttonImport = tk.Button(root, 
                                      text="Previous Image", 
                                      command=self.prev_image,
                                      bg="white")
        self.buttonImport.pack(side=tk.LEFT, padx=20, pady=20, fill=tk.X)

        # Bindings
        self.root.bind("<Left>", self.prev_image)
        self.root.bind("<Right>", self.next_image)
        self.root.bind("<Escape>", lambda e: root.quit())
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<MouseWheel>", self.zoom)
        self.root.bind("<Control-MouseWheel>", self.zoom)
        self.root.bind("<ButtonPress-1>", self.start_pan)
        self.root.bind("<B1-Motion>", self.pan_image)
        self.root.bind("<space>", self.toggle_slideshow)
        
    def load_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.image_paths = [os.path.join(folder_selected, f) for f in os.listdir(folder_selected)
                                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
            self.current_index = 0
            if self.image_paths:#stores all images in it
                self.show_image()


    def show_image(self):
        if not self.image_paths:
            return
        
        img_path = self.image_paths[self.current_index]
        img = cv2.imread(img_path)# load image using opencv
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)#converts bgr to rgb bz it wants rgb

        # Resize while maintaining aspect ratio
        screen_w, screen_h = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        img_h, img_w = img.shape[:2]
        scale = min(screen_w / img_w, screen_h / img_h)
        new_w, new_h = int(img_w * scale * self.scale), int(img_h * scale * self.scale)

        img_resized = cv2.resize(img, (new_w, new_h))
        img_resized = np.roll(img_resized, shift=(self.offset_y, self.offset_x), axis=(0, 1))

        # Convert image for Tkinter
        img_pil = Image.fromarray(img_resized)
        self.tk_image = ImageTk.PhotoImage(img_pil)
        self.canvas.create_image(screen_w // 2, screen_h // 2, anchor="center", image=self.tk_image)

    def next_image(self, event=None): #moves to the next image 
        if self.image_paths:
            self.current_index = (self.current_index + 1) % len(self.image_paths)
            self.reset_view() #resets zoom position
            self.show_image()

    def prev_image(self, event=None):# moves to the previous image.
        if self.image_paths:
            self.current_index = (self.current_index - 1) % len(self.image_paths)
            self.reset_view()
            self.show_image()

    def zoom(self, event): #Zooms in/out when scrolling the mouse wheel.
        factor = 1.1 if event.delta > 0 else 0.9
        self.scale *= factor
        self.show_image()

    def start_pan(self, event):# starts panning when mouse is pressed.
        self.is_dragging = True
        self.start_x, self.start_y = event.x, event.y

    def pan_image(self, event):# moves the image while dragging.
        if self.is_dragging:
            self.offset_x += (event.x - self.start_x) // 2
            self.offset_y += (event.y - self.start_y) // 2
            self.start_x, self.start_y = event.x, event.y
            self.show_image()

    def reset_view(self):
        self.scale = 1.0 #Resets zoom to its original size.
        self.offset_x = 0 #Moves the image back to its original position
        self.offset_y = 0

    def toggle_fullscreen(self, event=None):
        self.root.attributes('-fullscreen', not self.root.attributes('-fullscreen'))

    def toggle_slideshow(self, event=None): #does slideshow when i hit spacebar
        self.slideshow_active = not self.slideshow_active
        if self.slideshow_active:
            self.run_slideshow()

    def run_slideshow(self): # switches images every 3 seconds while i hit slideshow
        if self.slideshow_active:
            self.next_image()
            self.root.after(3000, self.run_slideshow) # switches images every 3 seconds while i hit slideshow

if __name__ == "__main__":
    root = tk.Tk() #creates the main tkinter window
    app = ImageGallery(root) #creates a instance of imagegallery class

    root.iconbitmap("./assets/icon.ico") #Sets the window icon (Windows only).


    root.mainloop()