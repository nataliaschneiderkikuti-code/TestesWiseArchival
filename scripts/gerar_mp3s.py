"""
Gera arquivos de áudio MP3 sintéticos com tamanhos específicos para testes automatizados.
Utiliza o FFmpeg com codificador libmp3lame em taxa de bits constante (CBR 192k).
"""
from pathlib import Path
import subprocess
import shutil

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PASTA = PROJECT_ROOT / "test_data"
PASTA.mkdir(exist_ok=True)


def gerar_mp3(nome, alvo_mb, bitrate_kbps=192):
    caminho = PASTA / nome

    if not shutil.which("ffmpeg"):
        raise RuntimeError("FFmpeg não foi encontrado no PATH do sistema. Instale o FFmpeg para gerar arquivos de áudio.")

    bytes_alvo = alvo_mb * 1024 * 1024
    # Em CBR, taxa em bytes por segundo = (bitrate_kbps * 1000) / 8
    bytes_por_segundo = (bitrate_kbps * 1000) / 8
    duracao_segundos = max(1.0, bytes_alvo / bytes_por_segundo)

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=44100",
        "-t", f"{duracao_segundos:.2f}",
        "-b:a", f"{bitrate_kbps}k",
        "-c:a", "libmp3lame",
        str(caminho)
    ]

    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    tamanho_mb = caminho.stat().st_size / (1024 * 1024)
    print(f"MP3 gerado: {nome} -> {tamanho_mb:.2f} MiB (~{duracao_segundos/60:.1f} min)")
    return tamanho_mb


if __name__ == "__main__":
    print("--- Gerando áudios MP3 de teste ---")
    gerar_mp3("2mb.mp3", alvo_mb=2)
    gerar_mp3("10mb.mp3", alvo_mb=10)
    gerar_mp3("30mb.mp3", alvo_mb=30)
    print("Geração de MP3s concluída!\n")

