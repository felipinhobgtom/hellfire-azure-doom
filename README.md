# HELLFIRE — laboratório de FPS web e API SQLite

Projeto acadêmico de ponta a ponta: jogo de tiro retrô original no navegador, API REST em Python/Flask, persistência SQLite e infraestrutura Azure declarada em ARM. O cliente abre direto na arena; o placar consulta e grava no backend.

> **Importante sobre o jogo:** este repositório ainda não incorpora nem compila o código de [Chocolate Doom](https://github.com/midzer/chocolate-doom) para WebAssembly. A arena atual é um protótipo original em Canvas 2D com controles FPS; não é Doom/Chocolate Doom nem contém IWAD. Para usar o port de Chocolate Doom em WASM seria necessário um port Emscripten/SDL2, integração de controles e fornecer ao jogador um IWAD legalmente obtido. Nenhum asset proprietário é distribuído.

## Executar localmente

Para desenvolvimento, instale Python 3.12+ e execute `pip install -r requirements.txt`. Opcionalmente, `nix develop` fornece Python, dependências e Azure CLI; **Nix não é requisito de execução nem de deploy**.

```bash
python app.py                # http://localhost:8000
```

Também pode executar com Docker sem Nix:

```bash
docker build -t hellfire .
docker run --rm -p 8000:8000 -v "$PWD/data:/data" hellfire
```

## API

| Método | Rota | Função |
|---|---|---|
| GET | `/api/health` | Verifica aplicação e SQLite |
| GET | `/api/scores` | Lista até 10 maiores pontuações |
| POST | `/api/scores` | Registra `{ "player": "marine", "kills": 7 }` |

`POST` retorna `201` com o registro salvo. Nome de jogador: 1–24 caracteres. Eliminações: inteiro de 0–999999. Erros de validação retornam `400`. O banco padrão é `data/doom.db`; configure outro caminho por `DATABASE_PATH`.

## Deploy Azure

Pré-requisitos: assinatura Azure habilitada, `nix` instalado, `gh` autenticado e permissões para criar grupo, VM, rede e Storage Account.

1. Publique este repositório como **público**: a VM faz `git clone` durante o cloud-init.
2. `nix develop` e autentique com `az login` (se necessário).
3. Defina uma senha forte apenas para o perfil administrativo da VM: `export AZURE_VM_PASSWORD='...'`.
4. Execute `./deploy.sh` (região padrão `brazilsouth`; troque com `AZURE_LOCATION`).
5. Aguarde o cloud-init construir o container; abra a URL HTTP da saída e `/api/health`.
6. Ao terminar a demonstração, rode `az group delete --name rg-hellfire-demo --yes --no-wait` para remover os recursos e evitar cobranças.

O ARM cria VM Ubuntu 22.04 `Standard_B1s`, disco SSD gerenciado Standard 30 GB, IP público IPv4, VNet/subnet, NSG liberando somente HTTP/80 e Storage Account privada Standard_LRS para boot diagnostics. A aplicação/gravações SQLite ficam no disco persistente da VM, **não** no blob. O endpoint é HTTP sem TLS e serve para demonstração; não exponha dados sensíveis. SSH é fechado pela NSG.

Consulte o guia completo, diagrama, esquema relacional e comandos no [`docs/relatorio.md`](docs/relatorio.md). Uma cópia PDF está em [`docs/relatorio.pdf`](docs/relatorio.pdf).

## Tecnologias

Python 3.12, Flask, SQLite, Gunicorn, HTML/CSS/JavaScript Canvas, Docker, Nix Flake, Azure ARM, Azure CLI. O fonte de referência escolhido para avaliação do port é [midzer/chocolate-doom](https://github.com/midzer/chocolate-doom) (GPL); nenhuma cópia modificada está embutida neste primeiro deploy.
