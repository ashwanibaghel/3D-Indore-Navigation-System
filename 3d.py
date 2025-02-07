import requests
import time
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D

# Replace with your ESP8266's IP address
ESP_IP = "http://192.168.94.100/data"


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


# Initialize Streamlit
st.title("Real-Time Sensor Data Visualization")

# Layout: Create two columns
col1, col2 = st.columns(2)

# Create placeholders for graphs
with col1:
    st.subheader("3D Vector Visualization")
    vector_plot_placeholder = st.empty()

with col2:
    st.subheader("Line Graph of Acceleration Magnitude")
    line_plot_placeholder = st.empty()

# Initialize data storage for line graph
time_data = []
accel_magnitude_data = []

while True:
    sensor_data = fetch_data()
    if sensor_data:
        # Update 3D plot
        fig_3d = plt.figure()
        ax = fig_3d.add_subplot(111, projection='3d')

        ax.set_xlim(-10, 10)
        ax.set_ylim(-10, 10)
        ax.set_zlim(-10, 10)

        ax.set_xlabel('X Axis')
        ax.set_ylabel('Y Axis')
        ax.set_zlabel('Z Axis')

        # Plot Acceleration Vector
        ax.quiver(0, 0, 0,
                  sensor_data['ax'], sensor_data['ay'], sensor_data['az'],
                  color='r', label='Acceleration')

        # Plot Gyroscope Vector
        ax.quiver(0, 0, 0,
                  sensor_data['gx'], sensor_data['gy'], sensor_data['gz'],
                  color='b', label='Gyroscope')

        ax.legend()
        vector_plot_placeholder.pyplot(fig_3d)

        # Update line graph of acceleration magnitude
        current_time = time.time()
        accel_magnitude = np.sqrt(
            sensor_data['ax'] ** 2 + sensor_data['ay'] ** 2 + sensor_data['az'] ** 2
        )

        time_data.append(current_time)
        accel_magnitude_data.append(accel_magnitude)

        # Limit to last 50 data points
        if len(time_data) > 50:
            time_data = time_data[-50:]
            accel_magnitude_data = accel_magnitude_data[-50:]

        fig_line, ax_line = plt.subplots()
        ax_line.plot(time_data, accel_magnitude_data, label='Accel Magnitude (m/s²)', color='g')
        ax_line.set_xlabel("Time (s)")
        ax_line.set_ylabel("Acceleration Magnitude")
        ax_line.legend()
        line_plot_placeholder.pyplot(fig_line)

    # Update every 2 seconds
    time.sleep(2)
