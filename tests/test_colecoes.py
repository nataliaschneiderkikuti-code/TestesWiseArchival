from playwright.sync_api import expect

from pages.login_page import LoginPage
from pages.colecoes_page import ColecoesPage


def test_criar_colecao(page):

    # Login
    login = LoginPage(page)
    login.fazer_login()

    # Acessar Coleções
    colecoes = ColecoesPage(page)
    colecoes.acessar()

    # Criar coleção
    nome = colecoes.criar_colecao()

    # Verificar se a coleção apareceu
    expect(
        page.get_by_text(nome, exact=True).first
    ).to_be_visible(timeout=15000)