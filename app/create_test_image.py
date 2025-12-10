import numpy as np
from PIL import Image

# Create a simple image
width, height = 400, 300
img_array = np.zeros((height, width, 3), dtype=np.uint8)

# Add some shapes/colors
img_array[100:200, 100:300] = [255, 0, 0]    # Red rectangle
img_array[50:150, 50:250] = [0, 255, 0]      # Green rectangle  
img_array[200:280, 150:350] = [0, 0, 255]    # Blue rectangle
img_array[10:40, 10:40] = [255, 255, 0]      # Yellow square
img_array[250:290, 10:100] = [255, 0, 255]   # Purple rectangle

# Add some diagonal line
for i in range(50, 250):
    img_array[i, i] = [255, 255, 255]

# Save as JPEG
img = Image.fromarray(img_array)
img.save('test_hw.jpg')
print(f"Created test_hw.jpg - Size: {width}x{height} pixels")
print(f"File size: {width * height * 3} bytes")
