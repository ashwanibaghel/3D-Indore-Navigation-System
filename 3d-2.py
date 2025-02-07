import pandas as pd
import numpy as np
import requests
import streamlit as st
from scipy.signal import butter, filtfilt
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from filterpy.kalman import KalmanFilter
import time

ESP_IP = "http://192.168.94.100/data"


# Function to fetch sensor data from the ESP device
def fetch_data():
    try:
        response = requests.get(ESP_IP, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if all(key in data for key in ['ax', 'ay', 'az', 'gx', 'gy', 'gz']):
                return {
                    'Accelerometer_X': [data['ax']],
                    'Accelerometer_Y': [data['ay']],
                    'Accelerometer_Z': [data['az']],
                    'Gyroscope_X': [data['gx']],
                    'Gyroscope_Y': [data['gy']],
                    'Gyroscope_Z': [data['gz']]
                }
            else:
                st.error("Error: Missing keys in data")
        else:
            st.error(f"Error: Received status code {response.status_code}")
    except Exception as e:
        st.error(f"Error fetching data: {e}")
    return None


# Apply Butterworth filter
def butter_filter(data, cutoff, fs, btype, order=2):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype=btype, analog=False)
    if len(data) >= 3 * max(len(a), len(b)):
        return filtfilt(b, a, data)
    else:
        st.warning("Data length too short for filtering")
        return data


# Complementary filter for sensor fusion
def complementary_filter(acc, gyr, dt, alpha=0.98):
    acc_angle = np.arctan2(acc[1], acc[2]) * (180.0 / np.pi)
    gyr_angle = gyr[0] * dt
    angle = alpha * gyr_angle + (1 - alpha) * acc_angle
    return angle


# Create a placeholder for dynamic updates
st.title("Real-Time Sensor Data Visualization")

# Streamlit dynamic plot update
angle_plot = st.empty()  # Empty placeholder for angle graph
three_d_plot = st.empty()  # Empty placeholder for 3D graph

angles = []
data_buffer = []  # Buffer to store incoming data points
while True:
    # Fetch new data periodically
    data = fetch_data()
    if data:
        accX = np.array(data['Accelerometer_X'])
        accY = np.array(data['Accelerometer_Y'])
        accZ = np.array(data['Accelerometer_Z'])
        gyrX = np.array(data['Gyroscope_X'])
        gyrY = np.array(data['Gyroscope_Y'])
        gyrZ = np.array(data['Gyroscope_Z'])

        if len(accX) > 0:
            # Add new data to buffer
            data_buffer.append((accX[0], accY[0], accZ[0], gyrX[0], gyrY[0], gyrZ[0]))

            if len(data_buffer) > 10:  # Ensure there's enough data for filtering
                # Extract values for filtering and processing
                accX_buffer, accY_buffer, accZ_buffer, gyrX_buffer, gyrY_buffer, gyrZ_buffer = zip(*data_buffer)

                # Calculate magnitude of accelerometer data
                acc_mag = np.sqrt(np.array(accX_buffer) ** 2 + np.array(accY_buffer) ** 2 + np.array(accZ_buffer) ** 2)

                # Apply high-pass filter to accelerometer magnitude
                acc_mag_filt = butter_filter(acc_mag, cutoff=0.01, fs=256, btype='high')

                # Use complementary filter to fuse accelerometer and gyroscope data
                angle = complementary_filter([accX_buffer[-1], accY_buffer[-1], accZ_buffer[-1]],
                                             [gyrX_buffer[-1], gyrY_buffer[-1], gyrZ_buffer[-1]], dt=1 / 256)
                angles.append(angle)

                # Update the angle plot
                angle_plot.line_chart(pd.DataFrame(angles, columns=["Angle"]))

                # 3D Plot (if required)
                fig = plt.figure()
                ax = fig.add_subplot(111, projection='3d')
                ax.plot(angles, angles, angles)  # Placeholder for 3D motion
                three_d_plot.pyplot(fig)

                # Remove oldest data to keep the buffer size manageable
                data_buffer.pop(0)

        else:
            st.warning("Fetched data is empty!")
    else:
        st.error("No data fetched from ESP device.")

    # Add a small delay to allow Streamlit to update the plot
    time.sleep(1)  # Adjust as needed for data fetch rate
