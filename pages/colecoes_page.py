from datetime import datetime


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