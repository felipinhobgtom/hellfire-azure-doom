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

## Deploy Azure com ARM + Azure CLI

Este caminho faz deploy na sua assinatura Azure, no Windows (PowerShell) ou Linux (Bash), usando **somente Azure CLI e o template ARM publicado no GitHub**. Não exige Nix, Docker, GitHub CLI nem clone local: a VM baixa o repositório público durante o bootstrap. A implantação cria uma VM Ubuntu e os recursos de rede, IP/DNS e diagnóstico.

> **Custos:** a VM ligada, o disco e outros recursos podem gerar cobrança. Consulte a [calculadora de preços do Azure](https://azure.microsoft.com/pricing/calculator/) para sua região/assinatura. Apague o grupo de recursos ao terminar.

### 1. Pré-requisitos

- Uma assinatura Azure ativa e Azure CLI instalado:
  - [Instalar no Windows](https://learn.microsoft.com/cli/azure/install-azure-cli-windows)
  - [Instalar no Linux](https://learn.microsoft.com/cli/azure/install-azure-cli-linux)
- Permissão para criar um Resource Group e recursos Compute, Network e Storage; cota/capacidade disponível para `Standard_B1s` ou `Standard_B2s`.
- Internet para acessar Azure e GitHub. O repositório configurado no template é público.
- Uma senha forte para `azureuser`: mínimo de 12 caracteres com maiúscula, minúscula, número e símbolo. O SSH não é aberto pela regra de rede.

O Azure CLI é o mesmo em Windows e Linux. Os exemplos usam PowerShell no Windows e Bash no Linux; execute cada bloco no terminal correspondente. Nix é opcional e não participa do deploy.

### 2. Entrar na assinatura Azure

No PowerShell ou Bash:

```text
az login
az account list --output table
az account set --subscription "<ID-OU-NOME-DA-SUBSCRICAO>"
az account show --output table
```

Se `az login` abrir o navegador, conclua a autenticação com a conta que receberá os recursos. Em Azure Cloud Shell, a sessão normalmente já está autenticada; ainda confira a assinatura com `az account show`.

### 3. Implantar o template

O template remoto define a região por meio do Resource Group. Escolha uma região habilitada na sua assinatura; abaixo usamos `brazilsouth`. O rótulo DNS público precisa ser único. Se Azure indicar que o rótulo já está em uso, gere outro e repita o deploy. A senha não é salva no repositório nem no arquivo de parâmetros.

#### Windows — PowerShell

```powershell
$ResourceGroup = "rg-hellfire-demo"
$Location = "brazilsouth"
$DnsLabel = "hellfire-doom-$((Get-Random -Minimum 10000 -Maximum 99999))"
$TemplateUri = "https://raw.githubusercontent.com/felipinhobgtom/hellfire-azure-doom/main/infra/main.json"
$RepositoryUrl = "https://github.com/felipinhobgtom/hellfire-azure-doom.git"

az group create --name $ResourceGroup --location $Location --output table

$SecurePassword = Read-Host "Senha forte para azureuser" -AsSecureString
$VmPassword = [System.Net.NetworkCredential]::new("", $SecurePassword).Password
$WebsiteUrl = az deployment group create `
  --resource-group $ResourceGroup `
  --name ("hellfire-" + (Get-Date -Format "yyyyMMddHHmmss")) `
  --template-uri $TemplateUri `
  --parameters "adminPassword=$VmPassword" "repositoryUrl=$RepositoryUrl" "dnsLabel=$DnsLabel" "vmSize=Standard_B1s" `
  --query "properties.outputs.websiteUrl.value" --output tsv
if ($LASTEXITCODE -ne 0) { throw "O deploy ARM falhou; consulte a mensagem do Azure." }
$VmPassword = $null
$SecurePassword = $null
Write-Host "URL do jogo: $WebsiteUrl"
```

#### Linux — Bash

```bash
set -euo pipefail
RESOURCE_GROUP="rg-hellfire-demo"
LOCATION="brazilsouth"
DNS_LABEL="hellfire-doom-$RANDOM-$RANDOM"
TEMPLATE_URI="https://raw.githubusercontent.com/felipinhobgtom/hellfire-azure-doom/main/infra/main.json"
REPOSITORY_URL="https://github.com/felipinhobgtom/hellfire-azure-doom.git"

az group create --name "$RESOURCE_GROUP" --location "$LOCATION" --output table

read -r -s -p "Senha forte para azureuser: " VM_PASSWORD
printf '\n'
WEBSITE_URL="$(az deployment group create \
  --resource-group "$RESOURCE_GROUP" \
  --name "hellfire-$(date +%Y%m%d%H%M%S)" \
  --template-uri "$TEMPLATE_URI" \
  --parameters "adminPassword=$VM_PASSWORD" "repositoryUrl=$REPOSITORY_URL" "dnsLabel=$DNS_LABEL" "vmSize=Standard_B1s" \
  --query 'properties.outputs.websiteUrl.value' --output tsv)"
unset VM_PASSWORD
printf 'URL do jogo: %s\n' "$WEBSITE_URL"
```

Os dois exemplos usam o SKU econômico `Standard_B1s`; o ARM também aceita `Standard_B2s`. Se sua assinatura não tiver cota ou capacidade na região/SKU, escolha outra região com suporte ou troque `Standard_B1s` por `Standard_B2s` e tente novamente. O template define por padrão a VM `hellfire-vm` e o usuário `azureuser`.

### 4. Aguardar a inicialização e abrir o jogo

O comando ARM termina quando os recursos foram provisionados; a VM ainda precisa executar cloud-init, instalar Docker, clonar o projeto e iniciar o serviço. Aguarde alguns minutos. Caddy precisa resolver o DNS público para emitir o certificado HTTPS; isso também pode levar alguns minutos. Abra a URL `https://...` impressa pelo comando — não adivinhe o endereço: ele é o output `websiteUrl` do ARM.

No Linux, teste quando a URL aparecer:

```bash
curl --fail --show-error "$WEBSITE_URL/api/health"
curl --fail --show-error --output /dev/null "$WEBSITE_URL/doom/chocolate-doom.wasm"
```

No Windows PowerShell:

```powershell
Invoke-RestMethod "$WebsiteUrl/api/health"
Invoke-WebRequest "$WebsiteUrl/doom/chocolate-doom.wasm" -Method Head
Start-Process $WebsiteUrl
```

O health check deve retornar `status: ok` e o arquivo WASM uma resposta HTTP de sucesso. A imagem do jogo no início deste README mostra a experiência esperada após a página abrir.

### 5. O que o template cria

| Recurso | Configuração padrão | Finalidade |
|---|---|---|
| Resource Group | `rg-hellfire-demo` | Agrupa os recursos desta implantação |
| VM Linux | Ubuntu Server 22.04, `Standard_B1s` | Executa Docker, a API Flask/SQLite e o proxy Caddy |
| Disco gerenciado | Standard SSD, 30 GB | Sistema operacional e banco SQLite persistente |
| Rede | VNet, subnet, NIC e IP público IPv4 estático | Conectividade da VM e hostname DNS Azure |
| NSG | Entrada TCP 80 e 443; sem SSH/22 | HTTP para redirecionamento/desafio TLS e HTTPS para o site |
| Storage Account | `Standard_LRS`, acesso público a Blob desativado | Boot diagnostics; **não** armazena o banco da aplicação |

SQLite fica no disco da VM, não na Storage Account. O hostname DNS e URL HTTPS são outputs do ARM. A configuração é uma única VM para demonstração, sem alta disponibilidade ou backup automático.

### 6. Ver logs se o site ainda não abrir

O bootstrap roda na VM e pode continuar após o ARM terminar. Aguarde mais alguns minutos e, se ainda falhar, consulte o log cloud-init remotamente pelo Azure CLI (não precisa liberar SSH):

```text
az vm run-command invoke --resource-group rg-hellfire-demo --name hellfire-vm --command-id RunShellScript --scripts "tail -n 100 /var/log/cloud-init-output.log" --query "value[0].message" --output tsv
```

Confira também se o rótulo DNS foi aceito, se a região/SKU tem quota e se TCP/80 e TCP/443 estão liberados. O Caddy só conclui a emissão TLS quando DNS e HTTP público estão acessíveis.

### 7. Remover tudo e interromper cobranças

Use o nome do **seu** Resource Group; este comando apaga todos os recursos criados dentro dele:

```text
az group delete --name rg-hellfire-demo --yes --no-wait
```

O comando acima remove sua implantação de exemplo; não use `rg-hellfire-mexico` a menos que queira apagar a demo pública deste projeto.

Consulte o [`relatório técnico detalhado em PDF`](docs/relatorio.pdf) ou a [versão editável](docs/relatorio.md) para arquitetura, esquema da API, recursos Azure, CI/CD e evidências.

## CI/CD GitHub Actions

`.github/workflows/cicd.yml` executa testes da API, valida JavaScript/shell/ARM e constrói a imagem em cada push e pull request. Pushes para `main` também fazem deploy: o workflow autentica no Azure por OIDC, chama `az vm run-command` para atualizar o código e reconstruir o container, preserva o SQLite e testa a URL HTTPS. Não há client secret no GitHub.

Para outra instalação, configure as variáveis do repositório `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`, `AZURE_RESOURCE_GROUP`, `AZURE_VM_NAME` e `AZURE_SITE_URL`. A aplicação Entra precisa de uma credencial federada com subject no formato `repo:OWNER@OWNER_ID/REPO@REPO_ID:ref:refs/heads/main` (use os claims exatos emitidos pelo GitHub) e da função `Virtual Machine Contributor` no escopo da VM. O script executado remotamente está em `scripts/deploy_vm.sh`.

## Tecnologias

Python 3.12, Flask, SQLite, Gunicorn, Chocolate Doom 3.1.0, Emscripten/SDL2, Freedoom 0.13, Docker, Caddy, Nix Flake, Azure ARM e Azure CLI. Chocolate Doom está incluído como submódulo GPL-2.0; conteúdo Freedoom sob BSD-3-Clause.
