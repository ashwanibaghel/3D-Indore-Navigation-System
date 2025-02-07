import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import socket
import time


# Madgwick filter (for real sensor data)
class Madgwick:
    def __init__(self, sample_freq=100):
        self.q0, self.q1, self.q2, self.q3 = 1.0, 0.0, 0.0, 0.0
        self.beta = 0.1
        self.sample_freq = sample_freq

    def update(self, gx, gy, gz, ax, ay, az, mx, my, mz):
        roll = np.arctan2(ay, az)
        pitch = np.arctan2(-ax, np.sqrt(ay ** 2 + az ** 2))
        yaw = np.arctan2(my, mx)

        self.q0 = np.cos(roll / 2) * np.cos(pitch / 2) * np.cos(yaw / 2) + np.sin(roll / 2) * np.sin(
            pitch / 2) * np.sin(yaw / 2)
        self.q1 = np.sin(roll / 2) * np.cos(pitch / 2) * np.cos(yaw / 2) - np.cos(roll / 2) * np.sin(
            pitch / 2) * np.sin(yaw / 2)
        self.q2 = np.cos(roll / 2) * np.sin(pitch / 2) * np.cos(yaw / 2) + np.sin(roll / 2) * np.cos(
            pitch / 2) * np.sin(yaw / 2)
        self.q3 = np.cos(roll / 2) * np.cos(pitch / 2) * np.sin(yaw / 2) - np.sin(roll / 2) * np.sin(
            pitch / 2) * np.cos(yaw / 2)

        return self.q0, self.q1, self.q2, self.q3


# Initialize UDP socket
import socket

# Define UDP IP and Port
UDP_IP = "0.0.0.0"  # Accept connections from all interfaces
UDP_PORT = 80     # Ensure this port is available

# Create UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

try:
    # Bind socket to IP and Port
    sock.bind((UDP_IP, UDP_PORT))
    print(f"Listening on {UDP_IP}:{UDP_PORT}")
except OSError as e:
    print(f"Error: {e}")
    exit(1)

while True:
    # Receive data from client
    data, addr = sock.recvfrom(1024)
    print(f"Received message: {data} from {addr}")


# Load the floor plan
floor_plan = mpimg.imread(r"C:\Users\ashwa\OneDrive\Desktop\floor_plan.jpg")

# Initialize Madgwick filter
filter = Madgwick(sample_freq=100)

# Variables for position (initialized to 0)
position_x = 10
position_y = 10
position_z = 0

# Set up Streamlit page
st.set_page_config(layout="wide")
st.title("Real-Time 3D and Floor Plan Position Tracking")

# Read data from UDP socket and update position
while True:
    # Receive data from UDP socket
    data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
    try:
        # Assuming your sensor sends comma-separated values like: ax, ay, az, gx, gy, gz, mx, my, mz
        data = data.decode().strip()  # Decode bytes to string and strip newline/space
        ax, ay, az, gx, gy, gz, mx, my, mz = map(float, data.split(','))  # Convert to floats
    except:
        continue  # If data is not valid, skip it

    # Update filter with real sensor data
    q0, q1, q2, q3 = filter.update(gx, gy, gz, ax, ay, az, mx, my, mz)

    # Convert quaternion to Euler angles (pitch, roll, yaw)
    roll = np.arctan2(2 * (q0 * q1 + q2 * q3), 1 - 2 * (q1 ** 2 + q2 ** 2))
    pitch = np.arcsin(2 * (q0 * q2 - q3 * q1))
    yaw = np.arctan2(2 * (q0 * q3 + q1 * q2), 1 - 2 * (q2 ** 2 + q3 ** 2))

    # Update position based on yaw
    position_x += 0.1 * np.cos(yaw)
    position_y += 0.1 * np.sin(yaw)
    position_z = pitch

    # Create 3D plot for real-time tracking
    fig3d = plt.figure(figsize=(8, 6))
    ax3d = fig3d.add_subplot(111, projection="3d")
    ax3d.set_xlabel("X Position")
    ax3d.set_ylabel("Y Position")
    ax3d.set_zlabel("Z Position")
    ax3d.set_title("3D Position Tracking")
    ax3d.scatter(position_x, position_y, position_z, color="red", marker="o")

    # Display 3D plot in Streamlit
    st.pyplot(fig3d)

    # Create 2D plot for floor plan
    fig2d = plt.figure(figsize=(8, 6))
    ax2d = fig2d.add_subplot(111)
    ax2d.imshow(floor_plan, extent=[0, 20, 0, 20])  # Adjust extent as per your floor plan dimensions
    ax2d.scatter(position_x, position_y, color="red", marker="o")
    ax2d.set_title("Real-time Position on Floor Plan")

    # Display 2D plot in Streamlit
    st.pyplot(fig2d)

    # Pause for update interval
    time.sleep(0.1)
