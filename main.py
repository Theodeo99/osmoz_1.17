#!/usr/bin/env python3
# main.py — Streamlit app to execute Osmoz_1.22.ipynb with helpful kernel checks & diagnostics
# Python 3.12 compatible

import streamlit as st
import subprocess
import shutil
import json
from pathlib import Path
import time
import tempfile
import sys
import os

st.set_page_config(page_title="Osmoz — Exécuter Notebook", layout="wide")
NB_NAME = "Osmoz_1.22.ipynb"
OUT_BASENAME = "osmoz_executed"
OUT_HTML = f"{OUT_BASENAME}.html"
NBCONVERT_TIMEOUT = 600  # secondes

st.title("Osmoz — Exécuter le notebook (nbconvert)")
st.markdown(
    "Cette app exécute le notebook côté serveur avec `jupyter nbconvert --to html --execute` "
    "et affiche le rendu HTML. L'exécution lance un kernel Jupyter — il faut qu'un kernelspec "
    "existante (nommé `python3` ou autre) soit disponible."
)

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Fichier notebook")
    nb_path = Path(NB_NAME)
    if nb_path.exists():
        st.success(f"Notebook trouvé : {NB_NAME}")
        st.markdown(f"- Taille : {nb_path.stat().st_size} bytes")
    else:
        st.error(f"Notebook introuvable : {NB_NAME} — placez ce fichier dans le même dossier que main.py")
        st.stop()

with col2:
    st.subheader("Options")
    force = st.checkbox("Forcer ré-exécution (supprime le cache HTML)", value=False)
    timeout = st.number_input("Timeout (s) nbconvert", value=NBCONVERT_TIMEOUT, min_value=30, max_value=3600, step=30)
    do_install_kernel = st.button("Installer ipykernel & enregistrer kernel 'python3' (optionnel)")

log_area = st.empty()
progress = st.progress(0)

def run_cmd(cmd, timeout=None, env=None):
    """Run cmd list, return (returncode, stdout+stderr)."""
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env)
        out = (proc.stdout or "") + (proc.stderr or "")
        return proc.returncode, out
    except subprocess.TimeoutExpired as e:
        return -1, f"TimeoutExpired: {e}"
    except Exception as e:
        return -1, f"Exception: {e}"

def kernelspecs_json():
    rc, out = run_cmd(["jupyter", "kernelspec", "list", "--json"], timeout=10)
    if rc != 0:
        return {}
    try:
        return json.loads(out).get("kernelspecs", {})
    except Exception:
        return {}

def kernel_exists(name="python3"):
    ks = kernelspecs_json()
    return name in ks

def try_install_ipykernel():
    """Attempt to pip install ipykernel in the current interpreter and register a kernelspec named 'python3'."""
    log_area.markdown("➡️ Tentative d'installation de ipykernel et enregistrement du kernel 'python3'...")
    progress.progress(5)
    python_exec = sys.executable
    # pip install ipykernel
    rc, out = run_cmd([python_exec, "-m", "pip", "install", "--upgrade", "pip", "ipykernel"], timeout=600)
    log_area.code(out)
    progress.progress(30)
    if rc != 0:
        st.error("Échec de l'installation via pip. Voir logs ci-dessus.")
        return False
    # register kernel
    rc2, out2 = run_cmd([python_exec, "-m", "ipykernel", "install", "--user", "--name", "python3", "--display-name", "python3"], timeout=60)
    log_area.code(out2)
    progress.progress(70)
    if rc2 != 0:
        st.error("Échec de l'enregistrement du kernel. Voir logs ci-dessus.")
        return False
    progress.progress(100)
    st.success("ipykernel installé et kernel 'python3' enregistré (si la commande a réussi). Relancez l'exécution.")
    return True

if do_install_kernel:
    try_install_ipykernel()

st.markdown("---")
st.subheader("Vérification kernelspecs disponibles")
ks = kernelspecs_json()
if not ks:
    st.warning("Impossible de lister les kernelspecs via `jupyter kernelspec list --json`. La commande peut manquer ou échouer.")
else:
    ks_list_md = "\n".join(f"- **{k}** → {v.get('resource_dir')}" for k, v in ks.items())
    st.markdown("Kernelspecs détectés :\n" + ks_list_md)

