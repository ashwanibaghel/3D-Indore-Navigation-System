import firebase_admin
from firebase_admin import credentials, db
import time
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

cred = credentials.Certificate("service_account_key.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://d-live-system003-default-rtdb.firebaseio.com/'
})

ref = db.reference('users/combined_data')

floor_image_path = "kiet_2nd_floor.jpg"
try:
    img = Image.open(floor_image_path)
except Exception as e:
    print(f"Error loading floor image: {e}")
    exit()

img = img.transpose(Image.FLIP_TOP_BOTTOM)

plt.ion()
fig = plt.figure(figsize=(14, 10))
gs = fig.add_gridspec(2, 2, height_ratios=[2, 1])

ax_floor = fig.add_subplot(gs[0, :])
ax_floor.imshow(img, extent=[0, 1650, 0, 1275], origin='lower')
ax_floor.set_xlim([0, 1650])
ax_floor.set_ylim([0, 1275])

ax_floor.set_title("Real-time Movement on Floor Plan", fontsize=14, fontweight='bold', pad=20)

ax_accel = fig.add_subplot(gs[1, 0])
ax_gyro = fig.add_subplot(gs[1, 1])

accel_x, accel_y, accel_z = [], [], []
gyro_x, gyro_y, gyro_z = [], [], []
timestamps = []

x_pos, y_pos = 500, 400
scaling_factor = 1 / 100

while True:
    print("Fetching data from Firebase...")
    data = ref.get()

    if data:
        accelerometer_data = data.get('accelerometer', {})
        gyroscope_data = data.get('gyroscope', {})
        magnetometer_data = data.get('magnetometer', {})
        azimuth_deg = data.get('azimuth', 0)
        azimuth_rad = np.radians(azimuth_deg)

        azimuth_deg = (azimuth_deg - 45) % 360
        azimuth_rad = np.radians(azimuth_deg)

        x_raw = accelerometer_data.get('x', 0)
        y_raw = accelerometer_data.get('y', 0)
        z_raw = accelerometer_data.get('z', 0)

        gyro_x_val = gyroscope_data.get('x', 0)
        gyro_y_val = gyroscope_data.get('y', 0)
        gyro_z_val = gyroscope_data.get('z', 0)

        x_adjusted = (x_raw * np.cos(azimuth_rad) - y_raw * np.sin(azimuth_rad)) * scaling_factor
        y_adjusted = (x_raw * np.sin(azimuth_rad) + y_raw * np.cos(azimuth_rad)) * scaling_factor

        x_pos += x_adjusted
        y_pos += y_adjusted
        x_pos = np.clip(x_pos, 0, 1650)
        y_pos = np.clip(y_pos, 0, 1275)

        current_time = time.time()
        timestamps.append(current_time)
        accel_x.append(x_raw)
        accel_y.append(y_raw)
        accel_z.append(z_raw)
        gyro_x.append(gyro_x_val)
        gyro_y.append(gyro_y_val)
        gyro_z.append(gyro_z_val)

        ax_floor.clear()
        ax_floor.imshow(img, extent=[0, 1650, 0, 1275], origin='lower')
        ax_floor.set_xlim([0, 1650])
        ax_floor.set_ylim([0, 1275])
        ax_floor.scatter(x_pos, y_pos, color='red', s=50)
        arrow_length = 50
        ax_floor.arrow(x_pos, y_pos, arrow_length * np.cos(azimuth_rad),
                       arrow_length * np.sin(azimuth_rad), color='blue', head_width=20, head_length=30)

        ax_accel.clear()
        ax_accel.plot(timestamps, accel_x, label="Accel X", color="red")
        ax_accel.plot(timestamps, accel_y, label="Accel Y", color="green")
        ax_accel.plot(timestamps, accel_z, label="Accel Z", color="blue")
        ax_accel.legend(loc="upper left")
        ax_accel.set_title("Accelerometer Data")
        ax_accel.set_xlabel("Time")
        ax_accel.set_ylabel("Acceleration (cm/s²)")

        ax_gyro.clear()
        ax_gyro.plot(timestamps, gyro_x, label="Gyro X", color="orange")
        ax_gyro.plot(timestamps, gyro_y, label="Gyro Y", color="purple")
        ax_gyro.plot(timestamps, gyro_z, label="Gyro Z", color="brown")
        ax_gyro.legend(loc="upper left")
        ax_gyro.set_title("Gyroscope Data")
        ax_gyro.set_xlabel("Time")
        ax_gyro.set_ylabel("Angular Velocity (deg/s)")

        plt.tight_layout()
        plt.pause(0.1)

    else:
        print("No data found at the specified path.")

    time.sleep(2)
 