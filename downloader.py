import os
import requests
from tqdm import tqdm

# Create folder
save_folder = "lorem_full_res_images"
os.makedirs(save_folder, exist_ok=True)

# Number of images to download
num_images = 1000

# Function to get image info and download full resolution
def download_image(image_id, save_path):
    info_url = f"https://picsum.photos/id/{image_id}/info"
    try:
        info = requests.get(info_url, timeout=10).json()
        full_res_url = info["download_url"]

        response = requests.get(full_res_url, timeout=10)
        if response.status_code == 200:
            with open(save_path, "wb") as f:
                f.write(response.content)
    except requests.exceptions.RequestException as e:
        print(f"Error downloading image {image_id}: {e}")

# Download images
for i in tqdm(range(num_images), desc="Downloading Images"):
    image_id = i + 1  # Image IDs start from 1
    image_path = os.path.join(save_folder, f"image_{image_id}.jpg")
    download_image(image_id, image_path)

print(f"✅ Download complete! Images saved in '{save_folder}'")
