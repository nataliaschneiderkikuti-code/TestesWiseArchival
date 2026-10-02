# Testes automatizados - Wise Archival

Testes automatizados da interface web do Wise Archival.

## Tecnologias

- Python
- Playwright
- pytest

## Instalação

```bash
pip install -r requirements.txt
playwright install
```

## Configuração

Antes de executar os testes, é necessário criar e configurar o arquivo utils/config.py.

Esse arquivo deve conter as configurações locais necessárias para acessar o Wise Archival, como a URL da aplicação e as credenciais de acesso.

Crie o arquivo:
utils/config.py

Copie o arquivo utils/config.example.py para utils/config.py e preencha os valores com as configurações do ambiente de testes.