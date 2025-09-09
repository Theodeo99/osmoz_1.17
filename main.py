# main.py - rend le notebook Osmoz_1.22.ipynb
import streamlit as st
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from nbconvert import HTMLExporter

st.set_page_config(page_title="Osmoz", layout="wide")
st.title("Osmoz_1.22.ipynb")

NOTEBOOK_PATH = "Osmoz_1.22.ipynb"  # <-- chemin/nom exact dans le repo

try:
    with open(NOTEBOOK_PATH, "r", encoding="utf-8") as f:
        nb = nbformat.read(f, as_version=4)

    ep = ExecutePreprocessor(timeout=300, kernel_name="python3")
    ep.preprocess(nb, {"metadata": {"path": "./"}})

    html_exporter = HTMLExporter()
    (body, resources) = html_exporter.from_notebook_node(nb)

    st.components.v1.html(body, height=900, scrolling=True)

except FileNotFoundError:
    st.error(f"Notebook introuvable : {NOTEBOOK_PATH}")
except Exception as e:
    st.error(f"Erreur lors de l'exécution/affichage du notebook : {e}")
