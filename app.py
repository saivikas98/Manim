import streamlit as st
import subprocess
import os

st.set_page_config(page_title="Manim Generator", page_icon="🎥")

st.title("Interactive Manim Generator")
st.write("Generate a customized 3D wave animation.")

color_choice = st.selectbox("Select Wave Color", ["BLUE", "RED", "GREEN", "PURPLE"])

manim_code = f'''
from manim import *

class StreamlitWave(ThreeDScene):
    def construct(self):
        axes = ThreeDAxes()
        self.set_camera_orientation(phi=75 * DEGREES, theta=30 * DEGREES)
        
        wave = axes.plot_parametric_curve(
            lambda t: np.array([t, np.sin(t), 0]), 
            t_range=[-TAU, TAU], 
            color={color_choice}
        )
        
        self.play(Create(axes), run_time=1)
        self.play(Create(wave), run_time=2)
        self.begin_ambient_camera_rotation(rate=0.2)
        self.wait(2)
        self.stop_ambient_camera_rotation()
'''

if st.button("Render Animation"):
    with st.spinner("Rendering video... this may take a moment."):
        with open("temp_scene.py", "w") as f:
            f.write(manim_code)
        
        subprocess.run(
            ["manim", "temp_scene.py", "StreamlitWave", "-ql", "--media_dir", "./media"],
            capture_output=True
        )
        
        video_path = "./media/videos/temp_scene/480p15/StreamlitWave.mp4"
        
        if os.path.exists(video_path):
            st.video(video_path)
            st.success("Render complete!")
        else:
            st.error("Rendering failed. Check your Manim syntax or local FFmpeg installation.")
