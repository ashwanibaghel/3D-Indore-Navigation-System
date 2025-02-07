import time

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.image as mpimg
import numpy as np

from firebash import fetch_data_from_firebase

# Floor image ko plot ke background mein set karne ka path
floor_image_path = "floor_plan.jpg"  # Apni floor image ka path dena
img = mpimg.imread(floor_image_path)

# Plot ko initialize karna
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Labels set karna
ax.set_xlabel('X-axis (Movement)')
ax.set_ylabel('Y-axis (Movement)')
ax.set_zlabel('Z-axis (Height)')

# Variables to track the movement on the floor
x_pos = 0
y_pos = 0
z_pos = 0


# Function to plot the data dynamically
def plot_data_on_floor(accelerometer_data, gyroscope_data, location_data, azimuth_data):
    global x_pos, y_pos, z_pos

    # Accelerometer data se movement ko update karna
    x_pos += accelerometer_data.get('x', 0)  # Update X position
    y_pos += accelerometer_data.get('y', 0)  # Update Y position
    z_pos += accelerometer_data.get('z', 0)  # Update Z position

    # Floor image ko background mein plot karna
    ax.clear()
    ax.plot_surface(np.linspace(-10, 10, 10), np.linspace(-10, 10, 10), np.zeros((10, 10)), rstride=1, cstride=1,
                    facecolors=img, shade=False)

    # Red dot ke saath position ko plot karna
    ax.scatter(x_pos, y_pos, z_pos, color='r', s=100)  # Red dot representing the movement

    # Labels ko update karna
    ax.set_xlabel('X-axis (Movement)')
    ax.set_ylabel('Y-axis (Movement)')
    ax.set_zlabel('Z-axis (Height)')

    # Plot ko show karna
    plt.draw()
    plt.pause(0.1)  # Update plot every 100ms


# Real-time plotting update karna
while True:
    # Firebase se data fetch karenge
    accelerometer_data, gyroscope_data, location_data, timestamp, azimuth_data = fetch_data_from_firebase()

    # Agar data available ho toh plot karenge
    if accelerometer_data:
        plot_data_on_floor(accelerometer_data, gyroscope_data, location_data, azimuth_data)
    else:
        print("No data to plot.")

    # Data ko har 2 second mein refresh karenge
    time.sleep(2)
