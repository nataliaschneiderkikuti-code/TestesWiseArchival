"""
Script unificado para geração de todos os arquivos de teste automatizados:
PDF, PNG, MP3 e MP4 com diferentes perfis de tamanho (leve, médio, pesado).

Uso:
    python scripts/gerar_todos_arquivos.py           # Gera todos os formatos recomendados
    python scripts/gerar_todos_arquivos.py --png     # Gera apenas PNGs
    python scripts/gerar_todos_arquivos.py --mp3     # Gera apenas MP3s
    python scripts/gerar_todos_arquivos.py --mp4     # Gera apenas MP4s
    python scripts/gerar_todos_arquivos.py --pdf     # Gera apenas PDFs
"""
import sys
import argparse
from pathlib import Path

# Adiciona o diretório do script ao sys.path para importação
SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from gerar_pdfs import gerar_pdf_com_tamanho_alvo
from gerar_pngs import gerar_png
from gerar_mp3s import gerar_mp3
from gerar_mp4s import gerar_mp4


def gerar_lote_pdf():
    print("\n[1/4] === Gerando PDFs (Documentos) ===")
    gerar_pdf_com_tamanho_alvo("2mb.pdf", alvo_mb=2)
    gerar_pdf_com_tamanho_alvo("10mb.pdf", alvo_mb=10)
    gerar_pdf_com_tamanho_alvo("50mb.pdf", alvo_mb=50)


def gerar_lote_png():
    print("\n[2/4] === Gerando PNGs (Imagens) ===")
    gerar_png("2mb.png", alvo_mb=2)
    gerar_png("5mb.png", alvo_mb=5)
    gerar_png("20mb.png", alvo_mb=20)


def gerar_lote_mp3():
    print("\n[3/4] === Gerando MP3s (Áudios) ===")
    gerar_mp3("2mb.mp3", alvo_mb=2)
    gerar_mp3("10mb.mp3", alvo_mb=10)
    gerar_mp3("30mb.mp3", alvo_mb=30)


def gerar_lote_mp4():
    print("\n[4/4] === Gerando MP4s (Vídeos) ===")
    gerar_mp4("5mb.mp4", alvo_mb=5)
    gerar_mp4("25mb.mp4", alvo_mb=25)
    gerar_mp4("50mb.mp4", alvo_mb=50)


def main():
    parser = argparse.ArgumentParser(
        description="Gerador de arquivos de teste para Wise Archival."
    )
    parser.add_argument("--pdf", action="store_true", help="Gera apenas PDFs")
    parser.add_argument("--png", action="store_true", help="Gera apenas imagens PNG")
    parser.add_argument("--mp3", action="store_true", help="Gera apenas áudios MP3")
    parser.add_argument("--mp4", action="store_true", help="Gera apenas vídeos MP4")

    args = parser.parse_args()

    gerou_algo = False

    if args.pdf:
        gerar_lote_pdf()
        gerou_algo = True
    if args.png:
        gerar_lote_png()
        gerou_algo = True
    if args.mp3:
        gerar_lote_mp3()
        gerou_algo = True
    if args.mp4:
        gerar_lote_mp4()
        gerou_algo = True

    # Se nenhum filtro específico foi passado, gera todos
    if not gerou_algo:
        print("Iniciando geração de todos os arquivos de teste padrão...")
        gerar_lote_pdf()
        gerar_lote_png()
        gerar_lote_mp3()
        gerar_lote_mp4()

    print("\nTodos os arquivos solicitados estão prontos em 'test_data/'!")


if __name__ == "__main__":
    main()