preferred_kernel = st.text_input("Nom du kernel à utiliser pour l'exécution (metadata du notebook)", value="python3")
st.caption("Le kernel demandé doit exister dans la liste ci‑dessus. Par défaut `python3`.")

st.markdown("---")
run_button = st.button("▶️ Exécuter le notebook maintenant (nbconvert)")

def prepare_output_names(basename):
    # nbconvert --output argument will be used without extension; ensure path is safe
    return basename

def execute_notebook(nb_file: str, out_basename: str, kernel_name: str, timeout:int):
    out_html_path = Path(f"{out_basename}.html")
    # remove cached html if forcing
    if force and out_html_path.exists():
        try:
            out_html_path.unlink()
        except Exception:
            pass

    # Build nbconvert command
    # Use --output <basename> and --ExecutePreprocessor.kernel_name=<kernel>
    cmd = [
        "jupyter", "nbconvert",
        f"--ExecutePreprocessor.timeout={timeout}",
        "--to", "html",
        "--output", out_basename,
        "--ExecutePreprocessor.kernel_name=" + kernel_name,
        "--execute", nb_file
    ]
    log_area.markdown("Commande lancée : `" + " ".join(cmd) + "`")
    progress.progress(5)
    start = time.time()
    rc, out = run_cmd(cmd, timeout=timeout + 30)
    elapsed = time.time() - start
    progress.progress(90)
    if rc == 0:
        progress.progress(100)
        log_area.success(f"Exécution terminée en {int(elapsed)}s — rendu HTML généré : {out_html_path}")
        return True, out_html_path, out
    else:
        log_area.error(f"Erreur nbconvert (rc={rc}) — durée {int(elapsed)}s")
        log_area.code(out)
        return False, out_html_path, out

if run_button:
    # quick check: does requested kernel exist?
    if not kernel_exists(preferred_kernel):
        st.error(f"Le kernel '{preferred_kernel}' n'existe pas (nbconvert renverra NoSuchKernel).")
        st.info("Si vous souhaitez que l'app tente d'installer ipykernel et enregistrer un kernel 'python3', utilisez le bouton 'Installer ipykernel...' dans Options.")
    else:
        ok, html_path, nbconvert_log = execute_notebook(str(nb_path), prepare_output_names(OUT_BASENAME), preferred_kernel, int(timeout))
        if ok and html_path.exists():
            try:
                html_text = html_path.read_text(encoding="utf-8", errors="ignore")
                st.markdown("---")
                st.success(f"Affichage du rendu HTML : {html_path.name}")
                # embed rendered HTML (beware of size). height adjustable.
                st.components.v1.html(html_text, height=900, scrolling=True)
            except Exception as e:
                st.error(f"Impossible de lire/afficher {html_path}: {e}")
        else:
            st.error("L'exécution a échoué. Consultez les logs ci-dessus. Voir conseils ci‑dessous.")

st.markdown("---")
st.subheader("Conseils & dépannage rapide")
st.markdown(
    "- Si vous obtenez `No such kernel named python3` : en général il suffit d'installer ipykernel dans l'environnement utilisé par Streamlit et d'enregistrer le kernelspec :\n"
    "  1) pip install ipykernel\n"
    "  2) python -m ipykernel install --user --name python3 --display-name \"python3\"\n"
    "- Si `jupyter` n'est pas trouvé : installez `notebook`/`jupyter` (ex. pip install notebook nbconvert) et assurez-vous que `jupyter` est dans le PATH utilisé par Streamlit.\n"
    "- Si votre notebook dépend de paquets (pandas, reportlab, pillow, openpyxl, chardet, ipywidgets, ...) ajoutez-les au requirements.txt ou installez-les dans l'environnement avant d'exécuter.\n"
    "- Limitez le timeout si l'exécution prend trop longtemps, ou augmentez `timeout` dans Options si nécessaire."
)

st.markdown("---")
st.caption("Attention : exécuter un notebook côté serveur exécute tout le code présent dans le fichier (accès disque, réseau). Ne lancez pas de notebooks non vérifiés sur des serveurs publics.")
