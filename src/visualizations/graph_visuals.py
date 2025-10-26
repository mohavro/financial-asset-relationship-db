import plotly.graph_objects as go
import numpy as np
from typing import Tuple, List
from src.logic.asset_graph import AssetRelationshipGraph

def visualize_3d_graph(graph: AssetRelationshipGraph) -> go.Figure:
    """Create 3D visualization of asset relationship graph"""
    positions, asset_ids, colors, hover_texts, edges = graph.get_3d_visualization_data()
    edges_x, edges_y, edges_z = edges

    fig = go.Figure()

    # Add edges (single trace for performance)
    fig.add_trace(go.Scatter3d(
        x=edges_x, y=edges_y, z=edges_z,
        mode='lines',
        line=dict(color='rgba(125, 125, 125, 0.25)', width=1),
        hoverinfo='none',
        name='Relationships'
    ))

    # Add nodes
    fig.add_trace(go.Scatter3d(
        x=positions[:, 0], y=positions[:, 1], z=positions[:, 2],
        mode='markers+text',
        marker=dict(
            size=10,
            color=colors,
            opacity=0.85,
            line=dict(color='rgba(0,0,0,0.5)', width=1)
        ),
        text=asset_ids,
        hovertext=hover_texts,
        hoverinfo='text',
        textposition="top center",
        name='Assets'
    ))

    fig.update_layout(
        title="Financial Asset Relationship Network - 3D Visualization",
        scene=dict(
            xaxis=dict(title='Dimension 1'),
            yaxis=dict(title='Dimension 2'),
            zaxis=dict(title='Dimension 3'),
            bgcolor='rgba(240, 240, 240, 0.9)'
        ),
        width=1200,
        height=800,
        showlegend=True,
        hovermode='closest'
    )

    return fig