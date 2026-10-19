"""Cloud-safe interactive 3D wave app.

This version does not invoke Manim, FFmpeg, LaTeX, Cairo, or subprocesses.
It therefore avoids native dependency installation failures on Streamlit Cloud.
"""
from __future__ import annotations

import numpy as np
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Interactive 3D Wave", page_icon="🎥", layout="wide")

COLOR_MAP = {
    "BLUE": "#1f77b4",
    "RED": "#d62728",
    "GREEN": "#2ca02c",
    "PURPLE": "#9467bd",
}


def build_wave_figure(
    color: str,
    amplitude: float,
    frequency: float,
    phase_speed: float,
    frame_count: int,
) -> go.Figure:
    """Create an animated 3D sinusoidal wave using Plotly frames."""
    x = np.linspace(-2 * np.pi, 2 * np.pi, 500)
    phases = np.linspace(0, 2 * np.pi, frame_count, endpoint=False)

    def coordinates(phase: float) -> tuple[np.ndarray, np.ndarray]:
        y = amplitude * np.sin(frequency * x - phase_speed * phase)
        z = 0.30 * amplitude * np.cos(frequency * x - phase_speed * phase)
        return y, z

    initial_y, initial_z = coordinates(phases[0])
    line_color = COLOR_MAP[color]

    figure = go.Figure(
        data=[
            go.Scatter3d(
                x=x,
                y=initial_y,
                z=initial_z,
                mode="lines",
                line={"color": line_color, "width": 8},
                name="Wave",
            )
        ],
        frames=[
            go.Frame(
                name=str(index),
                data=[
                    go.Scatter3d(
                        x=x,
                        y=coordinates(phase)[0],
                        z=coordinates(phase)[1],
                        mode="lines",
                        line={"color": line_color, "width": 8},
                    )
                ],
            )
            for index, phase in enumerate(phases)
        ],
    )

    figure.update_layout(
        height=700,
        margin={"l": 0, "r": 0, "t": 50, "b": 0},
        title="Animated 3D Wave",
        scene={
            "xaxis_title": "X",
            "yaxis_title": "Amplitude",
            "zaxis_title": "Depth",
            "xaxis": {"range": [-2 * np.pi, 2 * np.pi]},
            "yaxis": {"range": [-2.2 * amplitude, 2.2 * amplitude]},
            "zaxis": {"range": [-1.2 * amplitude, 1.2 * amplitude]},
            "camera": {"eye": {"x": 1.7, "y": 1.7, "z": 1.1}},
            "aspectmode": "manual",
            "aspectratio": {"x": 2.4, "y": 1.0, "z": 0.7},
        },
        updatemenus=[
            {
                "type": "buttons",
                "direction": "left",
                "x": 0.5,
                "xanchor": "center",
                "y": 0.02,
                "yanchor": "bottom",
                "buttons": [
                    {
                        "label": "Play",
                        "method": "animate",
                        "args": [
                            None,
                            {
                                "frame": {"duration": 45, "redraw": True},
                                "transition": {"duration": 0},
                                "fromcurrent": True,
                                "mode": "immediate",
                            },
                        ],
                    },
                    {
                        "label": "Pause",
                        "method": "animate",
                        "args": [
                            [None],
                            {
                                "frame": {"duration": 0, "redraw": False},
                                "transition": {"duration": 0},
                                "mode": "immediate",
                            },
                        ],
                    },
                ],
            }
        ],
    )
    return figure


st.title("Interactive 3D Wave Generator")
st.caption("Cloud-safe animation without Manim, LaTeX, FFmpeg, or OS packages.")

with st.sidebar:
    st.header("Wave settings")
    color_choice = st.selectbox("Wave color", list(COLOR_MAP))
    amplitude = st.slider("Amplitude", 0.25, 3.0, 1.0, 0.05)
    frequency = st.slider("Frequency", 0.25, 4.0, 1.0, 0.05)
    phase_speed = st.slider("Motion speed", 0.25, 4.0, 1.0, 0.05)
    frame_count = st.slider("Animation frames", 20, 120, 60, 10)

figure = build_wave_figure(
    color=color_choice,
    amplitude=amplitude,
    frequency=frequency,
    phase_speed=phase_speed,
    frame_count=frame_count,
)
st.plotly_chart(figure, use_container_width=True)
st.info("Use Play/Pause below the chart. Drag the chart to rotate the 3D view.")
