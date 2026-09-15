import asyncio
import unittest

from event_stream import Session


class SessionBehaviorTests(unittest.TestCase):
    def test_close_is_idempotent_and_waits_for_cleanup(self):
        async def scenario():
            session = Session()
            await session.start()
            await session.close()
            await session.close()
            return session.active, session.cleanup_count

        self.assertEqual(asyncio.run(scenario()), (False, 1))


if __name__ == "__main__":
    unittest.main()
