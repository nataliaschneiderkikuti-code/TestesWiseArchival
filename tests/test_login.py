from playwright.sync_api import expect

from pages.login_page import LoginPage


def test_login_gestor(page):

    login = LoginPage(page)

    login.fazer_login()

    # Verifica se o Dashboard apareceu após o login
    dashboard = page.get_by_text("Dashboard", exact=True)

    expect(dashboard).to_be_visible(timeout=15000)