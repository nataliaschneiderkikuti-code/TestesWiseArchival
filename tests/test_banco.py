# pytest tests/test_banco.py -s
from playwright.sync_api import expect
import time

from pages.login_page import LoginPage
from pages.colecoes_page import ColecoesPage
from pages.processos_page import ProcessosPage

from pathlib import Path
from utils.database import salvar_resultado, registrar_etapa

def executar_etapa(nome_etapa, funcao, *args, **kwargs): # Quando eu for desenvolver o ciclo de testes diários tenho que colocar essa função
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

def test_criar_processso(page):

    nome = None
    titulo = None

    try:

        # Login
        login = LoginPage(page)
        executar_etapa(
            "Login",
            login.fazer_login
        )

        # Acessar Coleções
        colecoes = ColecoesPage(page)
        executar_etapa(
            "Acessar coleções",
            colecoes.acessar
        )

        # Criar coleção
        nome = nome = executar_etapa(
            "Criar coleção",
            colecoes.criar_colecao
        )

        # Acessar Processos
        processos = ProcessosPage(page)
        executar_etapa(
            "Acessar processos",
            processos.acessar
        )

        # Criar processo
        resultado = executar_etapa(
            "Criar processo",
            processos.criar_processo,
            nome,
            "test_data/grande.pdf",
            "PDF",
            "300MB"
        )

        titulo = resultado["titulo"]
        tempo_upload = resultado["tempo_upload"]
        inicio_processamento = resultado["inicio_processamento"]

        print(f"\n[TÍTULO] {titulo}")
        print(
            f"[TEMPO UPLOAD] "
            f"{tempo_upload:.2f} segundos"
        )

        # O card já aparece depois da criação
        card = processos.obter_card_processo(titulo[:18])

        quantidade_reloads = 0
        tempo_interface = None

        # Verifica se o tempo do processamento já apareceu
        for tentativa in range(1, 6):

            try:
                expect(
                    card
                ).to_be_visible(
                    timeout=15000
                )

                # Enquanto estiver processando, esse texto aparece.
                # Quando terminar, ele desaparece.
                expect(
                    card.get_by_text(
                        "Processando...",
                        exact=True
                    )
                ).to_be_hidden(
                    timeout=120000
                )

                # Depois que "Processando..." desapareceu,
                # tentamos obter o tempo mostrado pela interface.
                tempo_interface = (
                    processos.obter_tempo_interface(card)
                )

                # Se conseguimos obter os segundos,
                # consideramos que a interface foi atualizada.
                break

            except AssertionError:

                if tentativa == 5:
                    raise

                quantidade_reloads += 1

                print(
                    f"[RELOAD] Tentativa {tentativa} "
                    f"falhou, recarregando a página..."
                )

                page.reload(
                    wait_until="load"
                )

                # O DOM foi recriado, então pegamos
                # novamente o card.
                card = processos.obter_card_processo(titulo[:18])

        # O cronômetro termina quando a interface
        # finalmente mostrou o tempo do processamento.
        fim_processamento = time.perf_counter()

        tempo_processamento_real = (
            fim_processamento
            - inicio_processamento
        )

        # Comparação
        diferenca = (
            tempo_processamento_real
            - tempo_interface
        )

        diferenca_absoluta = abs(
            diferenca
        )

        arquivo = Path("test_data/grande.pdf")

        salvar_resultado(
            arquivo=arquivo.name,
            tipo_arquivo="PDF",
            tamanho_bytes=arquivo.stat().st_size,
            tempo_upload=tempo_upload,
            tempo_processamento_real=tempo_processamento_real,
            tempo_interface=tempo_interface,
            reloads=quantidade_reloads,
            status="SUCESSO"
        )

        print("\n==========================================")
        print(f"Título: {titulo}")
        print(
            f"Tempo de upload: "
            f"{tempo_upload:.2f} segundos"
        )
        print(
            f"Tempo real de processamento: "
            f"{tempo_processamento_real:.2f} segundos"
        )
        print(
            f"Tempo informado pela interface: "
            f"{tempo_interface:.2f} segundos"
        )
        print(
            f"Diferença: "
            f"{diferenca:.2f} segundos"
        )
        print(
            f"Diferença absoluta: "
            f"{diferenca_absoluta:.2f} segundos"
        )
        print(
            f"Reloads necessários: "
            f"{quantidade_reloads}"
        )
        print("==========================================")

        assert tempo_upload >= 0
        assert tempo_processamento_real >= 0
        assert tempo_interface >= 0
        assert quantidade_reloads >= 0

    finally:
        # Tenta excluir o processo, se ele foi criado.
        if titulo is not None:
            try:
                processos.acessar()

                card = processos.obter_card_processo(
                    titulo[:18]
                )

                executar_etapa(
                    "Excluir processo",
                    processos.excluir_processo,
                    card
                )

            except Exception as erro:
                print(
                    f"Falha na limpeza do processo: {erro}"
                )

        # Independentemente do resultado anterior,
        # tenta excluir a coleção, se ela foi criada.
        if nome is not None:
            try:
                colecoes.acessar()

                card_colecao = colecoes.obter_card_colecao(
                    nome
                )

                executar_etapa(
                    "Excluir coleção",
                    colecoes.excluir_colecao,
                    card_colecao
                )

            except Exception as erro:
                print(
                    f"Falha na limpeza da coleção: {erro}"
                )
                registrar_etapa(
                    etapa="Excluir coleção",
                    status="FALHA",
                    mensagem=f"{type(erro).__name__}: {erro}"
                )

    # processos.excluir_processo(card)
    # colecoes.acessar()
    # card_colecao = colecoes.obter_card_colecao(nome)
    # colecoes.excluir_colecao(card_colecao) # Outro erro na interface é que parece que mesmo depois de excluir a coleção a interface não atualiza a não ser que dê reload

    