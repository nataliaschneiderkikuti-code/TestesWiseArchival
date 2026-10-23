from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image
import random
import io
import math

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PASTA = PROJECT_ROOT / "test_data"
PASTA.mkdir(exist_ok=True)


def gerar_pdf(nome, paginas, incluir_imagens=False, qualidade=90):
    caminho = PASTA / nome
    pdf = canvas.Canvas(str(caminho), pagesize=A4)
    largura, altura = A4

    for numero in range(paginas):
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(50, altura - 60, f"Documento de teste - Página {numero + 1}")

        pdf.setFont("Helvetica", 11)
        for linha in range(25):
            texto = (
                f"Conteúdo sintético para teste automatizado. "
                f"Registro {numero + 1}-{linha + 1}. "
                f"Texto fictício sem dados pessoais."
            )
            pdf.drawString(50, altura - 100 - linha * 20, texto[:100])

        if incluir_imagens:
            imagem = Image.new("RGB", (500, 700))
            pixels = [
                (random.randrange(256), random.randrange(256), random.randrange(256))
                for _ in range(500 * 700)
            ]
            imagem.putdata(pixels)

            buffer = io.BytesIO()
            imagem.save(buffer, format="JPEG", quality=qualidade)
            buffer.seek(0)

            pdf.drawImage(ImageReader(buffer), 50, 50, width=250, height=300)

        pdf.showPage()

    pdf.save()
    tamanho_mb = caminho.stat().st_size / (1024 * 1024)
    print(f"{nome}: {tamanho_mb:.2f} MiB ({paginas} páginas)")
    return tamanho_mb


def gerar_pdf_com_tamanho_alvo(nome, alvo_mb, incluir_imagens=True,
                                qualidade=90, tolerancia=0.05):
    """Ajusta o número de páginas iterativamente até aproximar do alvo."""
    # Estimativa inicial baseada em ~0.382 MiB/página (com imagens)
    if incluir_imagens:
        paginas = max(1, int(alvo_mb / 0.382))
    else:
        paginas = max(1, int(alvo_mb / 0.001))

    for _ in range(8):  # até 8 tentativas
        tamanho = gerar_pdf(nome, paginas, incluir_imagens, qualidade)
        erro = abs(tamanho - alvo_mb) / alvo_mb

        if erro <= tolerancia:
            print(f"  → Alvo atingido: {alvo_mb} MiB\n")
            return

        # Ajusta proporcionalmente ao erro
        fator = alvo_mb / tamanho if tamanho > 0 else 1
        paginas = max(1, int(round(paginas * fator)))

    print(f"  → Melhor aproximação possível para {alvo_mb} MiB\n")


if __name__ == "__main__":
    # Você pode mudar os tamanhos dos pdfs mudando o alvo_mb
    gerar_pdf_com_tamanho_alvo("2mb.pdf", alvo_mb=2) 
    gerar_pdf_com_tamanho_alvo("10mb.pdf", alvo_mb=10)
    gerar_pdf_com_tamanho_alvo("50mb.pdf", alvo_mb=50)