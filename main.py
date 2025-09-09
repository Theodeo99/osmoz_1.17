# main.py
import streamlit as st
import subprocess
import sys
import shutil
from pathlib import Path
import tempfile
import time
import json
import os

NB_NAME = "Osmoz_1.22.ipynb"
OUT_HTML = "osmoz_executed.html"
NBCONVERT_TIMEOUT = 600  # secondes

st.set_page_config(page_title="Osmoz — Exécuter Notebook", layout="wide")
st.title("Osmoz — Exécuter Notebook (dynamique)")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown(f"- Notebook: **{NB_NAME}**")
    nb_path = Path(NB_NAME)
    if not nb_path.exists():
        st.error(f"Notebook introuvable : placez {NB_NAME} dans le même dossier que main.py.")
        st.stop()
    else:
        st.success(f"Notebook trouvé : {NB_NAME}")

    st.info("L'exécution va lancer le notebook côté serveur (code exécuté). Ne déployez pas cela sans précautions.")

with col2:
    run_now = st.button("▶️ Exécuter le notebook maintenant")
    force_reexec = st.checkbox("Forcer la ré-exécution (supprime cache HTML)", value=False)
    use_nbclient = st.checkbox("Utiliser nbclient (exécution interne Python)", value=False)

log_area = st.empty()
progress = st.empty()

def write_log(s: str, append=True):
    if append:
        prev = log_area.text_area("Logs", value="", height=300)
    # simple append strategy: print to console + update textarea (keeps last only)
    print(s)
    log_area.text_area("Logs", value=s, height=300)

def run_subprocess_nbconvert(nb: Path, out_html: str, timeout_sec: int = NBCONVERT_TIMEOUT):
    cmd = [
        sys.executable, "-m", "nbconvert",
        "--to", "html",
        "--execute",
        f"--ExecutePreprocessor.timeout={timeout_sec}",
        f"--output={out_html}",
        str(nb)
    ]
    # Use a temporary working dir so output name is predictable
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_sec + 10
        )
    except subprocess.TimeoutExpired as e:
        return False, f"TimeoutExpired: {e}"
    out = proc.stdout or ""
    err = proc.stderr or ""
    rc = proc.returncode
    return rc == 0, out + "\n" + err

def try_install_ipykernel_as_python3():
    # Attempt to install ipykernel and register kernel named "python3"
    cmds = [
        [sys.executable, "-m", "pip", "install", "--upgrade", "ipykernel"],
        [sys.executable, "-m", "ipykernel", "install", "--user", "--name", "python3", "--display-name", "python3"]
    ]
    logs = []
    for c in cmds:
        try:
            p = subprocess.run(c, capture_output=True, text=True, timeout=300)
            logs.append(f"$ {' '.join(c)}\n--- rc={p.returncode}\n{p.stdout}\n{p.stderr}\n")
            if p.returncode != 0:
                return False, "\n".join..(stopped)
