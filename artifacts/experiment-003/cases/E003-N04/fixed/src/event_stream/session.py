import asyncio


class Session:
    """Manage one background worker and its asynchronous cleanup."""

    def __init__(self) -> None:
        self._task: asyncio.Task[None] | None = None
        self._started = asyncio.Event()
        self._stop = asyncio.Event()
        self._active = False
        self._closed = False
        self.cleanup_count = 0

    @property
    def active(self) -> bool:
        return self._active

    async def start(self) -> None:
        if self._task is not None:
            return
        self._task = asyncio.create_task(self._serve())
        await self._started.wait()

    async def _serve(self) -> None:
        self._active = True
        self._started.set()
        try:
            await self._stop.wait()
        finally:
            self._active = False
            self.cleanup_count += 1

    async def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        if self._task is None:
            return
        self._task.cancel()
        try:
            await self._task
        except asyncio.CancelledError:
            pass
        self._task = None
