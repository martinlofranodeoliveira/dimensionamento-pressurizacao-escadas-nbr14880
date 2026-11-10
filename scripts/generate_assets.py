#!/usr/bin/env python3
"""Gera o painel vetorial SVG e renderiza a imagem PNG de alta resolução."""

import os
import subprocess
import sys

# Inserir src no sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from pressurizacao_nbr14880.calculator import dimensionar_pressurizacao_escada
from pressurizacao_nbr14880.codecs import carregar_dados_edificacao_json
from pressurizacao_nbr14880.svg_generator import gerar_painel_svg


def main() -> int:
    raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    exemplo_json = os.path.join(raiz, "examples", "edificio_residencial_torre_alta.json")
    docs_dir = os.path.join(raiz, "docs")
    os.makedirs(docs_dir, exist_ok=True)

    svg_path = os.path.join(docs_dir, "painel_exemplo.svg")
    png_path = os.path.join(docs_dir, "exemplo.png")

    with open(exemplo_json, "r", encoding="utf-8") as f:
        dados = carregar_dados_edificacao_json(f.read())

    res = dimensionar_pressurizacao_escada(dados)
    svg_conteudo = gerar_painel_svg(res)

    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_conteudo)
    print(f"[OK] SVG gerado em: {svg_path}")

    # Renderizar PNG via headless Chrome/Chromium
    chrome_cmd = [
        "google-chrome",
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--window-size=1440,900",
        f"--screenshot={png_path}",
        svg_path,
    ]
    try:
        subprocess.run(chrome_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        tamanho = os.path.getsize(png_path)
        print(f"[OK] PNG renderizado com sucesso: {png_path} ({tamanho} bytes)")
    except Exception as err:
        print(f"[AVISO] Não foi possível renderizar via Chrome: {err}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
