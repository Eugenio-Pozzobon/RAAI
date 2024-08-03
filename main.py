import os, sys

from app.src.startup import startup_app


def resolve_path(path):
    resolved_path = os.path.abspath(os.path.join(os.getcwd(), path))
    return resolved_path

def execute_pip_install():
    os.system("pip install -r app/requirements.txt")

if __name__ == "__main__":
    execute_pip_install()
    startup_app()
    import streamlit.web.cli as stcli
    sys.argv = [
        "streamlit",
        "run",
        resolve_path("app/Application.py"),
        "--global.developmentMode=false",
    ]
    sys.exit(stcli.main())

