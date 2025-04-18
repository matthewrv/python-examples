let
  pkgs = import <nixpkgs> {};
in pkgs.mkShell {
  packages = [
    pkgs.python313
    pkgs.uv
    pkgs.python312Packages.ruff
    pkgs.vscode-extensions.charliermarsh.ruff
  ];
  shellHook = ''
    export VENV_DIR=.venv
    if [ ! -d "$VENV_DIR" ]; then
      python -m venv $VENV_DIR
    fi
    
    source $VENV_DIR/bin/activate

    echo "Python version: $(python --version)"
    echo "Python executable: $(which python)"
    uv sync
  '';
}