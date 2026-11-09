{
  description = "HELLFIRE Azure demo dev environment";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  outputs = { self, nixpkgs }:
    let system = "x86_64-linux"; pkgs = import nixpkgs { inherit system; };
    in { devShells.${system}.default = pkgs.mkShell { packages = with pkgs; [ python312 python312Packages.flask python312Packages.gunicorn azure-cli ]; shellHook = ''echo "HELLFIRE dev shell — python, Flask, Gunicorn e Azure CLI"''; }; };
}
