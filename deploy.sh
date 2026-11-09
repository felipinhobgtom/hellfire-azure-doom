#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
LOCATION="${AZURE_LOCATION:-brazilsouth}"
RG="${AZURE_RESOURCE_GROUP:-rg-hellfire-demo}"
DEPLOYMENT="hellfire-$(date +%Y%m%d%H%M%S)"
command -v az >/dev/null || { echo 'Azure CLI ausente. Execute: nix develop'; exit 1; }
az account show >/dev/null 2>&1 || { echo 'Faça login com: az login'; exit 1; }
az group create --name "$RG" --location "$LOCATION" --output none
az deployment group create --resource-group "$RG" --name "$DEPLOYMENT" --template-file "$ROOT/infra/main.json" --parameters @"$ROOT/infra/parameters.json" --parameters adminPassword="${AZURE_VM_PASSWORD:?Defina AZURE_VM_PASSWORD (mín. 12 caracteres, maiúscula, minúscula, número e símbolo)}" vmSize="${AZURE_VM_SIZE:-Standard_B1s}" --output table
az deployment group show --resource-group "$RG" --name "$DEPLOYMENT" --query properties.outputs --output json
