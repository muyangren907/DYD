from asyncio import CancelledError
from asyncio import run

from src.application import TikTokDownloader
import time

async def main():
    async with TikTokDownloader() as downloader:
        try:
            await downloader.run()
        except (
                KeyboardInterrupt,
                CancelledError,
        ):
            return


if __name__ == "__main__":
    while True:
        run(main())
        break