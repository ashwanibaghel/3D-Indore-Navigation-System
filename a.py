import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import time

# Load Floor Image
floor_image_path = "kiet_2nd_floor.jpg"
img = Image.open(floor_image_path).transpose(Image.FLIP_TOP_BOTTOM)

# Initialize Position
x_pos, y_pos = 500, 400
scaling_factor = 1 / 100

# Plot Setup
plt.ion()
fig, ax = plt.subplots(figsize=(10, 8))

# Display Floor Plan Once
ax.imshow(img, extent=[0, 1650, 0, 1275], origin="upper")
scatter_plot = ax.scatter(x_pos, y_pos, color="red", s=50)  # Initial Position Marker

ax.set_xlim(0, 1650)
ax.set_ylim(0, 1275)
ax.set_title("Real-time Movement on Floor Plan", fontsize=14, fontweight="bold")

# Main Loop for Updates
while True:
    print("Updating position...")

    # Simulated Data (Replace with Firebase Data)
    x_raw, y_raw = np.random.randint(-10, 10, size=2)  # Example accelerometer data
    azimuth_deg = 45  # Example azimuth
    azimuth_rad = np.radians(azimuth_deg)

    # Adjust Position
    x_adjusted = (x_raw * np.cos(azimuth_rad) - y_raw * np.sin(azimuth_rad)) * scaling_factor
    y_adjusted = (x_raw * np.sin(azimuth_rad) + y_raw * np.cos(azimuth_rad)) * scaling_factor

    x_pos += x_adjusted
    y_pos += y_adjusted
    x_pos = np.clip(x_pos, 0, 1650)
    y_pos = np.clip(y_pos, 0, 1275)

    # Update Scatter Plot Data
    scatter_plot.set_offsets([[x_pos, y_pos]])
    plt.pause(0.1)  # Pause for smooth updates

    time.sleep(1)
