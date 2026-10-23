import time
from pathlib import Path

from playwright.sync_api import expect

from pages.login_page import LoginPage
from pages.colecoes_page import ColecoesPage
from pages.processos_page import ProcessosPage
from utils.database import salvar_resultado, registrar_etapa

import uuid
from datetime import datetime

PASTA_TESTES = Path("test_data")
EXTENSOES_SUPORTADAS = {".pdf", ".png", ".mp3", ".mp4"}  # ajuste se quiser
TAM_PREFIXO = 18


def formatar_tamanho(tamanho_bytes):
    mb = tamanho_bytes / (1024 * 1024)
    if mb >= 1:
        return f"{round(mb)}MB"
    return f"{max(1, round(tamanho_bytes / 1024))}KB"


def descobrir_casos(pasta=PASTA_TESTES, extensoes=EXTENSOES_SUPORTADAS):
    pasta = Path(pasta)

    if not pasta.is_dir():
        raise FileNotFoundError(f"Pasta de testes não encontrada: {pasta}")

    arquivos = [
        a for a in pasta.iterdir()
        if a.is_file() and a.suffix.lower() in extensoes
    ]

    if not arquivos:
        raise FileNotFoundError(
            f"Nenhum arquivo {sorted(extensoes)} encontrado em {pasta}"
        )

    if len(arquivos) > 999:
        raise ValueError("Há mais de 999 arquivos; aumente o índice do prefixo.")

    # Ordena por tipo e, dentro do tipo, do menor para o maior
    arquivos.sort(key=lambda a: (a.suffix.lower(), a.stat().st_size, a.name))

    run_id = uuid.uuid4().hex[:6]
    casos = []

    for indice, arquivo in enumerate(arquivos, start=1):
        tipo = arquivo.suffix.lstrip(".").upper()
        prefixo = f"AT-{run_id}-{indice:03d}-{tipo[:4].ljust(4, '_')}"
        assert len(prefixo) == TAM_PREFIXO

        casos.append({
            "arquivo": str(arquivo),
            "tipo": tipo,
            "tamanho": formatar_tamanho(arquivo.stat().st_size),
            "prefixo": prefixo,
        })

    return casos

# Defina como False para pular a etapa de exclusão (processos e coleção)
EXECUTAR_LIMPEZA = True


def executar_etapa(nome_etapa, funcao, *args, **kwargs):
    try:
        resultado = funcao(*args, **kwargs)

    except Exception as erro:
        registrar_etapa(
            etapa=nome_etapa,
            status="FALHA",
            mensagem=f"{type(erro).__name__}: {erro}"
        )
        raise

    else:
        registrar_etapa(
            etapa=nome_etapa,
            status="SUCESSO",
            mensagem="Etapa concluída."
        )
        return resultado


def aguardar_processamento(page, processos, titulo, prefixo=None):
    quantidade_reloads = 0
    termo_busca = prefixo if prefixo else titulo[:18]

    for tentativa in range(1, 6):
        try:
            card = processos.obter_card_processo(termo_busca)
            expect(card).to_be_visible(timeout=15000)

            expect(
                card.get_by_text("Processando...", exact=True)
            ).to_be_hidden(timeout=120000)

        except Exception as erro:
            if tentativa == 5:
                raise

            quantidade_reloads += 1

            print(
                f"[RELOAD] {titulo}: tentativa {tentativa} "
                f"falhou ({type(erro).__name__}: {erro}); recarregando..."
            )

            page.reload(wait_until="load")
            continue

        # Fora do try que controla os reloads:
        # se a extração falhar, o erro será reportado sem repetir reloads.
        tempo_interface = executar_etapa(
            f"Obter tempo da interface - {titulo}",
            processos.obter_tempo_interface,
            card
        )

        return tempo_interface, quantidade_reloads

    raise AssertionError(
        f"Não foi possível confirmar a conclusão: {titulo}"
    )


