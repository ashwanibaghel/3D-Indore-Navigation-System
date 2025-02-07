import matplotlib.pyplot as plt
import networkx as nx


# Create the flow diagram
def create_flow_diagram(filepath):
    G = nx.DiGraph()
    nodes = [
        "Data Collection\n(Accelerometer, Gyroscope,\nMagnetometer, GPS, Altimeter)",
        "Data Processing\n(Kalman Filter, Error Compensation)",
        "Data Storage\n(Firebase)",
        "Visualization\n(Person-In Mode / Commander Mode)",
        "Automatic Floor Switching\n(Based on Altitude)"
    ]

    G.add_edges_from([
        (nodes[0], nodes[1]),
        (nodes[1], nodes[2]),
        (nodes[2], nodes[3]),
        (nodes[3], nodes[4])
    ])

    pos = {
        nodes[0]: (0, 4),
        nodes[1]: (0, 3),
        nodes[2]: (0, 2),
        nodes[3]: (0, 1),
        nodes[4]: (0, 0)
    }

    plt.figure(figsize=(10, 8))
    nx.draw_networkx_nodes(G, pos, node_size=2000, node_color='skyblue', edgecolors='black')
    nx.draw_networkx_edges(G, pos, arrowstyle="->", arrowsize=20, edge_color="black", width=2)
    nx.draw_networkx_labels(G, pos, font_size=10, font_weight="bold", labels={n: n for n in nodes})

    plt.title("Workflow Diagram for 3DIndoorNavigation", fontsize=14)
    plt.axis("off")
    plt.savefig(filepath, bbox_inches='tight')
    plt.close()


# Create the reference chart
def create_reference_chart(filepath):
    categories = ["Mobile Sensors", "IoT Sensors", "Data Processing", "Data Storage", "Visualization"]
    values = [5, 3, 4, 3, 5]  # Example relative scores for importance or focus in the system.

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(categories, values, color="skyblue", edgecolor="black")
    ax.set_xlabel("Relative Importance", fontsize=12)
    ax.set_title("System Components: Importance Reference", fontsize=14)
    ax.grid(axis="x", linestyle="--", alpha=0.7)

    plt.savefig(filepath, bbox_inches='tight')
    plt.close()


# Save diagrams locally
create_flow_diagram("flow_diagram_3DIndoorNavigation.png")
create_reference_chart("reference_chart_3DIndoorNavigation.png")

print("Diagrams saved successfully!")