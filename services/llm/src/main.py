import asyncio
import os

from dotenv import load_dotenv

from client import AppServer


async def main():
    # Load ENV from .env
    env_file_path = os.getenv("ENV_FILE", "")
    if os.path.exists(env_file_path):
        load_dotenv(
            dotenv_path=os.getenv("ENV_FILE"),
            override=True,
        )
    

    # Start the server
    app = AppServer()
    await app.start()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
