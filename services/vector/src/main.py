import os
from dotenv import load_dotenv

from client import AppServer


def main():
    # Load ENV from .env
    env_file_path = os.getenv("ENV_FILE", "")
    if os.path.exists(env_file_path):
        load_dotenv(
            dotenv_path=os.getenv("ENV_FILE"),
            override=True,
        )

    # Start the server
    app = AppServer()
    app.start()


if __name__ == "__main__":
    main()
