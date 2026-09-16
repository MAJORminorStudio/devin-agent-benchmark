import asyncio
import unittest

from event_stream import Session


class SessionTests(unittest.TestCase):
    def test_close_waits_for_worker_cleanup(self):
        async def scenario():
            session = Session()
            await session.start()
            await session.close()
            return session.active, session.cleanup_count

        self.assertEqual(asyncio.run(scenario()), (False, 1))


if __name__ == "__main__":
    unittest.main()
