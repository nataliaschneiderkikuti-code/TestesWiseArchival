import sqlite3
from pathlib import Path
from datetime import datetime


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "reports" / "resultados.db"


def criar_banco():
    DB_PATH.parent.mkdir(exist_ok=True)

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resultados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_hora TEXT NOT NULL,
            arquivo TEXT NOT NULL,
            tipo_arquivo TEXT NOT NULL,
            tamanho_bytes INTEGER,
            tamanho_mb REAL,
            tempo_upload REAL,
            tempo_processamento_real REAL,
            tempo_interface REAL,
            diferenca REAL,
            diferenca_absoluta REAL,
            reloads INTEGER,
            status TEXT NOT NULL,
            mensagem TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS etapas_teste (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_hora TEXT NOT NULL,
            etapa TEXT NOT NULL,
            status TEXT NOT NULL,
            mensagem TEXT
        )
    """)

    conn.commit()
    conn.close()

def registrar_etapa(etapa, status, mensagem=""):
    criar_banco()

    conn = sqlite3.connect(DB_PATH)

    try:
        conn.execute("""
            INSERT INTO etapas_teste (
                data_hora,
                etapa,
                status,
                mensagem
            )
            VALUES (?, ?, ?, ?)
        """, (
            datetime.now().isoformat(timespec="seconds"),
            etapa,
            status,
            mensagem
        ))

        conn.commit()

    finally:
        conn.close()

def salvar_resultado(
    arquivo,
    tipo_arquivo,
    tamanho_bytes,
    tempo_upload,
    tempo_processamento_real,
    tempo_interface,
    reloads,
    status,
    mensagem=""
):
    criar_banco()

    tamanho_mb = (tamanho_bytes / (1024 * 1024)) if tamanho_bytes is not None else None

    if tempo_processamento_real is not None and tempo_interface is not None:
        diferenca = tempo_processamento_real - tempo_interface
        diferenca_absoluta = abs(diferenca)
    else:
        diferenca = None
        diferenca_absoluta = None

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO resultados (
            data_hora,
            arquivo,
            tipo_arquivo,
            tamanho_bytes,
            tamanho_mb,
            tempo_upload,
            tempo_processamento_real,
            tempo_interface,
            diferenca,
            diferenca_absoluta,
            reloads,
            status,
            mensagem
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().isoformat(timespec="seconds"),
        arquivo,
        tipo_arquivo,
        tamanho_bytes,
        tamanho_mb,
        tempo_upload,
        tempo_processamento_real,
        tempo_interface,
        diferenca,
        diferenca_absoluta,
        reloads,
        status,
        mensagem
    ))

    conn.commit()
    conn.close()
