"""
Gera imagens PNG sintéticas com tamanhos específicos para testes automatizados.
Utiliza a biblioteca Pillow (PIL) com ruído pseudo-aleatório para atingir
o tamanho alvo com rapidez e precisão.
"""
from pathlib import Path
import math
import os
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PASTA = PROJECT_ROOT / "test_data"
PASTA.mkdir(exist_ok=True)


def gerar_png(nome, alvo_mb):
    caminho = PASTA / nome
    bytes_alvo = int(alvo_mb * 1024 * 1024)

    # Cada pixel RGB ocupa 3 bytes. Com compress_level=1 em dados de alta entropia,
    # há um fator de ajuste de ~1.054 devido a filtros de scanline e cabeçalhos PNG.
    pixels_total = int((bytes_alvo / 1.054) / 3)
    largura = max(10, int(math.isqrt(pixels_total)))
    altura = max(10, pixels_total // largura)

    dados = os.urandom(largura * altura * 3)
    imagem = Image.frombytes("RGB", (largura, altura), dados)
    imagem.save(caminho, format="PNG", compress_level=1)

    tamanho_mb = caminho.stat().st_size / (1024 * 1024)
    print(f"PNG gerado: {nome} -> {tamanho_mb:.2f} MiB ({largura}x{altura})")
    return tamanho_mb


if __name__ == "__main__":
    print("--- Gerando imagens PNG de teste ---")
    gerar_png("2mb.png", alvo_mb=2)
    gerar_png("5mb.png", alvo_mb=5)
    gerar_png("20mb.png", alvo_mb=20)
    print("Geração de PNGs concluída!\n")

