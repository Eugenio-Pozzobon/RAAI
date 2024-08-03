import streamlit as st

# load readme.md and display

readme = open("README.md", "r").read()
st.markdown(readme)