"""Streamlit app that renders a genuine Manim MP4 file."""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import streamlit as st


st.set_page_config(
    page_title="Manim 3D Wave Renderer",
    page_icon="🎥",
    layout="wide",
)

MANIM_COLORS = {
    "Blue": "BLUE",
    "Red": "RED",
    "Green": "GREEN",
    "Purple": "PURPLE",
    "Yellow": "YELLOW",
    "Teal": "TEAL",
}

QUALITY_OPTIONS = {
    "Low quality (480p, fastest)": "l",
    "Medium quality (720p)": "m",
    "High quality (1080p)": "h",
}


def build_scene_code(
    color_constant: str,
    amplitude: float,
    frequency: float,
    rotation_rate: float,
) -> str:
    """Return the Manim scene source code for the selected settings."""
    return f'''from manim import *
import numpy as np


class StreamlitWave(ThreeDScene):
    def construct(self):
        axes = ThreeDAxes(
            x_range=[-7, 7, 1],
            y_range=[-3, 3, 1],
            z_range=[-2, 2, 1],
            x_length=11,
            y_length=5,
            z_length=3,
        )

        self.set_camera_orientation(phi=70 * DEGREES, theta=-35 * DEGREES)

        wave = ParametricFunction(
            lambda t: axes.c2p(
                t,
                {amplitude:.6f} * np.sin({frequency:.6f} * t),
                0.30 * {amplitude:.6f} * np.cos({frequency:.6f} * t),
            ),
            t_range=[-2 * PI, 2 * PI],
            color={color_constant},
            stroke_width=6,
        )

        self.play(Create(axes), run_time=1.0)
        self.play(Create(wave), run_time=1.5)
        self.begin_ambient_camera_rotation(rate={rotation_rate:.6f})
        self.wait(3.0)
        self.stop_ambient_camera_rotation()
        self.wait(0.5)
'''


def render_manim_video(
    scene_code: str,
    quality_flag: str,
) -> tuple[bytes | None, str]:
    """Render the scene and return MP4 bytes plus the Manim terminal log."""
    if shutil.which("ffmpeg") is None:
        return None, "FFmpeg is not installed. Check packages.txt deployment."

    with tempfile.TemporaryDirectory(prefix="manim_streamlit_") as temp_dir:
        work_dir = Path(temp_dir)
        scene_file = work_dir / "wave_scene.py"
        media_dir = work_dir / "media"
        scene_file.write_text(scene_code, encoding="utf-8")

        command = [
            sys.executable,
            "-m",
            "manim",
            str(scene_file),
            "StreamlitWave",
            f"-q{quality_flag}",
            "--media_dir",
            str(media_dir),
            "--disable_caching",
            "--format",
            "mp4",
        ]

        try:
            completed = subprocess.run(
                command,
                cwd=work_dir,
                capture_output=True,
                text=True,
                timeout=300,
                check=False,
            )
        except subprocess.TimeoutExpired as error:
            partial_log = (error.stdout or "") + "\n" + (error.stderr or "")
            return None, "Rendering exceeded the 300-second safety limit.\n" + partial_log

        terminal_log = (
            f"Command: {' '.join(command)}\n\n"
            f"STDOUT:\n{completed.stdout}\n\n"
            f"STDERR:\n{completed.stderr}"
        )

        if completed.returncode != 0:
            return None, terminal_log

        videos = sorted(media_dir.rglob("StreamlitWave.mp4"))
        if not videos:
            return None, terminal_log + "\n\nNo MP4 output file was found."

        return videos[-1].read_bytes(), terminal_log


st.title("Manim-rendered 3D Wave MP4")
st.write(
    "This app runs the Manim renderer on the Streamlit server and produces "
    "a genuine MP4 file for preview and download."
)

with st.sidebar:
    st.header("Animation settings")
    color_name = st.selectbox("Wave color", list(MANIM_COLORS))
    amplitude = st.slider("Amplitude", 0.25, 2.5, 1.0, 0.05)
    frequency = st.slider("Frequency", 0.25, 4.0, 1.0, 0.05)
    rotation_rate = st.slider("Camera rotation rate", 0.05, 0.50, 0.20, 0.05)
    quality_name = st.selectbox("Output quality", list(QUALITY_OPTIONS))

scene_code = build_scene_code(
    color_constant=MANIM_COLORS[color_name],
    amplitude=amplitude,
    frequency=frequency,
    rotation_rate=rotation_rate,
)

with st.expander("Preview generated Manim source code"):
    st.code(scene_code, language="python")

if st.button("Render Manim MP4", type="primary", use_container_width=True):
    with st.spinner("Rendering the Manim scene..."):
        video_bytes, render_log = render_manim_video(
            scene_code=scene_code,
            quality_flag=QUALITY_OPTIONS[quality_name],
        )

    if video_bytes is not None:
        st.success("Manim rendering completed successfully.")
        st.video(video_bytes, format="video/mp4")
        st.download_button(
            "Download Manim MP4",
            data=video_bytes,
            file_name="StreamlitWave.mp4",
            mime="video/mp4",
            use_container_width=True,
        )
    else:
        st.error("Manim rendering failed. Open the terminal log below for the exact cause.")

    with st.expander("Manim terminal log", expanded=video_bytes is None):
        st.code(render_log, language="text")
