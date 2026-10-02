from datetime import datetime
import re
import time


class ProcessosPage:

    def __init__(self, page):
        self.page = page

    def obter_card_processo(self, prefixo_visivel="AUTO-TEST"): # O prefixo visível eu tenho que mudar depois
        h1 = self.page.locator(
            "h1.mat-tooltip-trigger"
        ).filter(
            has_text=prefixo_visivel
        ).first

        h1.wait_for(
            state="visible"
        )

        return self.page.locator(
            "div.bloco_processo_recente"
        ).filter(
            has=h1
        ).first

    def acessar(self):
        self.page.locator(
            'a[href="#/processo"]'
        ).click()

    def clicar_novo_processo(self):
        self.page.locator(
            "button.novo_processo"
        ).click()

    def preencher_titulo(self, titulo):
        self.page.locator(
            'input[formcontrolname="titulo"]'
        ).fill(titulo)

    def escolher_colecao(self, nome_colecao):
        self.page.locator(
            'nz-select[formcontrolname="colecoes"]'
        ).click()

        self.page.locator(
            "nz-option-item"
        ).first.wait_for(
            state="visible"
        )

        self.page.locator(
            "nz-option-item",
            has_text=nome_colecao
        ).click()

    def fazer_upload(self, documento):
        inicio_upload = time.perf_counter()

        self.page.locator(
            "input[id=files]"
        ).set_input_files(documento)

        # Espera o upload terminar
        self.page.get_by_text(
            "Envios completos: 1/1",
            exact=True
        ).wait_for(
            state="visible",
            timeout=120000
        )

        fim_upload = time.perf_counter()

        return fim_upload - inicio_upload

    def clicar_proximo(self):
        self.page.get_by_role(
            "button",
            name="PRÓXIMO"
        ).click()

    def criar(self):
        self.page.get_by_role(
            "button",
            name="CRIAR"
        ).click()

    def criar_processo(
        self,
        nome_colecao,
        documento,
        tamanho_nome
    ):
        titulo = (
            f"AUTO-TEST PDF {tamanho_nome} - Processo" # Em vez de PDF eu tenho que mudar pra tipo depois
            + datetime.now().strftime("%Y%m%d_%H%M%S")
        )

        self.clicar_novo_processo()

        self.preencher_titulo(titulo)

        self.escolher_colecao(
            nome_colecao
        )

        # Mede somente o upload
        tempo_upload = self.fazer_upload(
            documento
        )

        self.clicar_proximo()

        # Começa a contar o processamento real
        # imediatamente antes de criar o processo.
        inicio_processamento = time.perf_counter()

        self.criar()

        return {
            "titulo": titulo,
            "tempo_upload": tempo_upload,
            "inicio_processamento": inicio_processamento
        }

    def obter_tempo_interface(self, card):
        """
        Obtém o tempo de processamento mostrado
        pela interface.
        """

        infos = card.locator("p.infos")

        quantidade = infos.count()

        if quantidade < 2:
            raise AssertionError(
                "Não foram encontrados elementos "
                "p.infos suficientes."
            )

        elemento_tempo = infos.nth(
            quantidade - 2
        )

        texto = elemento_tempo.inner_text().strip()

        print(
            f"[TEMPO INTERFACE] {texto}"
        )

        match = re.search(
            r"(\d+)\s*segundo",
            texto
        )

        if not match:
            raise AssertionError(
                f"Não foi possível extrair o tempo "
                f"da interface: '{texto}'"
            )

        return int(match.group(1))