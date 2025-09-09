# main.py
import streamlit as st
import subprocess
import shutil
import os
from pathlib import Path
import time

st.set_page_config(page_title="Osmoz — Exécuter Notebook", layout="wide")

NB_NAME = "Osmoz_1.22.ipynb"
OUT_HTML = "osmoz_executed.html"
NBCONVERT_TIMEOUT = 600  # secondes, ajustez si nécessaire

st.title("Osmoz — Notebook dynamique")
st.markdown(f"Notebook: **{NB_NAME}**")

col1, col2, col3 = st.columns([1,1,2])

with col1:
    if not Path(NB_NAME).exists():
        st.error(f"Notebook introuvable : {NB_NAME} — placez le fichier dans le même dossier que main.py.")
    else:
        st.success(f"Notebook trouvé : {NB_NAME}")

with col2:
    run_now = st.button("▶️ Exécuter le notebook maintenant")
    force_rerun = st.checkbox("Forcer la ré-exécution (supprime le cache HTML)", value=False)

with col3:
    st.write("Options")
    st.write(f"- Timeout nbconvert : {NBCONVERT_TIMEOUT} s")
    st.write("- L’exécution se fait côté serveur (backend).")

def available_cmd(cmd):
    return shutil.which(cmd) is not None

def run_nbconvert_execute(nb_path: str, out_html: str, timeout: int = 600):
    """
    Utilise `jupyter nbconvert --to html --execute` en sous-processus.
    Retourne (success: bool, stdout+stderr text).
    """
    # commande : nbconvert --ExecutePreprocessor.timeout=<timeout> --to html --output <out> --execute <notebook>
    cmd = [
        "jupyter", "nbconvert",
        "--ExecutePreprocessor.timeout={}".format(timeout),
        "--to", "html",
        "--output", out_html,  # nbconvert ajoutera .html si besoin
        "--execute",
        nb_path
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 30)
        out = proc.stdout + "\n" + proc.stderr
        return (proc.returncode == 0), out
    except subprocess.TimeoutExpired as e:
        return False, f"TimeoutExpired: {e}"
    except Exception as e:
        return False, f"Exception: {e}"

def html_path_from_nbconvert_output(base_output_name: str) -> str:
    # nbconvert ajoute .html
    if not base_output_name.lower().endswith(".html"):
        return base_output_name + ".html"
    return base_output_name

# show cached HTML if exists
html_file = Path(html_path_from_nbconvert_output(OUT_HTML))

if html_file.exists() and not force_rerun:
    st.info(f"Affichage du rendu exécuté précédemment : {html_file.name}")
    with open(html_file, "r", encoding="utf-8") as f:
        html = f.read()
    st.components.v1.html(html, height=900, scrolling=True)
else:
    if html_file.exists() and force_rerun:
        try:
            html_file.unlink()
            st.write("Cache HTML supprimé.")
        except Exception as e:
            st.warning(f"Impossible de supprimer {html_file}: {e}")

    if run_now:
        if not available_cmd("jupyter"):
            st.error("La commande 'jupyter' n'est pas disponible sur le serveur. Installez jupyter/nbconvert (voir requirements.txt).")
        elif not Path(NB_NAME).exists():
            st.error(f"Notebook introuvable : {NB_NAME}")
        else:
            st.info("Lancement de l'exécution du notebook (nbconvert). Cela peut prendre du temps...")
            progress = st.progress(0)
            status = st.empty()
            t0 = time.time()
            # exécution
            success, output = run_nbconvert_execute(NB_NAME, OUT_HTML, timeout=NBCONVERT_TIMEOUT)
            elapsed = time.time() - t0
            if success:
                progress.progress(100)
                status.success(f"Exécution terminée en ~{int(elapsed)} s. Rendu HTML créé : {html_file.name}")
                try:
                    with open(html_file, "r", encoding="utf-8") as f:
                        html = f.read()
                    st.components.v1.html(html, height=900, scrolling=True)
                except Exception as e:
                    st.error(f"Erreur lecture HTML produit : {e}")
            else:
                status.error(f"Échec d'exécution (voir logs ci-dessous). Durée écoulée : ~{int(elapsed)} s")
                st.code(output)
    else:
        st.warning("Aucun rendu disponible. Cliquez sur 'Exécuter le notebook maintenant' pour lancer l'exécution.")
