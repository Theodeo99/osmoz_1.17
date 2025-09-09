#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main wrapper pour lancer le notebook Untitled17.ipynb avec Voilà / navigateur.
Adapté pour être packagé par PyInstaller.
"""

import os
import sys
import time
import webbrowser
import threading

# Nom exact du notebook dans le repo (modifié comme demandé)
NB_NAME = "Untitled17.ipynb"

# Port et URL d'ouverture
PORT = 8866
HOST = "127.0.0.1"
URL = f"http://{HOST}:{PORT}/"

def run_voila():
    """Lance voila pour servir le notebook localement."""
    try:
        # Import local pour éviter d'échouer si non installé au runtime
        import voila.app  # noqa: F401
    except Exception:
        # Si voila n'est pas disponible, on tente un fallback : ouvrir le fichier dans le navigateur
        print("voila non disponible dans l'environnement d'exécution. On ouvre le notebook dans le navigateur si possible.")
        path = os.path.abspath(NB_NAME)
        if os.path.exists(path):
            webbrowser.open("file://" + path)
        else:
            print(f"Fichier {NB_NAME} introuvable.")
        return

    # Construire la commande voila via subprocess (plus fiable pour PyInstaller)
    import subprocess
    cmd = [
        sys.executable, "-m", "voila",
        NB_NAME,
        "--no-browser",
        f"--port={PORT}",
        f"--ip={HOST}",
        "--strip_sources=False"
    ]
    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError as e:
        print("Erreur lors du lancement de voila :", e)
    except FileNotFoundError:
        print("Commande voila introuvable. Vérifiez l'installation.")

def open_browser_later(delay=1.5):
    """Ouvrir le navigateur après un court délai pour laisser voila démarrer."""
    def _open():
        time.sleep(delay)
        try:
            webbrowser.open(URL)
        except Exception:
            pass
    t = threading.Thread(target=_open, daemon=True)
    t.start()

def main():
    # Vérifications simples
    if not os.path.exists(NB_NAME):
        print(f"Erreur: le notebook '{NB_NAME}' est introuvable dans le répertoire courant: {os.getcwd()}")
        print("Liste des fichiers présents :")
        for f in sorted(os.listdir(".")):
            print("  -", f)
        sys.exit(1)

    print("Démarrage de Voilà pour :", NB_NAME)
    open_browser_later(2.0)
    run_voila()

if __name__ == "__main__":
    main()
