from datetime import datetime
from playwright.sync_api import expect


class ColecoesPage:

    def __init__(self, page):
        self.page = page

    def acessar(self):
        self.page.locator('a[href="#/colecao"]').click()

    def clicar_nova_colecao(self):
        self.page.locator("button.nova_colecao").click()

    def preencher_nome(self, nome):
        self.page.locator('input[formcontrolname="nome"]').fill(nome)

    def preencher_descricao(self, descricao):
        self.page.locator('textarea[formcontrolname="descricao"]').fill(descricao)

    def clicar_proximo(self):
        self.page.get_by_role("button", name="PROXIMO").click()

    def criar(self):
        self.page.get_by_role("button", name="CRIAR").click()

    def obter_card_colecao(self, nome_colecao, timeout=15000):
        card = self.page.locator(
            "div.bloco_colecao"
        ).filter(
            has=self.page.locator(
                "h2 span"
            ).filter(
                has_text=nome_colecao
            )
        ).first

        card.wait_for(
            state="visible",
            timeout=timeout
        )

        return card

    def criar_colecao(self):
        nome = (
            "[AUTO-TEST] Coleção "
            + datetime.now().strftime("%Y%m%d_%H%M%S")
        )

        descricao = "Coleção criada automaticamente para testes."

        self.clicar_nova_colecao()

        self.preencher_nome(nome)
        self.preencher_descricao(descricao)

        self.clicar_proximo()

        self.criar()

        return nome

    def excluir_colecao(self, card):
        botao_menu = card.locator("button.mat-menu-trigger")
        botao_menu.wait_for(state="visible", timeout=15000)

        # Abre o menu de ações da coleção
        try:
            botao_menu.click(timeout=5000)
        except Exception:
            botao_menu.click(force=True)

        # Clica em Excluir
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
