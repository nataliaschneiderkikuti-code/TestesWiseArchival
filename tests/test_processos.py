from playwright.sync_api import expect
import time

from pages.login_page import LoginPage
from pages.colecoes_page import ColecoesPage
from pages.processos_page import ProcessosPage


def test_criar_processso(page):

    # Login
    login = LoginPage(page)
    login.fazer_login()

    # Acessar Coleções
    colecoes = ColecoesPage(page)
    colecoes.acessar()

    # Criar coleção
    nome = colecoes.criar_colecao()

    # Acessar Processos
    processos = ProcessosPage(page)
    processos.acessar()

    # Criar processo
    resultado = processos.criar_processo(
        nome,
        "test_data/grande.pdf",
        "25MB"
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
            card = processos.obter_card_processo()

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