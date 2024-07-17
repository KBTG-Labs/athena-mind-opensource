import os

from chainlit.cli import run_chainlit
from dotenv import load_dotenv

from client.server import __file__ as server


def main():
    env_file_path = os.getenv("ENV_FILE", "")
    if os.path.exists(env_file_path):
        load_dotenv(
            dotenv_path=os.getenv("ENV_FILE"),
        )

    run_chainlit(server)

if __name__ == "__main__":
    main()
