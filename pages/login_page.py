from utils.config import WISE_URL, WISE_USUARIO, WISE_SENHA


class LoginPage:

    def __init__(self, page):
        self.page = page

    def acessar(self):
        self.page.goto(WISE_URL)

    def preencher_usuario(self):
        self.page.locator("#usuario").fill(WISE_USUARIO)

    def preencher_senha(self):
        self.page.locator("#senha").fill(WISE_SENHA)

    def clicar_entrar(self):
        self.page.locator("button.login").click()

    def fazer_login(self):
        self.acessar()

        self.preencher_usuario()
        self.preencher_senha()

        self.clicar_entrar()