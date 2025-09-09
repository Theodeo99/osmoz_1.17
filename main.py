import streamlit as st
from pathlib import Path
from nbformat import read, write, NotebookNode
from nbclient import NotebookClient, CellExecutionError
from nbconvert import HTMLExporter
import tempfile
import traceback

st.set_page_config(page_title="Osmoz Notebook Runner", layout="wide")
st.title("Exécuter Osmoz_1.22.ipynb")

NB_PATH = Path("Osmoz_1.22.ipynb")

if not NB_PATH.exists():
    st.error(f"Notebook introuvable : {NB_PATH}. Placez Osmoz_1.22.ipynb à la racine du repo.")
    st.stop()

st.info("Lancement de l'exécution du notebook (nbclient). Cela peut prendre plusieurs secondes/minutes.")

# Lecture du notebook
with NB_PATH.open("r", encoding="utf-8") as f:
    nb = read(f, as_version=4)

# Si le kernel metadata n'existe pas, on force "python3"
kern_name = nb.metadata.get("kernelspec", {}).get("name", "python3")
st.write(f"Kernel demandé dans la metadata : {kern_name}")

# Exécuter en essayant d'abord le kernelspec demandé, puis fallback sur "python3"
attempts = [kern_name] if kern_name else []
if "python3" not in attempts:
    attempts.append("python3")

executed = False
errors = []
for kn in attempts:
    try:
        st.write(f"Tentative d'exécution avec kernel_name='{kn}' ...")
        client = NotebookClient(nb, timeout=600, kernel_name=kn, allow_errors=False)
        client.execute()
        executed = True
        st.success(f"Exécution terminée avec kernel '{kn}'.")
        break
    except CellExecutionError as e:
        tb = traceback.format_exc()
        errors.append((kn, str(e), tb))
        st.warning(f"Erreur d'exécution avec kernel '{kn}': {e}")
    except Exception as e:
        tb = traceback.format_exc()
        errors.append((kn, str(e), tb))
        st.warning(f"Échec avec kernel '{kn}': {e}")

if not executed:
    st.error("Impossible d'exécuter le notebook avec les kernels testés. Voir les détails ci‑dessous.")
    for kn, msg, tb in errors:
        st.subheader(f"Détails kernel: {kn}")
        st.text(msg)
        st.code(tb)
    st.stop()

# Exporter en HTML et afficher (via composant HTML)
exporter = HTMLExporter()
body, resources = exporter.from_notebook_node(nb)

# Sauvegarde locale du HTML dans le workspace (utile pour debug)
out_html = Path("osmoz_executed.html")
out_html.write_text(body, encoding="utf-8")
st.success(f"HTML généré et sauvegardé en {out_html}")

# Affichage dans Streamlit
st.subheader("Aperçu du notebook exécuté")
st.components.v1.html(body, height=800, scrolling=True)
