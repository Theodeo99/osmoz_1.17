# affiche_nom.py (intégrer dans mon_notebook.py ou appeler depuis main.py)
import streamlit as st

def main():
    st.set_page_config(page_title="Osmoz", layout="wide")
    st.title("Osmoz_1.22.ipynb")  # <-- affiche exactement ce texte
    st.caption("Notebook source : Osmoz_1.22.ipynb")
