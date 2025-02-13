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
        self.image_paths = []
        self.current_index = 0
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.is_dragging = False
        self.start_x = 0
        self.start_y = 0
        self.slideshow_active = False

        # UI
        self.canvas = tk.Canvas(root, bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Add Import Button
        self.buttonImport = tk.Button(root, 
                                      text="Import Image Folder", 
                                      command=self.load_folder)
        self.buttonImport.pack(padx=20, pady=20)

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
        
        # Load images
        self.load_folder()

    def load_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.image_paths = [os.path.join(folder_selected, f) for f in os.listdir(folder_selected)
                                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
            self.current_index = 0
            if self.image_paths:
                self.show_image()

    def show_image(self):
        if not self.image_paths:
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
        img_resized = np.roll(img_resized, shift=(self.offset_y, self.offset_x), axis=(0, 1))

        # Convert image for Tkinter
        img_pil = Image.fromarray(img_resized)
        self.tk_image = ImageTk.PhotoImage(img_pil)
        self.canvas.create_image(screen_w // 2, screen_h // 2, anchor="center", image=self.tk_image)

    def next_image(self, event=None):
        if self.image_paths:
            self.current_index = (self.current_index + 1) % len(self.image_paths)
            self.reset_view()
            self.show_image()

    def prev_image(self, event=None):
        if self.image_paths:
            self.current_index = (self.current_index - 1) % len(self.image_paths)
            self.reset_view()
            self.show_image()

    def zoom(self, event):
        factor = 1.1 if event.delta > 0 else 0.9
        self.scale *= factor
        self.show_image()

    def start_pan(self, event):
        self.is_dragging = True
        self.start_x, self.start_y = event.x, event.y

    def pan_image(self, event):
        if self.is_dragging:
            self.offset_x += (event.x - self.start_x) // 2
            self.offset_y += (event.y - self.start_y) // 2
            self.start_x, self.start_y = event.x, event.y
            self.show_image()

    def reset_view(self):
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0

    def toggle_fullscreen(self, event=None):
        self.root.attributes('-fullscreen', not self.root.attributes('-fullscreen'))

    def toggle_slideshow(self, event=None):
        self.slideshow_active = not self.slideshow_active
        if self.slideshow_active:
            self.run_slideshow()

    def run_slideshow(self):
        if self.slideshow_active:
            self.next_image()
            self.root.after(3000, self.run_slideshow)

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageGallery(root)

    root.iconbitmap("./assets/icon.ico")

    root.mainloop()