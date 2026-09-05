# RLF

Jogo feito em Python com Pygame.

## Requisitos

- Windows
- uv instalado

## Como rodar no Python

```powershell
uv python install 3.12
uv venv --python 3.12 .venv
uv pip install --python .\.venv\Scripts\python.exe -r requirements.txt
.\.venv\Scripts\python.exe .\game\python\joguinhoonline.py
```

## Como gerar o EXE

```powershell
.\scripts\build_exe.ps1
```

O executavel fica em:

```text
dist\RLF.exe
```

## Estrutura

```text
game/python/joguinhoonline.py  Jogo principal
game/python/fonts/            Fontes usadas na interface
scripts/build_exe.ps1         Script para gerar o .exe
requirements.txt              Dependencias do projeto
```

## Para postar no GitHub

Suba o codigo-fonte, as fontes, o `README.md`, o `requirements.txt` e a pasta `scripts`.

Nao precisa subir `.venv`, `build`, `dist`, `__pycache__` nem o `.exe`; esses arquivos sao gerados localmente.
