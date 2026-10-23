# Testes Automatizados - Wise Archival

Suíte de testes automatizados ponta a ponta (E2E) para a interface web do **Wise Archival**. O projeto utiliza **Playwright** e **pytest** para validar fluxos críticos do sistema, com foco especial na medição comparativa entre o **tempo real de processamento** e o **tempo exibido na interface**, persistindo todas as métricas em banco de dados SQLite para auditoria e relatórios.

---

## 🎯 Objetivos do Projeto

- **Validação de Fluxos E2E:** Login de gestor, criação/exclusão de coleções e submissão/exclusão de processos.
- **Auditoria de Performance:** Medição precisa do tempo de upload, tempo real de processamento e extração do tempo reportado pelo sistema.
- **Cálculo de Discrepância:** Registro da diferença (`tempo_real - tempo_interface`) para identificar inconsistências na interface do Wise Archival.
- **Suporte Multi-formato:** Testes com múltiplos formatos e pesos de arquivo (**PDF**, **PNG**, **MP3** e **MP4**).
- **Ciclo Diário Autolimpante:** Execução automatizada com descarte seguro de todos os processos e coleções gerados durante a rotina.

---

## 🛠️ Tecnologias Utilizadas

- **Linguagem:** Python 3.11+
- **Automação Web:** [Playwright](https://playwright.dev/python/) (Python Sync API)
- **Framework de Testes:** [pytest](https://docs.pytest.org/)
- **Manipulação de Imagens e Documentos:** Pillow e ReportLab
- **Multimídia:** FFmpeg (geração sintética de áudios MP3 e vídeos MP4)
- **Armazenamento:** SQLite3 (banco de dados local em `reports/resultados.db`)
- **Padrão de Projeto:** Page Object Model (POM)

---

## 📁 Estrutura do Repositório

```text
testes-wise-archival/
├── pages/                    # Page Objects (encapsulamento de seletores e ações)
│   ├── login_page.py         # Tela de login e autenticação
│   ├── colecoes_page.py      # Gestão de coleções (criação, busca e exclusão)
│   └── processos_page.py     # Gestão de processos (upload, extração de tempo e exclusão)
├── tests/                    # Suíte de testes
│   ├── test_diario.py        # [PRINCIPAL] Ciclo diário completo de testes e medições
│   ├── test_login.py         # Teste unitário de login
│   ├── test_colecoes.py      # Teste de criação de coleções
│   └── test_processos.py     # Teste de criação de processo individual
├── scripts/                  # Utilitários para geração de arquivos sintéticos
│   ├── gerar_todos_arquivos.py # Gerador unificado via CLI (PDF, PNG, MP3, MP4)
│   ├── gerar_pdfs.py         # Gerador de documentos PDF
│   ├── gerar_pngs.py         # Gerador de imagens PNG com peso exato
│   ├── gerar_mp3s.py         # Gerador de áudios MP3 (via FFmpeg)
│   └── gerar_mp4s.py         # Gerador de vídeos MP4 (via FFmpeg)
├── test_data/                # Arquivos sintéticos utilizados nos uploads de teste
├── utils/                    # Módulos auxiliares
│   ├── config.py             # Configurações e credenciais (ignorado no git)
│   ├── config.example.py     # Modelo de configuração de ambiente
│   └── database.py           # Gestão do banco de dados SQLite e gravação de resultados
├── reports/                  # Relatórios e base de dados local
│   └── resultados.db         # Banco SQLite com métricas e histórico de etapas
├── conftest.py               # Fixtures globais do pytest e configurações do Playwright
├── pytest.ini               # Argumentos padrão do pytest
└── requirements.txt          # Dependências do projeto Python
```

---

## 🚀 Instalação e Preparação do Ambiente

### 1. Clonar o repositório e criar o ambiente virtual

```bash
git clone <URL_DO_REPOSITORIO>
cd testes-wise-archival

# Criar ambiente virtual
python -m venv .venv

# Ativar ambiente virtual
# No Windows (PowerShell):
.venv\Scripts\Activate.ps1
# No Windows (CMD):
.venv\Scripts\activate.bat
# No Linux/macOS:
source .venv/bin/activate
```

### 2. Instalar dependências Python e navegador Playwright

```bash
pip install -r requirements.txt
playwright install chromium
```

> [!NOTE]
> Para gerar novos arquivos sintéticos de áudio (`.mp3`) ou vídeo (`.mp4`) através dos scripts auxiliares, é necessário que o **FFmpeg** esteja instalado no sistema operacional e disponível no `PATH`.

---

## ⚙️ Configuração de Acesso

Antes de rodar os testes, crie o arquivo com as credenciais do ambiente de testes:

1. Copie o arquivo modelo:
   ```bash
   cp utils/config.example.py utils/config.py
   ```
2. Crie `utils/config.py` e preencha a URL da interface e as credenciais do usuário Gestor

---

## 📦 Geração de Arquivos de Teste (`test_data/`)

O projeto possui scripts dedicados para gerar arquivos sintéticos com tamanhos exatos e conteúdo válido:

```bash
# Gerar todos os arquivos padrão (PDF, PNG, MP3 e MP4):
python scripts/gerar_todos_arquivos.py

# Ou gerar por formato específico:
python scripts/gerar_todos_arquivos.py --pdf
python scripts/gerar_todos_arquivos.py --png
python scripts/gerar_todos_arquivos.py --mp3
python scripts/gerar_todos_arquivos.py --mp4
```

### Perfis de Tamanho Disponíveis

| Formato | Leve | Médio | Pesado |
| :--- | :--- | :--- | :--- |
| **PDF** | `2mb.pdf` | `10mb.pdf` | `50mb.pdf` |
| **PNG** | `2mb.png` | `5mb.png` | `20mb.png` |
| **MP3** | `2mb.mp3` (~1.5 min) | `10mb.mp3` (~7.3 min) | `30mb.mp3` (~21.8 min) |
| **MP4** | `5mb.mp4` (~8s, 720p) | `25mb.mp4` (~40s, 720p) | `50mb.mp4` (~80s, 720p) |

---

## 🧪 Executando os Testes

### 1. Teste Diário Principal (`test_diario.py`)

Este é o teste oficial que executa o ciclo completo de medições:

```bash
pytest tests/test_diario.py -s
```

*(A flag `-s` garante a visualização dos logs, tempos medidos e prints em tempo real no terminal).*

#### Controle de Limpeza Automática
No início do arquivo `tests/test_diario.py`:
- `EXECUTAR_LIMPEZA = True`: Exclui todos os processos criados e a coleção ao término do teste (padrão de produção).
- `EXECUTAR_LIMPEZA = False`: Mantém os processos e a coleção visíveis no Wise Archival para inspeção manual.

### 2. Configurar os Casos de Teste no Ciclo Diário
No arquivo `tests/test_diario.py`, você pode selecionar quais arquivos e formatos deseja rodar ajustando a lista `casos`:

```python
    casos = [
        {"arquivo": "test_data/2mb.pdf", "tipo": "PDF", "tamanho": "2MB"},
        {"arquivo": "test_data/5mb.png", "tipo": "PNG", "tamanho": "5MB"},
        {"arquivo": "test_data/10mb.mp3", "tipo": "MP3", "tamanho": "10MB"},
        {"arquivo": "test_data/25mb.mp4", "tipo": "MP4", "tamanho": "25MB"},
    ]
```

---

## 📊 Banco de Dados de Métricas (`reports/resultados.db`)

Todos os resultados são persistidos automaticamente no banco SQLite localizado em `reports/resultados.db`.

### Estrutura das Tabelas

#### Tabela `resultados`
Registra os tempos de cada arquivo processado:

| Coluna | Tipo | Descrição |
| :--- | :--- | :--- |
| `id` | INTEGER | Identificador único auto-incremental |
| `data_hora` | TEXT | Timestamp ISO da execução (`YYYY-MM-DDTHH:MM:SS`) |
| `arquivo` | TEXT | Nome do arquivo enviado (ex: `2mb.pdf`) |
| `tipo_arquivo` | TEXT | Extensão/Tipo do documento (`PDF`, `PNG`, `MP3`, `MP4`) |
| `tamanho_bytes` | INTEGER | Tamanho físico real em bytes |
| `tamanho_mb` | REAL | Tamanho físico em MiB |
| `tempo_upload` | REAL | Tempo em segundos decorrido no upload |
| `tempo_processamento_real` | REAL | Tempo medido pelo teste até a conclusão |
| `tempo_interface` | REAL | Tempo que a interface web exibiu no card |
| `diferenca` | REAL | Discrepância (`tempo_processamento_real - tempo_interface`) |
| `diferenca_absoluta` | REAL | Valor absoluto da diferença (`abs(diferenca)`) |
| `reloads` | INTEGER | Quantidade de recarregamentos necessários para detectar conclusão |
| `status` | TEXT | `"SUCESSO"` ou `"FALHA"` |
| `mensagem` | TEXT | Detalhes do erro em caso de falha |

#### Tabela `etapas_teste`
Registra o ciclo de vida granular de cada etapa executada:

| Coluna | Tipo | Descrição |
| :--- | :--- | :--- |
| `id` | INTEGER | Identificador da etapa |
| `data_hora` | TEXT | Timestamp ISO do evento |
| `etapa` | TEXT | Nome descritivo da etapa (ex: `Criar processo - 10mb.pdf`) |
| `status` | TEXT | `"SUCESSO"` ou `"FALHA"` |
| `mensagem` | TEXT | Detalhes da conclusão ou rastreamento da exceção |