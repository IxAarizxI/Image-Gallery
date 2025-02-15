import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

class ImageProcessor:
    def __init__(self, root):  # Fixed constructor
        self.root = root
        self.root.title("Image Processing & Editing")
        
        self.image_path = None
        self.original_image = None
        self.processed_image = None
        self.previous_image = None  # Stores the last state for undo
        self.brightness_value = 0   # Initial brightness value

        # UI Setup
        self.canvas = tk.Canvas(root, bg="gray")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.toolbar = tk.Frame(root, bg="#333")
        self.toolbar.pack(fill=tk.X, side=tk.BOTTOM)

        tk.Button(self.toolbar, text="Open Image", command=self.open_image, bg="gray", fg="white").pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(self.toolbar, text="Enhance", command=self.enhance_image, bg="gray", fg="white").pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(self.toolbar, text="Crop", command=self.start_crop, bg="gray", fg="white").pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(self.toolbar, text="Undo", command=self.undo_last_edit, bg="orange", fg="white").pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(self.toolbar, text="Save", command=self.save_image, bg="green", fg="white").pack(side=tk.LEFT, padx=5, pady=5)

        # Brightness Slider
        self.brightness_slider = tk.Scale(self.toolbar, from_=-100, to=100, orient=tk.HORIZONTAL, label="Brightness", command=self.adjust_brightness)
        self.brightness_slider.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Reset Brightness Button
        tk.Button(self.toolbar, text="Reset Brightness", command=self.reset_brightness, bg="red", fg="white").pack(side=tk.LEFT, padx=5, pady=5)

    def open_image(self):
        """Opens an image and resets brightness settings."""
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", ".jpg;.png;.jpeg;.bmp;*.gif")])
        if file_path:
            self.image_path = file_path
            self.original_image = cv2.imread(file_path)
            self.processed_image = self.original_image.copy()
            self.previous_image = self.processed_image.copy()
            self.display_image()
            self.brightness_slider.set(0)  # Reset slider when new image is opened

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
            brightness = int(value)
            self.processed_image = cv2.convertScaleAbs(self.original_image, alpha=1, beta=brightness)
            self.display_image()

    def reset_brightness(self):
        """Resets the brightness to its original state."""
        if self.original_image is not None:
            self.processed_image = self.original_image.copy()
            self.display_image()
            self.brightness_slider.set(0)  # Reset slider value to zero

    def enhance_image(self):
        """Applies auto-contrast and sharpening to enhance the image."""
        if self.processed_image is not None:
            self.previous_image = self.processed_image.copy()
            kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
            self.processed_image = cv2.filter2D(self.processed_image, -1, kernel)
            self.display_image()

    def start_crop(self):
        """Activates cropping mode."""
        messagebox.showinfo("Crop Mode", "Crop feature will be added soon!")

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

if __name__ == "__main__":  # Fixed this line
    root = tk.Tk()
    app = ImageProcessor(root)
    root.mainloop()
