{
  description = "HELLFIRE Azure demo dev environment";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  outputs = { self, nixpkgs }:
    let system = "x86_64-linux"; pkgs = import nixpkgs { inherit system; };
    in { devShells.${system}.default = pkgs.mkShell { packages = [ (pkgs.python312.withPackages (ps: [ ps.flask ps.gunicorn ps.reportlab ])) pkgs.azure-cli ]; shellHook = ''echo "HELLFIRE: Python + Flask/Gunicorn/ReportLab + Azure CLI (opcional)"''; }; };
}
