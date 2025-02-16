import os 
import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from ctypes import windll
import subprocess  # Import subprocess to open Image Processor
import sys  # Added sys module

windll.shcore.SetProcessDpiAwareness(1)  # Improve DPI scaling on Windows


class ImageGallery:
    def __init__(self, root):  # FIXED __init__
        self.root = root #stores the main window
        self.root.title("Image Gallery")#sets the title  of the windows
        self.root.attributes('-fullscreen', True)# makes window fullscreen

        # Variables
        self.image_paths = []#List to store paths of images in the selected folder.
        self.current_index = 0#tracks the currently displayed image
        self.scale = 1.0 #tracks zoom level of the image
        self.offset_x = 0 #tracks the dragging offset
        self.offset_y = 0 #same
        self.is_dragging = False #tracks whether the user is dragging the image
        self.start_x = 0 #stores the dragging positon of the drag
        self.start_y = 0
        self.slideshow_active = False # tracks whether the trackshow is running

        # UI Components #canvas- used to dras shapes images or complex grahics
        self.canvas = tk.Canvas(root, bg="black") #canves for widget for drawing images and shapes, black sets the background color to black
        self.canvas.pack(fill=tk.BOTH, expand=True) # makes the canvas fill the entire windows

        # Buttons
        self.buttonImport = tk.Button(root, text="Import Image Folder", command=self.load_folder, bg="white") #tk.Button: Creates a button widget.text="Import Image Folder": Sets the button text.command=self.load_folder: Calls the load_folder method when the button is clicked.bg="white": Sets the button background color to white.pack(side=tk.LEFT): Places the button on the left side of the window.
        self.buttonImport.pack(side=tk.LEFT, padx=20, pady=20, fill=tk.X)

        self.buttonNext = tk.Button(root, text="Next Image", command=self.next_image, bg="white")
        self.buttonNext.pack(side=tk.RIGHT, padx=20, pady=20, fill=tk.X)# similar to previous button , but for navigating images ad opening the image editor

        self.buttonPrev = tk.Button(root, text="Previous Image", command=self.prev_image, bg="white")
        self.buttonPrev.pack(side=tk.LEFT, padx=20, pady=20, fill=tk.X)

        # New Button: Open Image Processor
        self.buttonProcessor = tk.Button(root, text="Image Editor", command=self.open_image_processor, bg="white", fg="black")
        self.buttonProcessor.pack(side=tk.RIGHT, padx=20, pady=20, fill=tk.X)

        # Bindings
        self.root.bind("<Left>", self.prev_image)
        self.root.bind("<Right>", self.next_image)
        self.root.bind("<Escape>", lambda e: root.quit())
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<MouseWheel>", self.zoom)
        self.root.bind("<ButtonPress-1>", self.start_pan)
        self.root.bind("<B1-Motion>", self.pan_image)
        self.root.bind("<space>", self.toggle_slideshow)

    def load_folder(self):  # opens a folder dialog to select a folder filter the image png jpg and stores their path in self.image.paths. and displays the first image
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.image_paths = [os.path.join(folder_selected, f) for f in os.listdir(folder_selected)
                                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
            self.current_index = 0
            if self.image_paths:
                self.show_image()

    def show_image(self):# loads and displays the current image , resized the image to fit the screen while maintaning aspect ratio
        if not self.image_paths: # converts the image to format tkinter can display ands hows it on the canvas
            return

        img_path = self.image_paths[self.current_index]
        img = cv2.imread(img_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Resize while maintaining aspect ratio
        screen_w, screen_h = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        img_h, img_w = img.shape[:2]
        scale = min(screen_w / img_w, screen_h / img_h)
        new_w, new_h = int(img_w * scale * self.scale), int(img_h * scale * self.scale)

        img_resized = cv2.resize(img, (new_w, new_h))

        # Convert image for Tkinter
        img_pil = Image.fromarray(img_resized)
        self.tk_image = ImageTk.PhotoImage(img_pil)
        self.canvas.delete("all")  # Clear previous image
        self.canvas.create_image(screen_w // 2 + self.offset_x, screen_h // 2 + self.offset_y, anchor="center",
                                 image=self.tk_image)

    def next_image(self, event=None): #navigates to the next or previous image in the list
        if self.image_paths:
            self.current_index = (self.current_index + 1) % len(self.image_paths)
            self.reset_view()
            self.show_image()

    def prev_image(self, event=None):
        if self.image_paths:
            self.current_index = (self.current_index - 1) % len(self.image_paths)
            self.reset_view()
            self.show_image()

    def zoom(self, event): # zoom: zooms in or out using the mouse whell
        factor = 1.1 if event.delta > 0 else 0.9
        self.scale *= factor
        self.show_image()

    def start_pan(self, event):# starts dragging the imgae
        self.is_dragging = True
        self.start_x, self.start_y = event.x, event.y

    def pan_image(self, event):# pan moves the image while dragging
        if self.is_dragging:
            self.offset_x += (event.x - self.start_x) // 2
            self.offset_y += (event.y - self.start_y) // 2
            self.start_x, self.start_y = event.x, event.y
            self.show_image()

    def reset_view(self): #resets the zoom and pan to default values
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0

    def toggle_fullscreen(self, event=None): #toogles full screen mode
        self.root.attributes('-fullscreen', not self.root.attributes('-fullscreen'))

    def toggle_slideshow(self, event=None): # starts or stops the slideshow
        self.slideshow_active = not self.slideshow_active
        if self.slideshow_active:
            self.run_slideshow()

    def run_slideshow(self): # automatically shows the next image every 3 seconds
        if self.slideshow_active:
            self.next_image()
            self.root.after(3000, self.run_slideshow)

    def open_image_processor(self): # opens another python scrot ( imageprovessro.py)for image editing
        """Opens the Image Processor in a new window."""
        subprocess.Popen(["python", "ImageProcessor.py"])  # Runs ImageProcessor.py
    def open_image_processor(self):
        """Opens the Image Processor with the current image."""
        if self.image_paths:
            current_img = self.image_paths[self.current_index]
            subprocess.Popen(["python", "ImageProcessor.py", current_img])


if __name__ == "__main__":  # FIXED __name__ # creates the main window and runs the application
    root = tk.Tk()
    app = ImageGallery(root)
    root.iconbitmap("./assets/icon.ico")
    root.mainloop()  # FIXED: Ensure the GUI runs
