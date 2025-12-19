{
  description = "Brainless flake";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = {
    self,
    nixpkgs,
    flake-utils,
  }:
    flake-utils.lib.eachDefaultSystem (
      system: let
        pkgs = nixpkgs.legacyPackages.${system};
        python = pkgs.python313;
        name = "brainless";
      in {
        packages.default = python.pkgs.buildPythonApplication {
          pname = name;
          version = "0.1.0";
          format = "pyproject";

          src = ./.;

          nativeBuildInputs = with pkgs; [python.pkgs.setuptools pkgs.makeWrapper];
          pyprojectBuildInputs = [python.pkgs.setuptools python.pkgs.wheel];
          nativeCheckInputs = [python.pkgs.pytest];
          propagatedBuildInputs = with python.pkgs; [
            colorama
            docker
            pyyaml
            tabulate
            jsonschema
            pydantic
          ];

          # checkPhase = ''
          #   pytest -v
          # '';
        };

        apps.default = flake-utils.lib.mkApp {
          drv = self.packages.${system}.default;
        };

        devShells.default = pkgs.mkShell {
          buildInputs = [
            python
            pkgs.uv
            python.pkgs.pytest
          ];

          name = name;
          shellHook = ''
            export name="${name}"

            if [ -f .venv/bin/activate ]; then
              source .venv/bin/activate
            else
              uv venv
              uv pip install -e .
              uv pip install -e ".[dev]"
            fi

            export PATH="$(pwd)/bin:$PATH"
          '';
        };
      }
    );
}
