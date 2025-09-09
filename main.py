# main.py
# Streamlit front-end to host/display the notebook Osmoz_1.22.ipynb in a safe way.
# - Renders the notebook statically (no execution) as HTML for reliability on Streamlit.
# - Can write a requirements.txt file into the working directory for deployment.
# - Provides simple checks and helpful messages.
#
# Usage:
#   pip install -r requirements.txt
#   streamlit run main.py
#
# This file assumes the notebook file is named exactly "Osmoz_1.22.ipynb" in the app folder.
# If the file has a different name or path, change NOTEBOOK_NAME below.

import streamlit as st
import os
import nbformat
from nbconvert import HTMLExporter
from typing import Optional

st.set_page_config(page_title="Osmoz — Notebook viewer", layout="wide")

NOTEBOOK_NAME = "Osmoz_1.22.ipynb"  # change if your notebook filename differs
REQUIREMENTS_CONTENT = """streamlit
pandas
openpyxl
chardet
reportlab
pillow
nbformat
nbconvert
jupyter-client
ipython
"""

def write_requirements(path: str = "requirements.txt", content: str = REQUIREMENTS_CONTENT) -> str:
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path

def render_notebook_static(path: str) -> Optional[str]:
    """
    Read the notebook (no execution) and convert to HTML string using nbconvert.HTMLExporter.
    Returns HTML body string or None on failure.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            nb = nbformat.read(f, as_version=4)
        exporter = HTMLExporter()
        body, resources = exporter.from_notebook_node(nb)
        return body
    except FileNotFoundError:
        return None
    except Exception as e:
        st.error(f"Erreur lors du rendu statique du notebook: {e}")
        return None

def main():
    st.title("Osmoz — Notebook viewer")
    st.markdown("Application Streamlit pour afficher statiquement le fichier notebook **Osmoz_1.22.ipynb**.")
    st.markdown(
        "Instructions rapides:\n"
        "- Si vous voulez déployer sur Streamlit Cloud ou un autre hébergeur, placez le fichier "
        f"`{NOTEBOOK_NAME}` à la racine du repo et installez les dépendances via `requirements.txt`.\n"
        "- Le rendu statique n'exécute pas le code du notebook (évite timeouts/erreurs d'exécution)."
    )

    st.divider()
    st.header("Fichiers et état")
    st.write("Working directory:", os.getcwd())
    files = sorted(os.listdir("."))
    # Display small file list
    with st.expander("Fichiers dans le répertoire (cliquer pour ouvrir)"):
        for fn in files:
            st.write("-", fn)

    nb_exists = os.path.exists(NOTEBOOK_NAME)
    st.write("Notebook détecté ?", nb_exists)
    if nb_exists:
        st.write("Taille (octets):", os.path.getsize(NOTEBOOK_NAME))

    st.divider()
    st.header("Actions utiles")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Générer requirements.txt"):
            path = write_requirements()
            st.success(f"requirements.txt créé: {path}")
            st.code(REQUIREMENTS_CONTENT, language="text")

        if st.button("Afficher le notebook (rendu statique)"):
            if not nb_exists:
                st.error(f"Notebook introuvable: {NOTEBOOK_NAME}")
            else:
                html = render_notebook_static(NOTEBOOK_NAME)
                if html:
                    # Keep a reasonable default height; allow scrolling
                    st.components.v1.html(html, height=900, scrolling=True)
                else:
                    st.error("Impossible de convertir le notebook en HTML (voir logs).")

    with col2:
        st.markdown(
            "Options avancées:\n\n"
            "- Convertir le notebook en script Python (nbconvert) et importer un main() adapté est possible,\n"
            "  mais attention: le notebook contient des widgets et du code IPython qui ne fonctionnent pas directement\n"
            "  sous Streamlit. La conversion requiert de nettoyer/remplacer les appels ipywidgets par Streamlit.\n\n"
            "- Pour convertir en .py localement:\n"
            "  jupyter nbconvert --to script Osmoz_1.22.ipynb\n\n"
            "- Si vous souhaitez que je génère un script `mon_notebook.py` adapté pour Streamlit (remplacement\n"
            "  des widgets), collez ici les cellules clefs (chargement données / génération PDF) et je le ferai."
        )

    st.divider()
    st.header("Diagnostic rapide (si la page reste vide)")
    st.markdown(
        "1) Assurez-vous d'avoir lancé `streamlit run main.py` dans le répertoire contenant `main.py` et "
        f"`{NOTEBOOK_NAME}`.\n\n"
        "2) Si vous déployez sur Streamlit Cloud: évitez d'exécuter automatiquement des tâches longues au démarrage.\n\n"
        "3) Si vous souhaitez exécuter le notebook avant d'afficher (risqué pour timeouts), je peux fournir\n"
        "   une version qui exécute le notebook avec nbconvert.ExecutePreprocessor mais cela peut échouer\n"
        "   sur les plateformes avec limites de temps ou sans certains paquets."
    )

    st.divider()
    st.caption("Si vous voulez, je peux aussi: 1) convertir automatiquement le notebook en script Streamlit-ready, "
               "ou 2) produire un main.py qui exécute le notebook (avec risques de timeout). Dites-moi votre choix.")

if __name__ == "__main__":
    main()
