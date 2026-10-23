"""
Gera arquivos de vídeo MP4 sintéticos com tamanhos específicos para testes automatizados.
Utiliza o FFmpeg com codificador H.264 e áudio AAC em taxa de bits controlada.
"""
from pathlib import Path
import subprocess
import shutil

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PASTA = PROJECT_ROOT / "test_data"
PASTA.mkdir(exist_ok=True)


def gerar_mp4(nome, alvo_mb, duracao_segundos=None):
    caminho = PASTA / nome

    if not shutil.which("ffmpeg"):
        raise RuntimeError("FFmpeg não foi encontrado no PATH do sistema. Instale o FFmpeg para gerar arquivos de vídeo.")

    # Duração calculada para manter um fluxo realista de vídeo (~5 Mbps)
    if duracao_segundos is None:
        duracao_segundos = max(5.0, alvo_mb * 1.6)

    bytes_alvo = alvo_mb * 1024 * 1024
    taxa_total_bps = (bytes_alvo * 8) / duracao_segundos
    taxa_audio_bps = 128_000
    taxa_video_bps = max(500_000, int(taxa_total_bps - taxa_audio_bps))
    bitrate_v_k = int(taxa_video_bps / 1000)

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "mandelbrot=size=1280x720:rate=30",
        "-f", "lavfi", "-i", "sine=frequency=1000:sample_rate=44100",
        "-t", f"{duracao_segundos:.2f}",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-b:v", f"{bitrate_v_k}k",
        "-minrate", f"{bitrate_v_k}k",
        "-maxrate", f"{bitrate_v_k}k",
        "-bufsize", f"{bitrate_v_k}k",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "128k",
        str(caminho)
    ]

    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    tamanho_mb = caminho.stat().st_size / (1024 * 1024)
    print(f"MP4 gerado: {nome} -> {tamanho_mb:.2f} MiB (~{duracao_segundos:.1f}s, {bitrate_v_k} kbps)")
    return tamanho_mb


if __name__ == "__main__":
    print("--- Gerando vídeos MP4 de teste ---")
    gerar_mp4("5mb.mp4", alvo_mb=5)
    gerar_mp4("25mb.mp4", alvo_mb=25)
    gerar_mp4("50mb.mp4", alvo_mb=50)
    print("Geração de MP4s concluída!\n")

