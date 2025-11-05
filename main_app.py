import eel
import os
import json
import subprocess
import threading
import win32gui
import ctypes
import tkinter as tk
from tkinter import filedialog
from pathlib import Path

# Caminhos base
BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"
BACKEND_DIR = BASE_DIR / "backend"
REQUESTS_FILE = FRONTEND_DIR / "requests.json"

# Inicializa EEL apontando para o frontend
eel.init(str(FRONTEND_DIR))

tk_root = None
@eel.expose
def selecionar_diretorio():
    global tk_root
    try:
        if tk_root is None:
            tk_root = tk.Tk()
            tk_root.withdraw()

        try:
            hwnd_main = win32gui.GetForegroundWindow()
        except Exception:
            hwnd_main = None

        if hwnd_main:
            try:
                tk_root.wm_attributes("-toolwindow", True)
                tk_root.wm_attributes("-topmost", True)
                tk_root.lift()
                tk_root.focus_force()
                ctypes.windll.user32.SetWindowLongW(
                    tk_root.winfo_id(),
                    -8,
                    hwnd_main
                )
            except Exception as e:
                print("Aviso: não foi possível vincular janela Tk ao app principal:", e)

        folder_selected = filedialog.askdirectory(
            parent=tk_root,
            title="Selecione um diretório de armazenamento"
        )
        print("selecionar_diretorio ->", folder_selected)
        return folder_selected if folder_selected else ""

    except Exception as e:
        print("Erro ao abrir diálogo de pasta:", e)
        return ""

@eel.expose
def atualizar_requests_json(caminho):
    """Grava o caminho escolhido no requests.json."""
    data = {"diretorio": caminho}
    print(f" Gravando no requests.json: {data}")

    with open(REQUESTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

@eel.expose
def executar_automacao():
    """Executa o script backend/accl.py."""
    try:
        script_path = BACKEND_DIR / "accl.py"
        subprocess.run(["python", str(script_path)], check=True)
        return "Automação executada com sucesso!"
    except subprocess.CalledProcessError as e:
        return f"Erro ao executar automação: {e}"

if __name__ == "__main__":
    try:
        eel.start(
            "index.html",
            port=0,  # 0 = escolhe uma porta livre automaticamente
            size=(1200, 800),
            cmdline_args=['--start-maximized']
        )
    except OSError:
        eel.start(
            "index.html",
            port=8080,
            size=(1200, 800),
            cmdline_args=['--start-maximized']
        )