def processar_caso(page, processos, nome_colecao, caso, titulos_criados):
    arquivo = Path(caso["arquivo"])

    if not arquivo.is_file():
        raise FileNotFoundError(
            f"Arquivo de teste não encontrado: {arquivo}"
        )
    
    prefixo = caso["prefixo"]
    titulo = (
        f"{prefixo} {caso['tipo']} {caso['tamanho']} - Processo "
        + datetime.now().strftime("%Y%m%d_%H%M%S")
    )

    # Criação do processo e medição do upload.
    resultado = executar_etapa(
        f"Criar processo - {arquivo.name}",
        processos.criar_processo,
        nome_colecao,
        str(arquivo),
        titulo,
    )

    # Registrar antes de esperar o processamento.
    # Assim, ele poderá ser excluído mesmo se uma etapa posterior falhar.
    titulos_criados.append(titulo)
    tempo_upload = resultado["tempo_upload"]
    inicio_processamento = resultado["inicio_processamento"]

    print(f"\n[TÍTULO] {titulo}")
    print(f"[ARQUIVO] {arquivo}")
    print(f"[TEMPO UPLOAD] {tempo_upload:.2f} segundos")


    # Espera a conclusão e mede o tempo apresentado pela interface.
    try:
        tempo_interface, quantidade_reloads = executar_etapa(
            f"Aguardar processamento - {arquivo.name}",
            aguardar_processamento,
            page,
            processos,
            titulo,
            prefixo=prefixo
        )
    except Exception as erro:
        fim_processamento = time.perf_counter()
        tempo_processamento_real = fim_processamento - inicio_processamento
        salvar_resultado(
            arquivo=arquivo.name,
            tipo_arquivo=caso["tipo"],
            tamanho_bytes=arquivo.stat().st_size,
            tempo_upload=tempo_upload,
            tempo_processamento_real=tempo_processamento_real,
            tempo_interface=None,
            reloads=0,
            status="FALHA",
            mensagem=f"{type(erro).__name__}: {erro}"
        )
        raise

    fim_processamento = time.perf_counter()

    tempo_processamento_real = (
        fim_processamento - inicio_processamento
    )

    diferenca = tempo_processamento_real - tempo_interface
    diferenca_absoluta = abs(diferenca)

    # Salva as métricas do processo.
    executar_etapa(
        f"Salvar resultado - {arquivo.name}",
        salvar_resultado,
        arquivo=arquivo.name,
        tipo_arquivo=caso["tipo"],
        tamanho_bytes=arquivo.stat().st_size,
        tempo_upload=tempo_upload,
        tempo_processamento_real=tempo_processamento_real,
        tempo_interface=tempo_interface,
        reloads=quantidade_reloads,
        status="SUCESSO"
    )

    print("\n==========================================")
    print(f"Arquivo: {arquivo.name}")
    print(f"Tamanho real: {arquivo.stat().st_size / (1024 * 1024):.2f} MiB")
    print(f"Tempo de upload: {tempo_upload:.2f} s")
    print(f"Tempo real de processamento: {tempo_processamento_real:.2f} s")
    print(f"Tempo da interface: {tempo_interface:.2f} s")
    print(f"Diferença: {diferenca:.2f} s")
    print(f"Diferença absoluta: {diferenca_absoluta:.2f} s")
    print(f"Reloads: {quantidade_reloads}")
    print("==========================================")

    return titulo


def test_ciclo_diario(page):
    casos = descobrir_casos()

    colecoes = ColecoesPage(page)
    processos = ProcessosPage(page)

    nome_colecao = None
    titulos_criados = []
    erros = []

    try:
        # Login
        login = LoginPage(page)
        executar_etapa("Login", login.fazer_login)

        # Criar uma coleção para todos os processos do ciclo
        executar_etapa(
            "Acessar coleções",
            colecoes.acessar
        )

        nome_colecao = executar_etapa(
            "Criar coleção",
            colecoes.criar_colecao
        )

        # Executar cada caso com o mesmo fluxo
        for caso in casos:
            try:
                # Garante acesso à tela de processos para iniciar o caso
                executar_etapa(
                    "Acessar processos",
                    processos.acessar
                )

                processar_caso(
                    page,
                    processos,
                    nome_colecao,
                    caso,
                    titulos_criados
                )

            except Exception as erro:
                mensagem = f"{type(erro).__name__}: {erro}"
                erros.append(f"{caso['arquivo']}: {mensagem}")
                print(f"\n[FALHA] {caso['arquivo']}: {mensagem}")

    finally:
        if not EXECUTAR_LIMPEZA:
            print("\n[LIMPEZA] Etapa de exclusão ignorada (EXECUTAR_LIMPEZA = False).")
        else:
            falha_limpeza_processos = False
            # Tenta excluir todos os processos criados.
            for titulo in reversed(titulos_criados):
                print(f"\n[LIMPEZA] Tentando excluir: {titulo}")
                try:
                    executar_etapa(
                        "Acessar processos para limpeza",
                        processos.acessar
                    )

                    card = processos.obter_card_processo(titulo[:TAM_PREFIXO])

                    executar_etapa(
                        f"Excluir processo - {titulo}",
                        processos.excluir_processo,
                        card
                    )

                    # Atualiza a página se a interface não refletir
                    # imediatamente a exclusão.
                    page.reload(wait_until="load")
                    print(f"[LIMPEZA] Processo excluído: {titulo}")

                except Exception as erro:
                    falha_limpeza_processos = True
                    mensagem = f"{type(erro).__name__}: {erro}"
                    print(
                        f"[FALHA NA LIMPEZA] Processo {titulo}: {mensagem}"
                    )

            # Excluir a coleção somente depois de tentar excluir
            # todos os processos.
            if nome_colecao is not None and not falha_limpeza_processos:
                try:
                    executar_etapa(
                        "Acessar coleções para limpeza",
                        colecoes.acessar
                    )

                    card_colecao = colecoes.obter_card_colecao(
                        nome_colecao
                    )

                    executar_etapa(
                        "Excluir coleção",
                        colecoes.excluir_colecao,
                        card_colecao
                    )

                    page.reload(wait_until="load")
                    print(f"[LIMPEZA] Coleção excluída: {nome_colecao}")

                except Exception as erro:
                    mensagem = f"{type(erro).__name__}: {erro}"
                    print(
                        f"[FALHA NA LIMPEZA] Coleção: {mensagem}"
                    )
            elif nome_colecao is not None:
                print(
                    "[LIMPEZA] Coleção mantida porque pelo menos "
                    "um processo não pôde ser excluído."
                )

    # Mantém o teste como falho se algum caso falhou,
    # mesmo que os outros tenham sido executados.
    assert not erros, (
        "Falhas encontradas no ciclo diário:\n"
        + "\n".join(erros)
    )
