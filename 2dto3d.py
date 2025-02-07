import plotly.graph_objects as go
import numpy as np
from PIL import Image

# Load the 2D image
img = Image.open('kiet_2nd_floor.jpg')  # Replace with your image path
img = img.convert("RGBA")
img_array = np.array(img)

# Create a 3D meshgrid for floor plan
x = np.linspace(0, img.width, img.width)
y = np.linspace(0, img.height, img.height)
x, y = np.meshgrid(x, y)

# Z height is set to zero (flat surface)
z = np.zeros_like(x)

# Create 3D surface plot
fig = go.Figure(data=[go.Mesh3d(
    x=x.flatten(),
    y=y.flatten(),
    z=z.flatten(),
    color='lightblue',  # Set a single color here (e.g., 'lightblue', 'gray', etc.)
    opacity=0.5         # Set transparency
)])

# Update layout
fig.update_layout(
    scene=dict(
        xaxis_title='X',
        yaxis_title='Y',
        zaxis_title='Height'
    ),
    title='3D Floor Plan with Fixed Color'
)

fig.show()
