# HELLFIRE — Chocolate Doom no Azure

Projeto acadêmico: Chocolate Doom em WebAssembly, com Freedoom Phase 1, API Flask e SQLite. Ao abrir a página, o jogo inicia diretamente no primeiro mapa; use setas, Ctrl e Espaço.
![HELLFIRE — Doom em execução no navegador](docs/evidence-homepage.png)

## Executar localmente

Clone com o submódulo upstream incluído: `git clone --recurse-submodules https://github.com/felipinhobgtom/hellfire-azure-doom.git`. Para desenvolvimento, instale Python 3.12+ e execute `pip install -r requirements.txt`. Nix é opcional para runtime/deploy; use `nix develop` e `./scripts/build_wasm.sh` para reconstruir o port com Emscripten/SDL2 e Freedoom. O pacote WASM compilado e IWAD já estão no repositório.

```bash
python app.py                # http://localhost:8000
```

Também pode executar o container sem Nix:

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

Pré-requisitos: Azure CLI instalado em qualquer máquina (Nix é opcional) e permissões para criar grupo, VM, rede e Storage Account. A demo está em **[https://hellfire-azure-doom-felipinhobgtom.mexicocentral.cloudapp.azure.com](https://hellfire-azure-doom-felipinhobgtom.mexicocentral.cloudapp.azure.com)** (`Standard_B1s`, `mexicocentral`).

1. Autentique com `az login` (se necessário).
2. Defina uma senha forte para a VM: `export AZURE_VM_PASSWORD='...'`.
3. Execute `./deploy.sh` (região padrão `brazilsouth`; selecione com `AZURE_LOCATION`, SKU com `AZURE_VM_SIZE`). O ARM configura o DNS público Azure; `AZURE_DNS_LABEL` permite escolher outro rótulo se o padrão já estiver ocupado na região. A assinatura estudantil atual permite `brazilsouth`, `mexicocentral`, `chilecentral`, `spaincentral` e `southcentralus`; valide as regiões/cotas da sua própria assinatura.
4. Aguarde cloud-init construir a aplicação e o Caddy emitir o certificado TLS; depois acesse a URL HTTPS.
5. Ao terminar a demonstração, rode `az group delete --name rg-hellfire-mexico --yes --no-wait` para remover os recursos e evitar cobranças.

O ARM cria VM Ubuntu 22.04 `Standard_B1s` por padrão (selecionável como `Standard_B2s`), disco SSD gerenciado Standard 30 GB, IP público IPv4 com hostname Azure `*.cloudapp.azure.com`, VNet/subnet, NSG liberando HTTP/80 e HTTPS/443 e Storage Account privada Standard_LRS para boot diagnostics. Caddy obtém e renova automaticamente certificado TLS público e redireciona HTTP para HTTPS. A aplicação/gravações SQLite ficam no disco persistente da VM, **não** no blob. SSH é fechado pela NSG.

Consulte o guia completo, diagrama, esquema relacional e comandos no [`docs/relatorio.md`](docs/relatorio.md). Uma cópia PDF está em [`docs/relatorio.pdf`](docs/relatorio.pdf).

## CI/CD GitHub Actions

`.github/workflows/cicd.yml` executa testes da API, valida JavaScript/shell/ARM e constrói a imagem em cada push e pull request. Pushes para `main` também fazem deploy: o workflow autentica no Azure por OIDC, chama `az vm run-command` para atualizar o código e reconstruir o container, preserva o SQLite e testa a URL HTTPS. Não há client secret no GitHub.

Para outra instalação, configure as variáveis do repositório `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`, `AZURE_RESOURCE_GROUP`, `AZURE_VM_NAME` e `AZURE_SITE_URL`. A aplicação Entra precisa de uma credencial federada com subject no formato `repo:OWNER@OWNER_ID/REPO@REPO_ID:ref:refs/heads/main` (use os claims exatos emitidos pelo GitHub) e da função `Virtual Machine Contributor` no escopo da VM. O script executado remotamente está em `scripts/deploy_vm.sh`.

## Tecnologias

Python 3.12, Flask, SQLite, Gunicorn, Chocolate Doom 3.1.0, Emscripten/SDL2, Freedoom 0.13, Docker, Caddy, Nix Flake, Azure ARM e Azure CLI. Chocolate Doom está incluído como submódulo GPL-2.0; conteúdo Freedoom sob BSD-3-Clause.
