from datetime import datetime
import re
import time
from playwright.sync_api import expect


class ProcessosPage:

    def __init__(self, page):
        self.page = page

    def obter_card_processo(self, prefixo_visivel, timeout=15000):
        h1 = self.page.locator(
            "h1.mat-tooltip-trigger"
        ).filter(
            has_text=prefixo_visivel
        ).first

        h1.wait_for(
            state="visible",
            timeout=timeout
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
            timeout=180000
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
        tipo_doc,
        tamanho_nome
    ):
        titulo = (
            f"AUTO-TEST {tipo_doc} {tamanho_nome} - Processo"
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

    def excluir_processo(self, card):
        botao_menu = card.locator("button.mat-menu-trigger")
        botao_menu.wait_for(state="visible", timeout=15000)

        # Passa o mouse sobre o card para ativar controles caso necessário
        try:
            card.hover(timeout=3000)
        except Exception:
            pass

        # Abre o menu de ações do processo
        try:
            botao_menu.click(timeout=5000)
        except Exception:
            # Caso algum overlay (ex: div.card-menu-overlay) intercepte o ponteiro, força o clique
            botao_menu.click(force=True)

        # Clica na opção Excluir do menu suspenso
        excluir = self.page.get_by_role(
            "menuitem",
            name="Excluir"
        )
        expect(excluir).to_be_visible(timeout=10000)
        excluir.click()

        # Confirma a exclusão no SweetAlert
        confirmar = self.page.locator(
            "button.swal2-confirm.excluir-modal, button.swal2-confirm"
        ).first
        expect(confirmar).to_be_visible(timeout=10000)
        confirmar.click()

    def obter_tempo_interface(self, card):
        infos = card.locator("p.infos")
        quantidade = infos.count()

        if quantidade < 2:
            raise AssertionError(
                "Não foram encontrados elementos p.infos suficientes."
            )

        elemento_tempo = infos.nth(quantidade - 2)
        texto = elemento_tempo.inner_text().strip().lower()

        print(f"[TEMPO INTERFACE] {texto}")

        total_segundos = 0
        encontrou = False

        # Horas
        match_hora = re.search(r"(\d+)\s*(?:hora|horas|h\b)", texto)
        if match_hora:
            total_segundos += int(match_hora.group(1)) * 3600
            encontrou = True

        # Minutos
        match_min = re.search(r"(\d+)\s*(?:minuto|minutos|min\b|m\b)", texto)
        if match_min:
            total_segundos += int(match_min.group(1)) * 60
            encontrou = True

        # Segundos
        match_seg = re.search(r"(\d+)\s*(?:segundo|segundos|seg\b|s\b)", texto)
        if match_seg:
            total_segundos += int(match_seg.group(1))
            encontrou = True

        if not encontrou:
            # Se a interface contiver apenas o número puro de segundos
            match_puro = re.search(r"^(\d+)$", texto)
            if match_puro:
                return int(match_puro.group(1))

            raise AssertionError(
                f"Não foi possível extrair o tempo da interface: '{texto}'"
            )

        return total_segundos
