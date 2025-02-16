import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import sys  # For command-line arguments

class ImageProcessor:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Processing & Editing")

        self.image_path = None
        self.original_image = None
        self.processed_image = None
        self.previous_image = None

        # UI Setup
        self.canvas = tk.Canvas(root, bg="gray")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.toolbar = tk.Frame(root, bg="#333")
        self.toolbar.pack(fill=tk.X, side=tk.BOTTOM)

        # Buttons
        tk.Button(self.toolbar, text="Load Image", command=self.load_image, bg="blue", fg="white").pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(self.toolbar, text="Enhance", command=self.enhance_image, bg="orange", fg="white").pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(self.toolbar, text="Undo", command=self.undo_last_edit, bg="red", fg="white").pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(self.toolbar, text="Save", command=self.save_image, bg="green", fg="white").pack(side=tk.LEFT, padx=5, pady=5)

        # Brightness Slider
        self.brightness_slider = ttk.Scale(self.toolbar, from_=-100, to=100, orient=tk.HORIZONTAL, command=self.adjust_brightness)
        self.brightness_slider.pack(side=tk.LEFT, padx=10)
        self.brightness_label = tk.Label(self.toolbar, text="Brightness")
        self.brightness_label.pack(side=tk.LEFT, padx=5)

        # Load Image from Arguments
        if len(sys.argv) > 1:
            self.image_path = sys.argv[1]
            self.load_image()

    def load_image(self):
        """Loads an image from file dialog or command-line argument."""
        if not self.image_path:
            self.image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.png;*.bmp;*.jpeg")])
        if self.image_path:
            self.original_image = cv2.imread(self.image_path)
            self.processed_image = self.original_image.copy()
            self.previous_image = self.processed_image.copy()
            self.display_image()

    def display_image(self):
        """Displays the processed image on the canvas."""
        if self.processed_image is None:
            return
        img_rgb = cv2.cvtColor(self.processed_image, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        img_pil.thumbnail((800, 600))
        self.tk_image = ImageTk.PhotoImage(img_pil)
        self.canvas.delete("all")
        self.canvas.create_image(400, 300, anchor=tk.CENTER, image=self.tk_image)

    def adjust_brightness(self, value):
        """Dynamically adjusts brightness based on slider movement."""
        if self.processed_image is not None:
            self.previous_image = self.original_image.copy()  # Store original before changing
            self.processed_image = cv2.convertScaleAbs(self.original_image, alpha=1, beta = float(value))
            self.display_image()

    def enhance_image(self):
        """Applies auto-contrast and sharpening to enhance the image."""
        if self.processed_image is not None:
            self.previous_image = self.processed_image.copy()
            kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])  # Sharpening filter
            self.processed_image = cv2.filter2D(self.processed_image, -1, kernel)
            self.display_image()

    def undo_last_edit(self):
        """Reverts the image to its previous state."""
        if self.previous_image is not None:
            self.processed_image = self.previous_image.copy()
            self.display_image()

    def save_image(self):
        """Saves the edited image."""
        if self.processed_image is not None:
            file_path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG", ".jpg"), ("PNG", ".png"), ("BMP", "*.bmp")])
            if file_path:
                cv2.imwrite(file_path, self.processed_image)
                messagebox.showinfo("Success", "Image saved successfully!")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessor(root)
    root.mainloop()
