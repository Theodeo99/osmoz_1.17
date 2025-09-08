#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import socket
import subprocess
import webbrowser
import signal

# pywebview est optionnel (on bascule vers le navigateur si indisponible)
try:
    import webview
except Exception:
    webview = None

# --------- Paramètres à adapter ----------
NB_NAME = "Untitled17.ipynb"   # nom du notebook à lancer
PORT = 8866                    # port local pour Voilà
WINDOW_TITLE = "Osmoz"
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
# ----------------------------------------

def resource_path(*paths):
    """
    Renvoie un chemin vers une ressource empaquetée.
    - En mode PyInstaller (onefile), les fichiers add-data sont dans sys._MEIPASS.
    - En mode normal, on prend le dossier du script.
    """
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, *paths)

def is_port_open(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.25)
        return s.connect_ex((host, port)) == 0

def build_url():
    nb_abs = resource_path(Untitled17.ipynb)
    nb_base = os.path.basename(nb_abs)
    return f"http://127.0.0.1:{PORT}/voila/render/{nb_base}"

def start_voila(notebook_path: str):
    """
    Lance Voilà en sous-processus.
    On force l'écoute sur 127.0.0.1, sans ouverture de navigateur.
    """
    cmd = [
        sys.executable, "-m", "voila", notebook_path,
        "--no-browser",
        f"--port={PORT}",
        "--Voila.ip=127.0.0.1",
    ]
    # Sous Windows, éviter les fenêtres console parasites (quand packagé)
    creationflags = 0
    if os.name == "nt":
        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    return subprocess.Popen(cmd, creationflags=creationflags)

def wait_for_server(timeout=45):
    """
    Attend que le port de Voilà réponde. Retourne True si OK, False sinon.
    """
    t0 = time.time()
    while time.time() - t0 < timeout:
        if is_port_open("127.0.0.1", PORT):
            return True
        time.sleep(0.2)
    return False

def open_in_webview(url: str, on_closed):
    """
    Ouvre l'URL dans une fenêtre native via pywebview.
    Si pywebview est indisponible, fallback navigateur par défaut.
    """
    if webview is None:
        webbrowser.open(url)
        return "browser"

    win = webview.create_window(
        WINDOW_TITLE, url=url, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, resizable=True
    )
    # on_closed est appelé quand l'utilisateur ferme la fenêtre
    webview.start(on_closed, debug=False)
    return "webview"

def main():
    # Gestion Ctrl+C propre
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    nb_path = resource_path(untitled17)
    if not os.path.exists(nb_path):
        print(f"[ERREUR] Notebook introuvable: {nb_path}")
        print("Vérifiez NB_NAME ou l'option --add-data de PyInstaller.")
        sys.exit(1)

    url = build_url()
    proc = None
    try:
        proc = start_voila(nb_path)
        if not wait_for_server():
            raise RuntimeError("Voilà ne démarre pas (port bloqué ou dépendances manquantes).")

        def on_closed():
            # Ferme Voilà quand la fenêtre se ferme
            try:
                if proc and proc.poll() is None:
                    proc.terminate()
                    # Sur certaines plateformes, un kill peut être nécessaire
                    try:
                        proc.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        proc.kill()
            except Exception:
                pass

        mode = open_in_webview(url, on_closed)
        # Si on a ouvert dans le navigateur, garder Voilà en vie jusqu'à Ctrl+C
        if mode == "browser":
            print(f"Application lancée sur: {url}")
            print("Appuyez sur Ctrl+C pour quitter.")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass

    except Exception as e:
        print(f"[ERREUR] {e}")
        sys.exit(2)
    finally:
        if proc and proc.poll() is None:
            try:
                proc.terminate()
                proc.wait(timeout=2)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass

if __name__ == "__main__":
    main()
