# main.py (rendu statique)
import streamlit as st
import nbformat
from nbconvert import HTMLExporter

st.set_page_config(page_title="Osmoz", layout="wide")
st.title("Osmoz_1.22.ipynb (rendu statique)")

path = "Osmoz_1.22.ipynb"
try:
    with open(path, "r", encoding="utf-8") as f:
        nb = nbformat.read(f, as_version=4)
    html_exporter = HTMLExporter()
    body, _ = html_exporter.from_notebook_node(nb)
    st.components.v1.html(body, height=900, scrolling=True)
except FileNotFoundError:
    st.error(f"Notebook introuvable: {path}")
except Exception as e:
    st.error(f"Erreur lors du rendu statique: {e}")
