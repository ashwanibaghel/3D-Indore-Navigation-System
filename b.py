import numpy as np
import plotly.graph_objs as go
from stl import mesh

# Load the STL file
your_stl_file = 'img.stl'  # Apna path daalo
stl_mesh = mesh.Mesh.from_file(your_stl_file)

# Extract vertices and faces
x, y, z = [], [], []
for f in stl_mesh.vectors:
    for point in f:
        x.append(point[0])
        y.append(point[1])
        z.append(point[2])

# Normalize Z values (you can adjust this factor)
z_min, z_max = np.min(z), np.max(z)
z_range = z_max - z_min
z_normalized = (z - z_min) / z_range  # Normalizing between 0 and 1

# Apply scaling factor to Z axis for better visualization
scale_factor = 10  # Adjust this value for better scaling
z_scaled = z_normalized * scale_factor

# Create a simple 3D plot with scaled Z-axis
trace = go.Mesh3d(
    x=x,
    y=y,
    z=z_scaled,  # Use the scaled Z-values
    opacity=0.7,
    color='lightblue',
    flatshading=True
)

layout = go.Layout(
    scene=dict(
        xaxis=dict(title='X'),
        yaxis=dict(title='Y'),
        zaxis=dict(title='Z'),
        aspectmode='cube'
    ),
    title="3D Model"
)

# Show plot
fig = go.Figure(data=[trace], layout=layout)
fig.show()
