import requests
import time
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.image as mpimg

# Replace with your ESP8266's IP address
ESP_IP = "http://192.168.94.100/data"

# Fetch data from ESP8266
def fetch_data():
    try:
        response = requests.get(ESP_IP, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if all(key in data for key in ['ax', 'ay', 'az', 'gx', 'gy', 'gz']):
                return data
            else:
                st.error("Error: Missing keys in data")
        else:
            st.error(f"Error: Received status code {response.status_code}")
    except requests.exceptions.RequestException as e:
        st.error(f"Request error: {e}")
    except ValueError:
        st.error("Error: Failed to decode JSON")
    return None

# Complementary filter for combining accelerometer and gyroscope data
def complementary_filter(accel, gyro, prev_angle, alpha, dt):
    accel_angle = np.arctan2(accel[1], accel[2])  # Compute angle from accelerometer
    gyro_angle = prev_angle + gyro * dt          # Compute angle from gyroscope
    return alpha * gyro_angle + (1 - alpha) * accel_angle

# Streamlit app title
st.title("Real-Time Sensor Data Visualization with Noise Handling")

# Layout: Create two columns
col1, col2 = st.columns(2)

# Create placeholders for plots
with col1:
    st.subheader("3D Orientation Visualization")
    vector_plot_placeholder = st.empty()

with col2:
    st.subheader("Real-time Movement on Floor Plan")
    floor_plan_placeholder = st.empty()

# Initialize variables
position_x, position_y = 10, 10  # Initial position
velocity_x, velocity_y = 0, 0
dt = 0.05  # Sampling time (adjust based on ESP8266 data rate)
alpha = 0.98  # Complementary filter constant
roll, pitch, yaw = 0, 0, 0  # Initial angles
damping = 0.9  # Damping factor for velocity
threshold = 0.1  # Threshold for noise filtering

# Load floor plan image
floor_plan_img = mpimg.imread("floor_plan.jpg")  # Replace with your floor plan image path

# Infinite loop to fetch and visualize real-time data
while True:
    sensor_data = fetch_data()
    if sensor_data:
        # Fetch accelerometer and gyroscope data
        ax, ay, az = sensor_data['ax'], sensor_data['ay'], sensor_data['az']
        gx, gy, gz = sensor_data['gx'], sensor_data['gy'], sensor_data['gz']

        # Apply noise filtering: Ignore small values
        if abs(ax) < threshold: ax = 0
        if abs(ay) < threshold: ay = 0
        if abs(az) < threshold: az = 0
        if abs(gx) < threshold: gx = 0
        if abs(gy) < threshold: gy = 0
        if abs(gz) < threshold: gz = 0

        # Update roll, pitch, and yaw using complementary filter
        roll = complementary_filter([ax, ay, az], gx, roll, alpha, dt)
        pitch = complementary_filter([ay, ax, az], gy, pitch, alpha, dt)
        yaw += gz * dt  # Yaw can be directly integrated from gyroscope

        # Update velocity (based on roll and pitch)
        velocity_x = (velocity_x + ax * dt) * damping
        velocity_y = (velocity_y + ay * dt) * damping

        # Update position (based on velocity)
        position_x += velocity_x * dt
        position_y += velocity_y * dt

        # Create 3D orientation plot
        fig_3d = plt.figure()
        ax_3d = fig_3d.add_subplot(111, projection='3d')
        ax_3d.quiver(0, 0, 0, roll, pitch, yaw, color='r', label='Orientation')
        ax_3d.set_xlim(-10, 10)
        ax_3d.set_ylim(-10, 10)
        ax_3d.set_zlim(-10, 10)
        ax_3d.set_xlabel('Roll')
        ax_3d.set_ylabel('Pitch')
        ax_3d.set_zlabel('Yaw')
        ax_3d.legend()
        vector_plot_placeholder.pyplot(fig_3d)

        # Plot position on the floor plan
        fig_floor_plan, ax_floor_plan = plt.subplots(figsize=(8, 6))
        ax_floor_plan.imshow(floor_plan_img, extent=[0, 20, 0, 20])  # Adjust extent for your floor plan
        ax_floor_plan.scatter(position_x, position_y, color="red", marker="o", label="Movement")
        ax_floor_plan.set_title("Real-time Position on Floor Plan")
        ax_floor_plan.legend()
        floor_plan_placeholder.pyplot(fig_floor_plan)

    # Update every `dt` seconds
    time.sleep(dt)
