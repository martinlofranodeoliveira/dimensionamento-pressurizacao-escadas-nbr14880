#!/usr/bin/env python3
"""Verifica a integridade dos pacotes sdist (.tar.gz) e wheel (.whl) construídos."""

import os
import sys
import tarfile
import zipfile


def main() -> int:
    raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    dist_dir = os.path.join(raiz, "dist")

    if not os.path.exists(dist_dir):
        print(f"Diretório dist não encontrado em: {dist_dir}", file=sys.stderr)
        return 1

    arquivos = os.listdir(dist_dir)
    sdists = [f for f in arquivos if f.endswith(".tar.gz")]
    wheels = [f for f in arquivos if f.endswith(".whl")]

    if not sdists:
        print("Nenhum sdist (.tar.gz) encontrado em dist/", file=sys.stderr)
        return 1
    if not wheels:
        print("Nenhum wheel (.whl) encontrado em dist/", file=sys.stderr)
        return 1

    sdist_path = os.path.join(dist_dir, sdists[0])
    wheel_path = os.path.join(dist_dir, wheels[0])

    print(f"Verificando sdist: {sdists[0]}")
    with tarfile.open(sdist_path, "r:gz") as tar:
        membros = tar.getnames()
        print(f"  Total de arquivos no sdist: {len(membros)}")
        assert any("pyproject.toml" in m for m in membros), "pyproject.toml ausente no sdist"
        assert any("LICENSE" in m for m in membros), "LICENSE ausente no sdist"

    print(f"Verificando wheel: {wheels[0]}")
    with zipfile.ZipFile(wheel_path, "r") as whl:
        membros = whl.namelist()
        print(f"  Total de arquivos no wheel: {len(membros)}")
        assert any("pressurizacao_nbr14880/__init__.py" in m for m in membros), "Código ausente no wheel"
        assert any("pressurizacao_nbr14880/py.typed" in m for m in membros), "py.typed ausente no wheel"

    print("\nArtefatos de distribuição sdist e wheel validados com sucesso!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
