"""
gui_main.py

Ponto de entrada do Translate VN em modo GUI (desktop, via
pywebview). O main.py original (CLI) continua existindo e
funcionando exatamente como antes -- este e' um segundo ponto de
entrada, para quem preferir a interface grafica.

Para rodar em modo desenvolvimento:
    python gui_main.py

Para gerar o .exe da GUI, veja build_gui.bat.
"""

import sys
import os
import webview

from gui_api import Api, attach_gui_log_handler


def resource_path(relative_path: str) -> str:
    """Resolve caminho de recursos (ui/index.html) tanto rodando
    via 'python gui_main.py' quanto congelado em .exe (onefile),
    onde os arquivos de dados ficam em sys._MEIPASS."""

    base_path = getattr(sys, "_MEIPASS", None)

    if base_path is None:
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, relative_path)


def main():

    api = Api()

    window = webview.create_window(
        "Translate VN",
        resource_path(os.path.join("ui", "index.html")),
        js_api=api,
        width=1180,
        height=760,
        min_size=(860, 600)
    )

    # O handler de log e o push de progresso da Api precisam da
    # instancia da janela, que so' existe depois do create_window
    # acima -- por isso get_window e' uma funcao (lazy), nao a
    # janela direto.
    attach_gui_log_handler(lambda: window)
    api.set_window_getter(lambda: window)

    webview.start()


if __name__ == "__main__":
    main()